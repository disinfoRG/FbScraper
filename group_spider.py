import db_manager
from group_pipeline import GroupPipeline
from group_crawler import GroupCrawler


class GroupSpider:
    def __init__(self, site_url, site_id, browser, existing_article_urls, logfile, max_try_times):
        self.site_url = site_url
        self.site_id = site_id
        self.browser = browser
        self.existing_article_urls = existing_article_urls
        self.logfile = logfile
        self.max_try_times = max_try_times

    def work(self):
        gi = GroupPipeline([], self.site_id, db_manager, self.logfile)
        gc = GroupCrawler(self.site_url, self.browser, self.existing_article_urls, gi.write_post, self.logfile, self.max_try_times)
        gc.crawl()
