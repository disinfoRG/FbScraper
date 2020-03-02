from tqdm import tqdm
import argparse
import time
import os
import sys
import pugsql
import multiprocessing
multiprocessing.set_start_method('spawn', True)

# self-defined
from facebook import Facebook
from settings import FB_EMAIL, FB_PASSWORD, CHROMEDRIVER_BIN
from discover_crawler import DiscoverCrawler
from update_crawler import UpdateCrawler
from helper import helper, SelfDefinedError
import config


queries = pugsql.module('queries')
queries.connect(os.getenv('DB_URL'))


class Handler:
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
        if result is not None:
            timestamp = 'handler_timestamp_{}: {}, {}, result is {} \n'.format(helper.now(), description, parameters, result)
        else:
            timestamp = 'handler_timestamp_{}: {}, {} \n'.format(helper.now(), description, parameters)
        logfile.write(timestamp)

    def update_one(self, article, browser, logfile):
        article_id = article['article_id']
        article_url = article['url']
        process = UpdateCrawler(url=article_url, article_id=article_id, browser=browser,
                                queries=queries, logfile=logfile, is_logined=self.is_logined,
                                timeout=config.UPDATE_CRAWLER_TIMEOUT)
        process.crawl_and_save()

    def discover_one(self, site, browser, logfile, is_group_site_type, max_try_times=None):
        site_url = site['url']
        site_id = site['site_id']
        existing_urls = [x['url'] for x in queries.get_article_urls_of_site(site_id=site_id)]
        process = DiscoverCrawler(url=site_url, site_id=site_id, browser=browser, queries=queries,
                                  existing_article_urls=existing_urls,
                                  logfile=logfile, max_try_times=max_try_times,
                                  should_use_original_url=is_group_site_type)
        process.crawl_and_save()

    def process_one(self, item, browser, logfile):
        is_group_site_type = True if self.site_type == config.GROUP_SITE_TYPE else False

        if self.action == config.DISCOVER_ACTION:
            self.discover_one(item, browser, logfile, is_group_site_type)
        elif self.action == config.UPDATE_ACTION:
            self.update_one(item, browser, logfile)

    def process_item(self, item, should_show_progress=True):
        errors = []
        pid = os.getpid()
        start_at = helper.now()

        fpath = '{}-{}_pid_{}_timestamp_{}.log'.format(self.action, self.site_type, pid, start_at)
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
        
        response = dict()
        response['errors'] = errors
        response['is_security_check'] = is_security_check
        response['url'] = item['url']
        return response

    def countdown(self, period, desc=config.ITEM_PROCESS_COUNTDOWN_DESCRIPTION):
        with tqdm(desc=desc, total=period) as pbar:
            for i in range(period):
                helper.wait(1)
                pbar.update(1)

    def handle(self):
        if self.action == config.UPDATE_ACTION:
            items = queries.get_articles_need_to_update(site_id=self.specific_site_id,
                                                        now=int(time.time()),
                                                        amount=self.max_amount_of_items)
        elif self.action == config.DISCOVER_ACTION:
            if self.specific_site_id:  # if given a site id
                items = queries.get_site_by_id(site_id=self.specific_site_id)
                items = [items]
            else:
                items = queries.get_sites_by_type(site_type=self.site_type,
                                                  amount=self.max_amount_of_items)
        else:
            raise Exception('Please specified valid action')

        items = list(items)  # turn generator object into list of dict
        items_len = len(items)
        dummy_items = range(items_len)
        dummy_item_chunks = helper.divide_chunks(dummy_items, self.n_amount_in_a_chunk)

        desc = '{} {}'.format(self.action, self.site_type)
        with tqdm(desc=desc, total=items_len) as pbar:
            for c in range(len(dummy_item_chunks)):
                n_realtime_item = items[c*self.n_amount_in_a_chunk:(c+1)*self.n_amount_in_a_chunk]
                n_item_for_pool = helper.to_tuples(n_realtime_item)

                n_item_result = None
                
                countdown_process = multiprocessing.Process(target=self.countdown, args=(self.timeout,))
                countdown_process.start()

                with multiprocessing.Pool(processes=self.n_amount_in_a_chunk) as pool:
                    note = 'n_item_for_pool={}, self={}'.format(n_item_for_pool, self)
                    pool_result = pool.starmap_async(self.process_item, n_item_for_pool)
                    try:
                        n_item_result = pool_result.get(timeout=self.timeout)
                        print(n_item_result)
                    except multiprocessing.context.TimeoutError as e:
                        helper.print_error(e, note)
                    except Exception as e:
                        helper.print_error(e, note)
                        raise
                        
                try:
                    countdown_process.terminate()
                except Exception as e:
                    helper.print_error(e)
                
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

                pbar.update(self.n_amount_in_a_chunk)

                break_time = helper.random_int(config.DEFAULT_BREAK_BETWEEN_PROCESS) if not self.break_between_process else self.break_between_process
                self.countdown(break_time, desc=config.TAKE_A_BREAK_COUNTDOWN_DESCRIPTION)

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

    is_logined = config.DEFAULT_IS_LOGINED
    is_headless = config.DEFAULT_IS_HEADLESS
    max_amount_of_items = config.DEFAULT_MAX_AMOUNT_OF_ITEMS
    n_amount_in_a_chunk = config.DEFAULT_N_AMOUNT_IN_A_CHUNK
    break_between_process = None
    specific_site_id = None
    max_auto_times = config.DEFAULT_MAX_AUTO_TIMES

    if args.discover:
        action = config.DISCOVER_ACTION
        timeout = config.DISCOVER_TIMEOUT
    elif args.update:
        action = config.UPDATE_ACTION
        timeout = config.UPDATE_TIMEOUT
    else:
        return

    if args.group:
        site_type = config.GROUP_SITE_TYPE
    elif args.page:
        site_type = config.PAGE_SITE_TYPE
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

    main_handler = Handler(action, site_type, is_logined=is_logined, timeout=timeout,
                           is_headless=is_headless, max_amount_of_items=max_amount_of_items,
                           n_amount_in_a_chunk=n_amount_in_a_chunk,
                           break_between_process=break_between_process,
                           specific_site_id=specific_site_id, max_auto_times=max_auto_times)
    main_handler.handle()
    

if __name__ == '__main__':
    main()
