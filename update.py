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
from post_spider import PostSpider
from logger import Logger
from helper import helper
import db_manager


def log_handler(logfile, description, parameters, result=None):
    timestamp = None

    if result is not None:
        timestamp = 'handler_timestamp_{}: {}, {}, result is {} \n'.format(helper.now(), description, parameters, result)
    else:
        timestamp = 'handler_timestamp_{}: {}, {} \n'.format(helper.now(), description, parameters)

    logfile.write(timestamp)

def update_one(_article, _browser, _logfile):
    article_id = _article['article_id']
    article_url = _article['url']
    ps = PostSpider(article_url, article_id, _browser, _logfile)
    ps.work()

# def update_all(site_ids, browser, logfile):
#         logfile.write('\n')

#         try:
#             running_browser = browser
#             with tqdm(total=len(articles)) as pbar:
#                 for article in articles:
#                     log_handler(logfile, 'start snapshoting article', article)

#                     try:

#                         else:
#                             log_handler(logfile, 'complete snapshoting article', article, 'SUCCESS')
#                     except NoSuchElementException as e:
#                         log_handler(logfile, 'failed snapshoting article', article, helper.print_error(e))
#                         raise
#                     except Exception as e:
#                         log_handler(logfile, 'failed snapshoting article', article, helper.print_error(e))
#                         raise
                    
#                     pbar.update(1)
#             log_handler(logfile, 'complete snapshoting articles from site id = {}'.format(site_id), articles)
#         except Exception as e:
#             log_handler(logfile, 'failed snapshoting articles from site id = {}'.format(site_id), articles, helper.print_error(e))
#             return

def test(browser, logfile):
    article = dict()
    article['article_id'] = 14259
    article['url'] = 'https://www.facebook.com/znk168/posts/412649276099554'
    # article['url'] = 'https://www.facebook.com/185537762220181/posts/2426555417632575'
    update_one(article, browser, logfile)
    with multiprocessing.Pool() as pool:
        pool_result = pool.starmap_async(update_one, product_names, 3)

def update_one_by_parallel(article, should_show_progress=True):
    pid = os.getpid()
    start_at = helper.now()

    fpath = 'update_articleId{}_timestamp{}.log'.format(article['article_id'], start_at)
    print(fpath)
    print(article)
    logfile = open(fpath, 'a', buffering=1)
    sys.stdout = logfile
    if not should_show_progress:
        sys.stderr = logfile
    logfile.write('[{}] -------- LAUNCH --------, article: {} \n'.format(start_at, pid, article))

    from config import fb
    fb.start(False)
    browser = fb.driver

    try:
        update_one(article, browser, logfile)
    except Exception as e:
        note = 'file_path = {}, article = {}'.format(fpath, article)
        logfile.write('[{}] Failed to update article, {} \n'.format(helper.now(), helper.print_error(e, note)))
    
    try:
        browser.quit()
        logfile.write('[{}] Quit Browser, result is SUCCESS \n'.format(helper.now()))
    except Exception as e:
        logfile.write('[{}] Failed to Quit Browser, {} \n'.format(helper.now(), helper.print_error(e, browser.current_url)))

    end_at = helper.now()
    spent = end_at - start_at
    logfile.write('[{}] -------- FINISH --------, spent: {}, article: {} \n'.format(end_at, spent, article))
    
    logfile.close()

def countdown(period):
    with tqdm(desc='Snapshot Process Countdown', total=period) as pbar:
        for i in range(period):
            helper.wait(1)
            pbar.update(1)

def update_one_dummy(article):
    print(article)

def main():
    n_amount_in_a_chunk = 4
    timeout = 60
    articles = db_manager.get_articles_never_update()

    random.shuffle(articles)
    article_tuples = helper.to_tuples(articles)
    article_chunks = helper.divide_chunks(article_tuples, n_amount_in_a_chunk)# [(articles[0],), (articles[1],)]
     
    # for article in articles:
    #     update_one_by_parallel(article)
    
    with tqdm(desc='Update Article', total=len(articles)) as pbar:
        for n_article in article_chunks:
            countdown_process = multiprocessing.Process(target=countdown,args=(timeout,))
            countdown_process.start()

            with multiprocessing.Pool(processes=n_amount_in_a_chunk) as pool:
                pool_result = pool.starmap_async(update_one_by_parallel, n_article)
                try:
                    res = pool_result.get(timeout=timeout)
                    print(res)
                except Exception as e:
                    helper.print_error(e)
            try:
                countdown_process.terminate()
            except Exception as e:
                helper.print_error(e)

            pbar.update(n_amount_in_a_chunk)

def _main():
    pid = os.getpid()
    start_at = helper.now()

    fpath = 'update_pid{}_timestamp{}.log'.format(pid, start_at)
    # logfile = Logger(open(fpath, 'a', buffering=1))
    logfile = open(fpath, 'a', buffering=1)

    logfile.write('[{}] -------- LAUNCH --------, pid: {}\n'.format(start_at, pid))

    # comment and disable redirect of stdout and stderr to original logfile, for displaying on middle2 cronjob's log instead
    sys.stdout = logfile
    sys.stderr = logfile

    from config import fb
    fb.start(False)
    browser = fb.driver

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--all', action='store_true',
                        help='update all posts in db')
    args = parser.parse_args()
    if args.all:
        # site_ids = [18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 79, 80, 87, 88, 89, 90, 91, 92, 93, 94, 95, 97, 975]
        site_ids = [95, 69]
        random.shuffle(site_ids)
        # site_ids = [80, 87, 88, 89] bruceisawesomeandcool@gmail.com
        # site_ids = [975]

        update_all(site_ids, browser, logfile)
    else:
        test(browser, logfile)

    try:
        browser.quit()
        logfile.write('[{}] Quit Browser, result is SUCCESS \n'.format(helper.now()))
    except Exception as e:
        logfile.write('[{}] Failed to Quit Browser, {} \n'.format(helper.now(), helper.print_error(e)))

    end_at = helper.now()
    spent = end_at - start_at
    logfile.write('[{}] -------- FINISH --------, spent: {}\n'.format(end_at, spent))
    
    logfile.close()

if __name__ == '__main__':
    main()
