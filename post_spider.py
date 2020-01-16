import db_manager
from post_pipeline import PostPipeline
from post_crawler import PostCrawler

class PostSpider:
    def __init__(self, article_url, article_id, browser):
        self.article_url = article_url
        self.article_id = article_id
        self.browser = browser
    def work(self):
        pi = PostPipeline([], self.article_id, db_manager)
        pc = PostCrawler(self.article_url, self.browser, pi.pipe_single_post_raw_data)
        pc.crawl()