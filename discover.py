import argparse
from tqdm import tqdm
import os
import sys

# self-defined
from page_spider import PageSpider
import db_manager
import helper

def discover_all(browser, logfile):
    sites = db_manager.get_sites_need_to_crawl()
    total = len(sites)

    with tqdm(total=total, file=logfile) as pbar:
        for s in sites:
            try:
                discover_one(s, browser, logfile)
            except Exception as e:
                helper.print_error(e)

            timestamp = 'handler_timestamp_{}'.format(helper.now())
            pbar.set_description(timestamp)
            pbar.update(1)

    browser.quit()

def discover_one(site, browser, log_file):
    site_url = site['url']
    site_id = site['site_id']
    existing_article_urls = db_manager.get_articles_by_site_id(site_id)
    ps = PageSpider(site_url, site_id, browser, existing_article_urls, log_file)
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
    logfile = open(fpath, 'a', buffering=1)

    logfile.write('[{}] -------- LAUNCH --------, pid: {}\n'.format(start_at, pid))

    sys.stdout = logfile
    sys.stderr = logfile

    from config import fb
    fb.start()
    browser = fb.driver

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--all', action='store_true',
                        help='discover new posts in site')
    args = parser.parse_args()
    if args.all:
        discover_all(browser)
    else:
        test(browser)

    end_at = helper.now()
    spent = end_at - start_at
    logfile.write('[{}] -------- FINISH --------, spent: {}\n'.format(end_at, spent))

    logfile.close()

if __name__ == '__main__':
    main()