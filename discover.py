from page_spider import PageSpider
import db_manager
import helper
from post_spider import PostSpider
import argparse

def discover_all(browser):
    sites = db_manager.get_sites_need_to_crawl()
    for s in sites:
        try:
            discover_one(s, browser)
        except Exception as e:
            helper.print_error(e)

def discover_one(site, browser):
    site_url = site['url']
    site_id = site['site_id']
    existing_article_urls = db_manager.get_articles_by_site_id(site_id)
    ps = PageSpider(site_url, site_id, browser, existing_article_urls)
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
    # from config import fb
    # fb.start()
    # test(fb.driver)
