import db_manager
from update_parser import UpdateParser
from update_pipeline import UpdatePipeline
from update_crawler import UpdateCrawler
from config import DEFAULT_IS_LOGINED

class UpdateSpider:
    def __init__(self, article_url, article_id, browser, logfile, timeout, is_logined=DEFAULT_IS_LOGINED):
        self.article_url = article_url
        self.article_id = article_id
        self.browser = browser
        self.logfile = logfile
        self.is_logined = is_logined
        self.timeout = timeout
    def work(self):
        parser = UpdateParser()
        pipeline = UpdatePipeline([], self.article_id, db_manager, self.logfile)
        crawler = UpdateCrawler(self.article_url, self.browser, parser, pipeline, self.logfile, timeout=self.timeout, is_logined=self.is_logined)
        crawler.crawl()