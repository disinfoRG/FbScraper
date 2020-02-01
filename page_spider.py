import db_manager
from page_pipeline import PagePipeline
from page_crawler import PageCrawler


class PageSpider:
    def __init__(self, site_url, site_id, browser, existing_article_urls, logfile, max_try_times):
        self.site_url = site_url
        self.site_id = site_id
        self.browser = browser
        self.existing_article_urls = existing_article_urls
        self.logfile = logfile
        self.max_try_times = max_try_times

    def work(self):
        pi = PagePipeline([], self.site_id, db_manager, self.logfile)
        pc = PageCrawler(self.site_url, self.browser, self.existing_article_urls, pi.write_post, self.logfile, self.max_try_times)
        pc.crawl()
