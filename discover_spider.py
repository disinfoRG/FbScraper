import db_manager
from discover_pipeline import DiscoverPipeline
from discover_crawler import DiscoverCrawler
from discover_parser import DiscoverParser


class DiscoverSpider:
    def __init__(self, site_url, site_id, browser, existing_article_urls, logfile, max_try_times, should_use_original_url=False):
        self.site_url = site_url
        self.site_id = site_id
        self.browser = browser
        self.existing_article_urls = existing_article_urls
        self.logfile = logfile
        self.max_try_times = max_try_times
        self.should_use_original_url = should_use_original_url

    def work(self):
        parser = DiscoverParser()
        pipeline = DiscoverPipeline([], self.site_id, db_manager, self.logfile)
        crawler = DiscoverCrawler(self.site_url, self.browser, self.existing_article_urls, parser, pipeline, self.logfile, self.max_try_times, self.should_use_original_url)
        crawler.crawl()
