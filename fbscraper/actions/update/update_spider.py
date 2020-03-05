from fbscraper.actions.update.update_crawler import UpdateCrawler
from config import DEFAULT_IS_LOGINED


class UpdateSpider:
    def __init__(self, article_url, db, article_id, browser, timeout, is_logined=DEFAULT_IS_LOGINED):
        self.article_url = article_url
        self.db = db
        self.article_id = article_id
        self.browser = browser
        self.is_logined = is_logined
        self.timeout = timeout

    def work(self):
        crawler = UpdateCrawler(article_url=self.article_url,
                                article_id=self.article_id,
                                db=self.db,
                                browser=self.browser,
                                timeout=self.timeout,
                                is_logined=self.is_logined)
        crawler.crawl()
