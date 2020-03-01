from tqdm import tqdm
import argparse
import os
import sys
import multiprocessing
multiprocessing.set_start_method('spawn', True)
from selenium.common.exceptions import NoSuchElementException
import threading
import random

# self-defined
from facebook import Facebook
from settings import FB_EMAIL, FB_PASSWORD, CHROMEDRIVER_BIN
from update_spider import UpdateSpider
from discover_spider import DiscoverSpider
from logger import Logger
from helper import helper, SelfDefinedError
import db_manager
from config import \
    DISCOVER_ACTION, \
    UPDATE_ACTION, \
    GROUP_SITE_TYPE, \
    PAGE_SITE_TYPE, \
    DISCOVER_TIMEOUT, \
    UPDATE_TIMEOUT, \
    DEFAULT_IS_LOGINED, \
    DEFAULT_IS_HEADLESS, \
    DEFAULT_MAX_AMOUNT_OF_ITEMS, \
    DEFAULT_N_AMOUNT_IN_A_CHUNK, \
    ITEM_PROCESS_COUNTDOWN_DESCRIPTION, \
    TAKE_A_BREAK_COUNTDOWN_DESCRIPTION, \
    DEFAULT_BREAK_BETWEEN_PROCESS, \
    DEFAULT_MAX_AUTO_TIMES
