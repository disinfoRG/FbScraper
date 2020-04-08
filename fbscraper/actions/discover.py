import time
import random
import logging

logger = logging.getLogger(__name__)
from bs4 import BeautifulSoup
import zlib
from fbscraper.settings import (
    DEFAULT_MAX_TRY_TIMES,
    DEFAULT_SHOULD_USE_ORIGINAL_URL,
    STATUS_SUCCESS,
)
import fbscraper.facebook as fb


class DiscoverCrawler:
    def __init__(
        self,
        site_url,
        site_id,
        browser,
        existing_article_urls,
        db,
        limit_sec,
        max_try_times=DEFAULT_MAX_TRY_TIMES,
        should_use_original_url=DEFAULT_SHOULD_USE_ORIGINAL_URL,
    ):
        self.site_url = site_url
        self.site_id = site_id
        self.browser = browser
        self.existing_article_urls = existing_article_urls
        self.max_try_times = max_try_times if max_try_times else DEFAULT_MAX_TRY_TIMES
        self.db = db
        self.should_use_original_url = should_use_original_url
        self.limit_sec = limit_sec
        self.start_at = None

    def crawl_and_save(self):
        self.start_at = int(time.time())
        self.enter_site()
        self.expand_page_and_insert_article()

    def enter_site(self):
        post_root_url = self.site_url
        if not self.should_use_original_url:
            if post_root_url.endswith("/"):
                post_root_url += "posts"
            else:
                post_root_url += "/posts"
        self.browser.get(post_root_url)

        fb.raise_if_security_check(self.browser)
        time.sleep(random.uniform(2, 3))

    def expand_page_and_insert_article(self):
        viewed_count = 0
        new_count = 0
        empty_count = 0

        while (
            int(time.time()) - self.start_at
        ) < self.limit_sec and empty_count < self.max_try_times:
            self.log_crawler(
                viewed_count, new_count, len(self.existing_article_urls), empty_count
            )
            self.browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(random.uniform(2, 3))

            post_urls = self.get_post_urls_from_html(html=self.browser.page_source)
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
                        article_id = self.insert_article(p_url)
                        self.db.update_site_crawl_time(site_id=self.site_id, last_crawl_at=int(time.time()))
                        self.log_pipeline(article_id)

                # reset empty count check when new_count > 0
                empty_count = 0
                self.existing_article_urls += new_post_urls

        crawled_time = int(time.time()) - self.start_at
        time_status = f"[discover crawler - expand_page_and_insert_article] LimitSec: {self.limit_sec}, Crawled: {crawled_time}. is_over_limit_sec={self.limit_sec < crawled_time}"
        logger.debug(time_status)

    def remove_old_post_urls(self, post_urls):
        return list(set(post_urls) - set(self.existing_article_urls))

    def get_post_urls_from_html(self, html):
        soup = BeautifulSoup(html, "html.parser")
        post_elements = soup.find_all("div", {"class": "userContentWrapper"})
        return [self.extract_post_url_from_element(post) for post in post_elements]

    @staticmethod
    def extract_post_url_from_element(post):
        result = None
        anchors = post.select('[data-testid="story-subtitle"] a')
        for index, anchor in enumerate(anchors):
            hasTimestamp = len(anchor.select("abbr > span.timestampContent")) > 0

            if hasTimestamp:
                url = anchor.get("href")
                if url:
                    url_info = fb.get_facebook_url_info(url)
                    if url_info["permalink"]:
                        result = url_info["permalink"]
                        break
                    elif url_info["original_url"]:
                        result = url_info["original_url"]

        return result

    def insert_article(self, article_url):
        article = dict()

        article["first_snapshot_at"] = 0
        article["last_snapshot_at"] = 0
        article["next_snapshot_at"] = -1
        article["snapshot_count"] = 0
        article["url_hash"] = zlib.crc32(article_url.encode())
        article["url"] = article_url
        article["site_id"] = self.site_id
        article["article_type"] = "FBPost"
        article["created_at"] = int(time.time())
        article["redirect_to"] = None

        article_id = self.db.insert_article(article)

        return article_id

    @staticmethod
    def log_crawler(viewed_count, new_count, existing_count, empty_count):
        timestamp = f"crawler: viewed {viewed_count} posts, add {new_count} new posts, existing {existing_count} posts in database, empty response count #{empty_count} \n"
        logger.debug(timestamp)

    @staticmethod
    def log_pipeline(article_id):
        message = f"pipeline: [{STATUS_SUCCESS}] insert Article #{article_id} \n"
        logger.info(message)
