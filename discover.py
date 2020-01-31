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

def discover_all(site_ids, browser, logfile):
    sites = db_manager.get_sites_need_to_crawl_by_ids(site_ids)
    total = len(sites)

    with tqdm(total=total) as pbar:
        for s in sites:
            logfile.write('\n')
            log_handler(logfile, 'start crawling site', s)
            try:
                discover_one(s, browser, logfile)
                log_handler(logfile, 'complete crawling site', s, 'SUCCESS')
            except Exception as e:
                log_handler(logfile, 'failed crawling site', s, helper.print_error(e))
            pbar.update(1)

def discover_one(site, browser, logfile):
    site_url = site['url']
    site_id = site['site_id']
    existing_article_urls = db_manager.get_articles_by_site_id(site_id)
    ps = PageSpider(site_url, site_id, browser, existing_article_urls, logfile)
    ps.work()

def test(browser):
    site = dict()
    site['site_id'] = 94
    site['url'] = 'https://www.facebook.com/znk168/'
    discover_one(site, browser)

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
                        help='discover new posts in site')
    args = parser.parse_args()
    if args.all:
        site_ids = [70, 71, 72, 73, 74, 75, 76]
        discover_all(site_ids, browser, logfile)
    else:
        test(browser)

    browser.quit()
    logfile.write('[{}] Quit Browser \n'.format(helper.now()))

    end_at = helper.now()
    spent = end_at - start_at
    logfile.write('[{}] -------- FINISH --------, spent: {}\n'.format(end_at, spent))
    
    logfile.close()

if __name__ == '__main__':
    main()