class Handler(object):
    def __init__(self, action, site_type, is_logined, timeout, is_headless, max_amount_of_items, n_amount_in_a_chunk, break_between_process, specific_site_id, max_auto_times):
        self.action = action
        self.site_type = site_type
        self.is_logined = is_logined
        self.timeout = timeout
        self.is_headless = is_headless
        self.max_amount_of_items = max_amount_of_items
        self.n_amount_in_a_chunk = n_amount_in_a_chunk
        self.break_between_process = break_between_process
        self.specific_site_id = specific_site_id
        self.max_auto_times = max_auto_times

    def log_handler(self, logfile, description, parameters, result=None):
        timestamp = None
        if result is not None:
            timestamp = 'handler_timestamp_{}: {}, {}, result is {} \n'.format(helper.now(), description, parameters, result)
        else:
            timestamp = 'handler_timestamp_{}: {}, {} \n'.format(helper.now(), description, parameters)
        logfile.write(timestamp)

    def update_one(self, article, browser, logfile, is_group_site_type):
        article_id = article['article_id']
        # article_url = article['url']
        article_url = 'https://google.com'
        spider = UpdateSpider(article_url, article_id, browser, logfile, is_logined=self.is_logined)
        spider.work()

    def discover_one(self, site, browser, logfile, is_group_site_type, max_try_times=None):
        site_url = site['url']
        site_id = site['site_id']
        existing_article_urls = db_manager.get_articles_by_site_id(site_id)
        should_use_original_url = is_group_site_type
        spider = DiscoverSpider(site_url, site_id, browser, existing_article_urls, logfile, max_try_times, should_use_original_url)
        spider.work()

    def process_one(self, item, browser, logfile):
        is_group_site_type = True if self.site_type == GROUP_SITE_TYPE else False

        if self.action == DISCOVER_ACTION:
            self.discover_one(item, browser, logfile, is_group_site_type)
        elif self.action == UPDATE_ACTION:
            self.update_one(item, browser, logfile, is_group_site_type)

    def process_item(self, item, should_show_progress=True):
        errors = []
        pid = os.getpid()
        start_at = helper.now()

        fpath = '{}-{}_pid_{}_timestamp_{}.log'.format(self.action, self.site_type, pid, start_at)
        print(fpath)
        print(item)
        logfile = open(fpath, 'a', buffering=1)
        sys.stdout = logfile
        if not should_show_progress:
            sys.stderr = logfile
        logfile.write('[{}][process_item] -------- LAUNCH --------, {}-{} for item: {} \n'.format(start_at, self.action, self.site_type, item))

        fb = Facebook(FB_EMAIL, FB_PASSWORD, 'Chrome', CHROMEDRIVER_BIN, self.is_headless)
        fb.start(self.is_logined)
        browser = fb.driver

        error_note = 'file_path = {}, item = {}'.format(fpath, item)
        is_security_check = False
        try:
            self.process_one(item, browser, logfile)
        except SelfDefinedError as e:
            # encountered security check for robot or login
            is_security_check = True
            error_msg = '[{}][process_item] Encountered security check and failed to {}-{} for item, error: {} \n'.format(helper.now(), self.action, self.site_type, helper.print_error(e, error_note))
            errors.append(error_msg)
            logfile.write(error_msg)
        except Exception as e:
            error_msg = '[{}][process_item] Failed to {}-{} for item, error: {} \n'.format(helper.now(), self.action, self.site_type, helper.print_error(e, error_note))
            errors.append(error_msg)
            logfile.write(error_msg)
        
        try:
            browser.quit()
            logfile.write('[{}][process_item] Quit Browser, result is SUCCESS \n'.format(helper.now()))
        except Exception as e:
            error_msg = '[{}][process_item] Failed to Quit Browser, {} \n'.format(helper.now(), helper.print_error(e, browser.current_url))
            errors.append(error_msg)
            logfile.write(error_msg)

        end_at = helper.now()
        spent = end_at - start_at
        logfile.write('[{}][process_item] -------- FINISH --------, spent: {}, {}-{} for item: {} \n'.format(end_at, spent, self.action, self.site_type, item))
        logfile.close()
        
        response = {}
        response['errors'] = errors
        response['is_security_check'] = is_security_check
        response['url'] = item['url']
        return response

    def countdown(self, period, desc=ITEM_PROCESS_COUNTDOWN_DESCRIPTION):
        with tqdm(desc=desc, total=period) as pbar:
            for i in range(period):
                helper.wait(1)
                pbar.update(1)

    def handle(self):
        items = []
        get_items = None
        if self.action == UPDATE_ACTION:
            get_items = db_manager.get_articles_need_to_update
        elif self.action == DISCOVER_ACTION:
            get_items = db_manager.get_sites_need_to_discover
        
        items = get_items(site_type=self.site_type, site_id=self.specific_site_id,amount=self.max_amount_of_items)
        items_len = len(items)
        dummy_items = range(items_len)
        dummy_item_chunks = helper.divide_chunks(dummy_items, self.n_amount_in_a_chunk)

        desc = '{} {}'.format(self.action, self.site_type)
        with tqdm(desc=desc, total=items_len) as pbar:
            stop_at_count = 100
            current_count = 0
            for _ in dummy_item_chunks:
                if current_count == stop_at_count:
                    helper.wait(1000000)
                current_count += 1 
                n_realtime_item = get_items(site_type=self.site_type, site_id=self.specific_site_id, amount=self.n_amount_in_a_chunk)
                n_item_for_pool = helper.to_tuples(n_realtime_item)

                n_item_result = None
                
                pool_countdown_process = multiprocessing.Process(target=self.countdown,args=(self.timeout,))

                # maxtasksperchild=1 by https://stackoverflow.com/a/54975030
                pool = multiprocessing.Pool(processes=self.n_amount_in_a_chunk, maxtasksperchild=1)
                note = 'n_item_for_pool={}, self={}'.format(n_item_for_pool, self)
                pool_result = pool.starmap_async(self.process_item, n_item_for_pool)
                pool_countdown_process.start()

                try:
                    n_item_result = pool_result.get(timeout=self.timeout)
                    print(n_item_result)
                except multiprocessing.context.TimeoutError as e:
                    pass
                except Exception as e:
                    helper.print_error(e, note)
                
                pool.close()
                pool.join()
                pool_countdown_process.terminate()
                pool_countdown_process.join()        

                while True:
                    act = multiprocessing.active_children()
                    if len(act)==0:
                        break
                    print("----------- Waiting for %d workers to finish ----------- "%len(act))
                    helper.wait(1)

                print('-------- Kill Zombie Processes --------')
                helper.kill_zombie()

                print('---------------------------------------------------------------- cleaned up unused memory')

                try:
                    # check if facebook block
                    for a_item_result in n_item_result:
                        is_failed = False

                        if a_item_result['is_security_check']:
                            is_failed = True
                            msg = '[{}][handle] Encountered security check in details: {}. \n'.format(helper.now(), a_item_result)
                            print(msg)

                        if len(a_item_result['errors']) > 0:
                            msg = '[{}][handle] Encountered errors in details: {}. \n'.format(helper.now(), a_item_result)
                            print(msg)

                        if is_failed:
                            if self.max_auto_times > 0:
                                self.max_auto_times -= 1
                                self.is_logined = not self.is_logined                            
                            else:
                                return
                # for multiprocessing.context.TimeoutError cause 'NoneType' object is not iterable
                except TypeError as e:
                    pass
                except Exception as e:
                    helper.print_error(e)

                pbar.update(self.n_amount_in_a_chunk)

                break_time = helper.random_int(DEFAULT_BREAK_BETWEEN_PROCESS) if self.break_between_process is None else self.break_between_process
                self.countdown(break_time, desc=TAKE_A_BREAK_COUNTDOWN_DESCRIPTION)

