from bs4 import BeautifulSoup
import time
import zlib
from helper import helper
from config import DEFAULT_MAX_TRY_TIMES


class DiscoverCrawler:
    def __init__(self, url, site_id, browser, existing_article_urls, queries, logfile, max_try_times, should_use_original_url=False):
        self.url = helper.get_clean_url(url)
        self.site_id = site_id
        self.browser = browser
        self.existing_article_urls = existing_article_urls
        self.max_try_times = max_try_times if max_try_times else DEFAULT_MAX_TRY_TIMES
        self.queries = queries
        self.logfile = logfile
        self.should_use_original_url = should_use_original_url

    def crawl_and_save(self):
        self.logfile.write('\n')
        self.enter_site()
        self.expand_page_and_insert_article()

    def enter_site(self):
        post_root_url = self.url
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

        while empty_count < self.max_try_times:
            self.log_crawler(viewed_count, new_count, len(self.existing_article_urls), empty_count)
            helper.scroll(self.browser)
            helper.wait()

            post_urls = self.get_post_urls()
            viewed_count = len(post_urls)
            new_post_urls = list(set(post_urls) - set(self.existing_article_urls))
            new_count = len(new_post_urls)
            
            if new_count == 0:
                if viewed_count < len(self.existing_article_urls):
                    continue
                else:
                    empty_count += 1                    
            else:
                for p_url in new_post_urls:
                    if p_url:
                        self.insert_article(post_url=p_url)

                # reset empty count check when new_count > 0
                empty_count = 0
                self.existing_article_urls += new_post_urls

    def insert_article(self, post_url):
        post = dict()

        post['first_snapshot_at'] = 0
        post['last_snapshot_at'] = 0
        post['next_snapshot_at'] = -1
        post['snapshot_count'] = 0
        post['url_hash'] = zlib.crc32(post_url.encode())
        post['url'] = post_url
        post['site_id'] = self.site_id
        post['article_type'] = 'FBPost'
        post['created_at'] = int(time.time())
        post['redirect_to'] = None

        article_id = self.queries.insert_article(post)
        self.logfile.write(f'[SUCCESS] inserted new article {article_id}')

    @staticmethod
    def extract_post_urls_from_post_element(post):
        anchors = post.select('[data-testid="story-subtitle"] a')
        for index, anchor in enumerate(anchors):
            try:
                hasTimestamp = anchor.select('abbr > span.timestampContent')
                if hasTimestamp:
                    url = anchor.get('href')
                    url_info = helper.get_facebook_url_info(url)
                    if url_info['permalink'] is not None:
                        return url_info['permalink']
                    elif url_info['original_url'] is not None:
                        return url_info['original_url']
            except:
                pass
        return None

    def get_post_urls(self):
        soup = BeautifulSoup(self.browser.page_source, 'html.parser')
        post_elements = soup.find_all('div', {'class': 'userContentWrapper'})
        posts_urls = [self.extract_post_urls_from_post_element(ele) for ele in post_elements]
        return posts_urls

    def log_crawler(self, viewed_count, new_count, existing_count, empty_count):
        timestamp = 'crawler_timestamp_{}: viewed {} posts, add {} new posts, existing {} posts in database, empty response count #{} \n'.format(helper.now(), viewed_count, new_count, existing_count, empty_count)
        self.logfile.write(timestamp)