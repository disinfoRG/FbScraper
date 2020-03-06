from fbscraper.actions.discover.discover_crawler import DiscoverCrawler


class DiscoverSpider:
    def __init__(
        self,
        site_url,
        db,
        site_id,
        browser,
        existing_article_urls,
        max_try_times,
        timeout,
        should_use_original_url=False,
    ):
        self.site_url = site_url
        self.db = db
        self.site_id = site_id
        self.browser = browser
        self.existing_article_urls = existing_article_urls
        self.max_try_times = max_try_times
        self.timeout = timeout
        self.should_use_original_url = should_use_original_url

    def work(self):
        crawler = DiscoverCrawler(
            site_url=self.site_url,
            site_id=self.site_id,
            db=self.db,
            browser=self.browser,
            existing_article_urls=self.existing_article_urls,
            timeout=self.timeout,
            max_try_times=self.max_try_times,
            should_use_original_url=self.should_use_original_url,
        )
        crawler.crawl()
