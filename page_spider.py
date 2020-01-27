import db_manager
from page_pipeline import PagePipeline
from page_crawler import PageCrawler


class PageSpider:
    def __init__(self, site_url, site_id, browser, existing_article_urls, log_file):
        self.site_url = site_url
        self.site_id = site_id
        self.browser = browser
        self.existing_article_urls = existing_article_urls
        self.log_file = log_file

    def work(self):
        pi = PagePipeline([], self.site_id, db_manager)
        pc = PageCrawler(self.site_url, self.browser, self.existing_article_urls, pi.write_post, self.log_file)
        pc.crawl()