def main():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('-d', '--discover', action='store_true', help='save article urls for sites')
    argument_parser.add_argument('-u', '--update', action='store_true', help='save html for articles')    
    argument_parser.add_argument('-g', '--group', action='store_true', help='facebook group')
    argument_parser.add_argument('-p', '--page', action='store_true', help='facebook page')    
    argument_parser.add_argument('-l', '--login', action='store_true', help='apply facebook login, default is without login')
    argument_parser.add_argument('-t', '--timeout', action='store', help='timeout for a site discover or an article update')    
    argument_parser.add_argument('-nh', '--non-headless', action='store_true', help='browser in non-headless mode, default is headless')
    argument_parser.add_argument('-m', '--max', action='store', help='max amount of sites(by discover) or articles(by update) want to be accomplished, default is 2')
    argument_parser.add_argument('-c', '--cpu', action='store', help='how many cpu processes run at the same time, default is 2')
    argument_parser.add_argument('-b', '--between', action='store', help='time break before continueing next site discover or article update')
    argument_parser.add_argument('-n', '--note', action='store', help='additional note to be viewed on CLI')
    argument_parser.add_argument('-s', '--site', action='store', help='discover and update sites or articles from specific site id')
    argument_parser.add_argument('-a', '--auto', action='store', help='max times of automatically switch between login and without-login for any error, default auto-switch max times is 0')
    args = argument_parser.parse_args()

    action = None
    site_type = None
    is_logined = DEFAULT_IS_LOGINED    
    timeout = None
    is_headless = DEFAULT_IS_HEADLESS
    max_amount_of_items = DEFAULT_MAX_AMOUNT_OF_ITEMS
    n_amount_in_a_chunk = DEFAULT_N_AMOUNT_IN_A_CHUNK
    break_between_process = None
    specific_site_id = None
    max_auto_times = DEFAULT_MAX_AUTO_TIMES

    if args.discover:
        action = DISCOVER_ACTION
        timeout = DISCOVER_TIMEOUT
    elif args.update:
        action = UPDATE_ACTION
        timeout = UPDATE_TIMEOUT
    else:
        return

    if args.group:
        site_type = GROUP_SITE_TYPE
    elif args.page:
        site_type = PAGE_SITE_TYPE
    else:
        return

    if args.login:
        is_logined = True

    if args.timeout:
        try:
            timeout = int(args.timeout)
        except Exception as e:
            helper.print_error(e)
            raise

    if args.non_headless:
        is_headless = False

    if args.max:
        try:
            max_amount_of_items = int(args.max)
        except Exception as e:
            helper.print_error(e)
            raise
    
    if args.cpu:
        try:
            n_amount_in_a_chunk = int(args.cpu)
        except Exception as e:
            helper.print_error(e)
            raise 

    if args.between:
        try:
            break_between_process = int(args.between)
        except Exception as e:
            helper.print_error(e)
            raise

    if args.site:
        try:
            specific_site_id = int(args.site)
        except Exception as e:
            helper.print_error(e)
            raise

    if args.auto:
        try:
            max_auto_times = int(args.auto)
        except Exception as e:
            helper.print_error(e)
            raise

    main_handler = Handler(action, site_type, is_logined=is_logined, timeout=timeout, is_headless=is_headless, max_amount_of_items=max_amount_of_items, n_amount_in_a_chunk=n_amount_in_a_chunk, break_between_process=break_between_process, specific_site_id=specific_site_id, max_auto_times=max_auto_times)
    main_handler.handle()
    

if __name__ == '__main__':
    main()
