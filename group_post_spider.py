import db_manager
from group_post_pipeline import GroupPostPipeline
from group_post_crawler import GroupPostCrawler

class GroupPostSpider:
    def __init__(self, article_url, article_id, browser, logfile):
        self.article_url = article_url
        self.article_id = article_id
        self.browser = browser
        self.logfile = logfile
    def work(self):
        pi = GroupPostPipeline([], self.article_id, db_manager, self.logfile)
        pc = GroupPostCrawler(self.article_url, self.browser, pi.pipe_single_post_raw_data, self.logfile)
        pc.crawl()