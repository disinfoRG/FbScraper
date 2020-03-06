import logging
import os
logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=os.getenv("LOG_LEVEL", "INFO"),
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("fb_handler.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

import argparse
import pugsql
import multiprocessing
multiprocessing.set_start_method('spawn', True)

# self-defined
import facebook as fb
from settings import FB_EMAIL, FB_PASSWORD, CHROMEDRIVER_BIN
from fbscraper.actions.update.update_spider import UpdateSpider
from fbscraper.actions.discover.discover_spider import DiscoverSpider
from helper import helper, SelfDefinedError
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
    DEFAULT_BREAK_BETWEEN_PROCESS, \
    DEFAULT_MAX_AUTO_TIMES, \
    DEFAULT_CPU, \
    DEFAULT_TIMEOUT_RATIO

db = pugsql.module('queries')
db.connect(os.getenv('DB_URL'))


class Handler:
    def __init__(self, action, site_type, is_logined, timeout, is_headless, max_amount_of_items, n_amount_in_a_chunk, break_between_process, specific_site_id, max_auto_times, cpu):
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
        self.cpu = cpu

    def update_one(self, article, browser, is_group_site_type, timeout):
        article_id = article['article_id']
        article_url = article['url']
        spider = UpdateSpider(article_url=article_url,
                                db=db,
                                article_id=article_id,
                                browser=browser,
                                timeout=timeout,
                                is_logined=self.is_logined)
        spider.work()

    def discover_one(self, site, browser, is_group_site_type, timeout, max_try_times=None):
        site_url = site['url']
        site_id = site['site_id']
        existing_article_urls = [x['url'] for x in db.get_article_urls_of_site(site_id=site_id)]
        should_use_original_url = is_group_site_type
        spider = DiscoverSpider(site_url=site_url,
                                db=db,
                                site_id=site_id,
                                browser=browser,
                                existing_article_urls=existing_article_urls,
                                max_try_times=max_try_times,
                                timeout=timeout,
                                should_use_original_url=should_use_original_url)
        spider.work()

    def process_one(self, item, browser, timeout):
        is_group_site_type = True if self.site_type == GROUP_SITE_TYPE else False

        if self.action == DISCOVER_ACTION:
            self.discover_one(item, browser, is_group_site_type, timeout)
        elif self.action == UPDATE_ACTION:
            self.update_one(item, browser, is_group_site_type, timeout)

    def process_item(self, item):
        break_time = helper.random_int(max=self.break_between_process)
        self.pause_escape_security_check(break_time)

        errors = []
        pid = os.getpid()
        start_at = helper.now()

        logger.debug(f'[{start_at}][process_item][pid={pid}] -------- LAUNCH --------, {self.action}-{self.site_type} for item: {item} \n')

        # fb = Facebook(FB_EMAIL, FB_PASSWORD, 'Chrome', CHROMEDRIVER_BIN, )
        browser = None
        try:
            browser = fb.create_driver_without_session(browser_type='Chrome', 
                                                    executable_path=CHROMEDRIVER_BIN, 
                                                    is_headless=self.is_headless)
            if self.is_logined:
                fb.login_with_account(driver=browser, 
                                        email=FB_EMAIL, 
                                        password=FB_PASSWORD)
        except:
            if browser:
                browser.close()
                browser.quit()

        max_timeout = self.timeout*(1 + DEFAULT_TIMEOUT_RATIO)
        min_timeout = self.timeout*(1 - DEFAULT_TIMEOUT_RATIO)
        timeout = helper.random_int(max=max_timeout, min=min_timeout)

        error_note = 'item = {}'.format(item)
        is_security_check = False
        try:
            self.process_one(item=item,
                                browser=browser,
                                timeout=timeout)
        except SelfDefinedError as e:
            # encountered security check for robot or login
            is_security_check = True
            error_msg = '[{}][process_item][pid={}] Encountered security check and failed to {}-{} for item, error: {} \n'.format(helper.now(), pid, self.action, self.site_type, helper.print_error(e, error_note))
            errors.append(error_msg)
            logger.debug(error_msg)
        except Exception as e:
            error_msg = '[{}][process_item][pid={}] Failed to {}-{} for item, error: {} \n'.format(helper.now(), pid, self.action, self.site_type, helper.print_error(e, error_note))
            errors.append(error_msg)
            logger.debug(error_msg)

        try:
            browser.close()
            browser.quit()
            logger.debug('[{}][process_item][pid={}] Quit Browser, result is SUCCESS \n'.format(helper.now(), pid))
        except Exception as e:
            error_msg = '[{}][process_item][pid={}] Failed to Quit Browser, {} \n'.format(helper.now(), pid, helper.print_error(e, browser.current_url))
            errors.append(error_msg)
            logger.debug(error_msg)

        response = dict()
        response['errors'] = errors
        response['is_security_check'] = is_security_check
        response['item'] = item

        end_at = helper.now()
        spent = end_at - start_at
        logger.debug(f'[{end_at}][process_item][pid={pid}] -------- FINISH --------, spent: {spent}, {self.action}-{self.site_type} for item: {item} \n')

        self.pause_escape_security_check(self.break_between_process - break_time)

        return response

    def pause_escape_security_check(self, break_time):
        logger.debug(f'[{helper.now()}][fb_handler - pause_escape_security_check] start to sleep for {break_time} seconds before next process_item')
        for i in range(break_time):
            helper.wait(1)
        logger.debug(f'[{helper.now()}][fb_handler - pause_escape_security_check] sleep is done')

    def handle(self):
        items = []

        if self.action == UPDATE_ACTION:
            if self.specific_site_id:  # if given a site id
                items = db.get_articles_outdated_by_site_id(site_id=self.specific_site_id,
                                                    now=helper.now(),
                                                    amount=self.max_amount_of_items)
            else:
                items = db.get_articles_outdated(now=helper.now(), amount=self.max_amount_of_items)
        elif self.action == DISCOVER_ACTION:
            if self.specific_site_id:  # if given a site id
                site = db.get_site_by_id(site_id=self.specific_site_id)
                items = [site]
            else:
                items = db.get_sites_by_type(site_type=self.site_type, amount=self.max_amount_of_items)

        chunks = helper.divide_chunks(items, self.n_amount_in_a_chunk)

        for chunk_index, n_item in enumerate(chunks):
            n_item_for_pool = helper.to_tuples(n_item)
            desc = f'{self.action} {self.site_type} for {len(n_item_for_pool)} items of chunk #{chunk_index}'
            logger.info('------------------------------------ [{}] start {}'.format(helper.now(), desc))

            # maxtasksperchild=1 by https://stackoverflow.com/a/54975030
            pool = None
            note = 'self={}'.format(self)
            try:
                pool = multiprocessing.Pool(processes=self.cpu, maxtasksperchild=1)
                pool_result = pool.starmap_async(self.process_item, n_item_for_pool)
            except Exception as e:
                logger.error(helper.print_error(e, note))
                raise

            logger.debug('---------------------------------------------------------------- wait for processes to finish and close')
            pool.close()
            pool.join()
            while True:
                act = multiprocessing.active_children()
                if len(act)==0:
                    break
                logger.debug("----------- Waiting for %d workers to finish ----------- "%len(act))
                helper.wait(1)
            logger.debug('---------------------------------------------------------------- all processes are closed')

            logger.debug('---------------------------------------------------------------- get processes result')
            n_item_result = pool_result.get()
            logger.debug(n_item_result)
            try:
                # check if facebook block
                for a_item_result in n_item_result:
                    is_failed = False

                    if a_item_result['is_security_check']:
                        is_failed = True
                        msg = '[{}][handle] Encountered security check in details: {}. \n'.format(helper.now(), a_item_result)
                        logger.debug(msg)

                    if len(a_item_result['errors']) > 0:
                        msg = '[{}][handle] Encountered errors in details: {}. \n'.format(helper.now(), a_item_result)
                        logger.debug(msg)

                    if is_failed:
                        if self.max_auto_times > 0:
                            self.max_auto_times -= 1
                            self.is_logined = not self.is_logined
                        else:
                            return
            except Exception as e:
                logger.error(helper.print_error(e))
                raise

            logger.info('------------------------------------ [{}] end {}'.format(helper.now(), desc))

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
    argument_parser.add_argument('-cs', '--chunk-size', action='store', help='how many site discover or article update assigned to a pool at a time, default is 10')
    args = argument_parser.parse_args()

    action = None
    site_type = None
    is_logined = DEFAULT_IS_LOGINED
    timeout = None
    is_headless = DEFAULT_IS_HEADLESS
    max_amount_of_items = DEFAULT_MAX_AMOUNT_OF_ITEMS
    cpu = DEFAULT_CPU
    break_between_process = DEFAULT_BREAK_BETWEEN_PROCESS
    specific_site_id = None
    max_auto_times = DEFAULT_MAX_AUTO_TIMES
    n_amount_in_a_chunk = DEFAULT_N_AMOUNT_IN_A_CHUNK

    if args.discover:
        action = DISCOVER_ACTION
        timeout = DISCOVER_TIMEOUT
    elif args.update:
        action = UPDATE_ACTION
        timeout = UPDATE_TIMEOUT
    else:
        raise Exception('Please specified valid action')

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
            logger.error(helper.print_error(e))
            raise

    if args.non_headless:
        is_headless = False

    if args.max:
        try:
            max_amount_of_items = int(args.max)
        except Exception as e:
            logger.error(helper.print_error(e))
            raise

    if args.cpu:
        try:
            cpu = int(args.cpu)
        except Exception as e:
            logger.error(helper.print_error(e))
            raise

    if args.between:
        try:
            break_between_process = int(args.between)
        except Exception as e:
            logger.error(helper.print_error(e))
            raise

    if args.site:
        try:
            specific_site_id = int(args.site)
        except Exception as e:
            logger.error(helper.print_error(e))
            raise

    if args.auto:
        try:
            max_auto_times = int(args.auto)
        except Exception as e:
            logger.error(helper.print_error(e))
            raise

    if args.chunk_size:
        try:
            n_amount_in_a_chunk = int(args.chunk_size)
        except Exception as e:
            logger.error(helper.print_error(e))
            raise

    main_handler = Handler(action, site_type, is_logined=is_logined, timeout=timeout, is_headless=is_headless, max_amount_of_items=max_amount_of_items, n_amount_in_a_chunk=n_amount_in_a_chunk, break_between_process=break_between_process, specific_site_id=specific_site_id, max_auto_times=max_auto_times, cpu=cpu)
    main_handler.handle()


if __name__ == '__main__':
    main()
