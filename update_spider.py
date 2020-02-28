import db_manager
from post_pipeline import PostPipeline
from post_crawler import PostCrawler
from config import DEFAULT_IS_LOGINED

class PostSpider:
    def __init__(self, article_url, article_id, browser, logfile, is_logined=DEFAULT_IS_LOGINED):
        self.article_url = article_url
        self.article_id = article_id
        self.browser = browser
        self.logfile = logfile
        self.is_logined = is_logined
    def work(self):
        pi = PostPipeline([], self.article_id, db_manager, self.logfile)
        pc = PostCrawler(self.article_url, self.browser, pi.pipe_single_post_raw_data, self.logfile, is_logined=self.is_logined)
        pc.crawl()