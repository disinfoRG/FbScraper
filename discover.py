import argparse
from tqdm import tqdm
import os
import sys

# self-defined
from page_spider import PageSpider
import db_manager
import helper

def discover_all(browser):
    # browser.quit()
    
    pid = os.getpid()
    fpath = 'discover_pid{}_timestamp{}.log'.format(pid, helper.now())
    sites = db_manager.get_sites_need_to_crawl()
    total = len(sites)

    with open(fpath, 'a', buffering=1) as f:
        sys.stdout = f
        sys.stderr = f
        
        with tqdm(total=total, file=f) as pbar:
            for s in sites:
                try:
                    discover_one(s, browser, f)
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

if __name__ == '__main__':
    main()