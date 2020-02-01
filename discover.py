import argparse
from tqdm import tqdm
import os
import sys

# self-defined
from page_spider import PageSpider
from logger import Logger
import db_manager
import helper

def log_handler(logfile, description, site, result=None):
    timestamp = None

    if result is not None:
        timestamp = 'handler_timestamp_{}: {}, {}, result is {} \n'.format(helper.now(), description, site, result)
    else:
        timestamp = 'handler_timestamp_{}: {}, {} \n'.format(helper.now(), description, site)

    logfile.write(timestamp)

def discover_all(browser, logfile, site_ids):
    sites = db_manager.get_sites_need_to_crawl_by_ids(site_ids)
    total = len(sites)

    has_error = False
    running_browser = browser
    with tqdm(total=total) as pbar:
        for s in sites:
            logfile.write('\n')

            if has_error:
                log_handler(logfile, '<create a new facebook browser> start', s)
                
                try:
                    running_browser.quit()
                    helper.wait(120)

                    from facebook import Facebook
                    from settings import FB_EMAIL, FB_PASSWORD, CHROMEDRIVER_BIN
                    fb = Facebook(FB_EMAIL, FB_PASSWORD, 'Chrome', CHROMEDRIVER_BIN, True, False)
                    fb.start()
                    running_browser = fb.driver
                    has_error = False
                    log_handler(logfile, '<create a new facebook browser> done', 'SUCCESS')
                except Exception as e:
                    log_handler(logfile, '<create a new facebook browser> failed', helper.print_error(e))
                    break

            log_handler(logfile, 'start crawling site', s)

            try:
                discover_one(s, running_browser, logfile, 6)
                log_handler(logfile, 'complete crawling site', s, 'SUCCESS')
            except Exception as e:
                log_handler(logfile, 'failed crawling site', s, helper.print_error(e))
                has_error = True
            pbar.update(1)

def discover_one(site, browser, logfile, max_try_times):
    site_url = site['url']
    site_id = site['site_id']
    existing_article_urls = db_manager.get_articles_by_site_id(site_id)
    ps = PageSpider(site_url, site_id, browser, existing_article_urls, logfile, max_try_times)
    ps.work()


def test(browser, logfile, max_try_times):
    site = dict()
    site['site_id'] = 66
    site['url'] = 'https://www.facebook.com/jesusSavesF13/'
    discover_one(site, browser, logfile, max_try_times)


def main():
    pid = os.getpid()
    start_at = helper.now()

    fpath = 'discover_pid{}_timestamp{}.log'.format(pid, start_at)
    logfile = Logger(open(fpath, 'a', buffering=1))

    logfile.write('[{}] -------- LAUNCH --------, pid: {}\n'.format(start_at, pid))

    # sys.stdout = logfile
    # sys.stderr = logfile

    from config import fb
    fb.start()
    browser = fb.driver

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--all', action='store_true',
                        help='discover new posts in all fb pages')
    parser.add_argument('-c', '--complete', action='store_true',
                        help='complete search in one site')
    args = parser.parse_args()
    if args.all:
        site_ids = [75, 76, 92, 93, 94, 95, 97, 975]
        discover_all(browser, logfile, site_ids)
    else:
        if args.complete:
            max_try_times = 1000
        else:
            max_try_times = 3
        test(browser, logfile, max_try_times)

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