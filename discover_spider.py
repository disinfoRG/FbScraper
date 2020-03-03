from discover_pipeline import DiscoverPipeline
from discover_crawler import DiscoverCrawler
from discover_parser import DiscoverParser

class DiscoverSpider:
    def __init__(self, site_url, db, site_id, browser, existing_article_urls, logfile, max_try_times, timeout, should_use_original_url=False):
        self.site_url = site_url
        self.db = db
        self.site_id = site_id
        self.browser = browser
        self.existing_article_urls = existing_article_urls
        self.logfile = logfile
        self.max_try_times = max_try_times
        self.timeout = timeout
        self.should_use_original_url = should_use_original_url

    def work(self):
        parser = DiscoverParser()
        pipeline = DiscoverPipeline(site_id=self.site_id, db=self.db, logfile=self.logfile)
        crawler = DiscoverCrawler(site_url=self.site_url, 
                                    browser=self.browser, 
                                    existing_article_urls=self.existing_article_urls, 
                                    parser=parser, 
                                    pipeline=pipeline, 
                                    logfile=self.logfile, 
                                    timeout=self.timeout, 
                                    max_try_times=self.max_try_times, 
                                    should_use_original_url=self.should_use_original_url)
        crawler.crawl()
