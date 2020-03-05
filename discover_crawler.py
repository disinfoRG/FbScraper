import logging
logger = logging.getLogger(__name__)
from helper import helper
from config import DEFAULT_MAX_TRY_TIMES, DEFAULT_SHOULD_USE_ORIGINAL_URL

class DiscoverCrawler:
    def __init__(self, site_url, browser, existing_article_urls, parser, pipeline, timeout, max_try_times=DEFAULT_MAX_TRY_TIMES, should_use_original_url=DEFAULT_SHOULD_USE_ORIGINAL_URL):
        self.site_url = site_url
        self.browser = browser
        self.existing_article_urls = existing_article_urls
        self.max_try_times = max_try_times if max_try_times else DEFAULT_MAX_TRY_TIMES
        self.parser = parser
        self.pipeline = pipeline
        self.should_use_original_url = should_use_original_url
        self.timeout = timeout
        self.start_at = None

    def crawl(self):
        self.start_at = helper.now()
        self.enter_site()
        self.expand_page_and_insert_article()

    def enter_site(self):
        post_root_url = self.site_url
        if not self.should_use_original_url:
            if post_root_url.endswith('/'):
                post_root_url += 'posts'
            else:
                post_root_url += '/posts'
        self.browser.get(post_root_url)
        helper.wait()

    def expand_page_and_insert_article(self):
        viewed_count = 0
        new_count = 0
        empty_count = 0

        while (helper.now() - self.start_at) < self.timeout and empty_count < self.max_try_times:
            self.log_crawler(viewed_count, new_count, len(self.existing_article_urls), empty_count)
            helper.scroll(self.browser)
            helper.wait()

            post_urls = self.get_post_urls()
            viewed_count = len(post_urls)
            new_post_urls = self.remove_old_post_urls(post_urls)
            new_count = len(new_post_urls)

            if new_count == 0:
                if viewed_count < len(self.existing_article_urls):
                    continue
                else:
                    empty_count += 1
            else:
                for p_url in new_post_urls:
                    if p_url:
                        self.pipeline.insert_article(p_url)

                # reset empty count check when new_count > 0
                empty_count = 0
                self.existing_article_urls += new_post_urls

        crawled_time = helper.now() - self.start_at
        time_status = '[{}][discover_crawler.py - expand_page_and_insert_article] Timeout: {}, Crawled: {}. is_timeout={}'.format(helper.now(), self.timeout, crawled_time, self.timeout < crawled_time)
        logger.debug(time_status)

    def remove_old_post_urls(self, post_urls):
        return list(set(post_urls) - set(self.existing_article_urls))

    def get_post_urls(self):
        return self.parser.get_post_urls(self.browser.page_source)

    def log_crawler(self, viewed_count, new_count, existing_count, empty_count):
        timestamp = '[{}] crawler viewed {} posts, add {} new posts, existing {} posts in database, empty response count #{} \n'.format(helper.now(), viewed_count, new_count, existing_count, empty_count)
        logger.debug(timestamp)
