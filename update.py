from tqdm import tqdm
import argparse
import os
import sys
from multiprocessing import Process
from selenium.common.exceptions import NoSuchElementException
import threading

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

def update_all(site_ids, browser, logfile):
    logfile.write('\n')

    for site_id in site_ids:
        log_handler(logfile, 'start snapshoting articles from site', site_id)
        articles = db_manager.get_articles_need_to_update(site_id)

        try:    
            has_error = False
            running_browser = browser
            with tqdm(total=len(articles)) as pbar:
                for article in articles:
                    if has_error:
                        log_handler(logfile, '<create a new facebook browser> start', article)
                        
                        try:
                            running_browser.quit()
                            helper.wait(120)

                            from facebook import Facebook
                            from settings import FB_EMAIL, FB_PASSWORD, CHROMEDRIVER_BIN
                            fb = Facebook(FB_EMAIL, FB_PASSWORD, 'Chrome', CHROMEDRIVER_BIN, True, False)
                            fb.start(False)
                            running_browser = fb.driver
                            has_error = False
                            log_handler(logfile, '<create a new facebook browser> done', 'SUCCESS')
                        except Exception as e:
                            log_handler(logfile, '<create a new facebook browser> failed', helper.print_error(e))
                            break

                    log_handler(logfile, 'start snapshoting article', article)

                    try:
                        update_one(article, browser, logfile)
                        # update_one_process = Process(target=update_one, args=[article, browser, logfile])
                        # update_one_process.start()
                        # update_one_process.join(timeout=10)

                        log_handler(logfile, 'complete snapshoting article', article, 'SUCCESS')

                        # if update_one_process.exitcode is None:
                        #     raise TimeoutError
                    except NoSuchElementException as e:
                        log_handler(logfile, 'failed snapshoting article', article, helper.print_error(e))
                        raise NoSuchElementException
                    except Exception as e:
                        log_handler(logfile, 'failed snapshoting article', article, helper.print_error(e))
                        has_error = True
                    
                    pbar.update(1)
            log_handler(logfile, 'complete snapshoting articles from site id = {}'.format(site_id), articles)
        except Exception as e:
            log_handler(logfile, 'failed snapshoting articles from site id = {}'.format(site_id), articles, helper.print_error(e))
            return
def update_one(article, browser, logfile):
    article_id = article['article_id']
    article_url = article['url']
    ps = PostSpider(article_url, article_id, browser, logfile)
    ps.work()

def test(browser, logfile):
    article = dict()
    article['article_id'] = 14259
    article['url'] = 'https://www.facebook.com/znk168/posts/412649276099554'
    # article['url'] = 'https://www.facebook.com/185537762220181/posts/2426555417632575'
    update_one(article, browser, logfile)

def main():
    pid = os.getpid()
    start_at = helper.now()

    fpath = 'update_pid{}_timestamp{}.log'.format(pid, start_at)
    logfile = Logger(open(fpath, 'a', buffering=1))
    # logfile = open(fpath, 'a', buffering=1)

    logfile.write('[{}] -------- LAUNCH --------, pid: {}\n'.format(start_at, pid))

    # comment and disable redirect of stdout and stderr to original logfile, for displaying on middle2 cronjob's log instead
    # sys.stdout = logfile
    # sys.stderr = logfile

    from config import fb
    fb.start(False)
    browser = fb.driver

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--all', action='store_true',
                        help='update all posts in db')
    args = parser.parse_args()
    if args.all:
        site_ids = [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 59, 60, 61, 62, 63, 64, 65]
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
