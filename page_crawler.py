from helper import helper
import page_parser_helper as ppa_helper
from bs4 import BeautifulSoup

MAX_TRY_TIMES_DEFAULT = 3

class PageCrawler:
    def __init__(self, url, browser, existing_article_urls, write_to_db_func, logfile, max_try_times=MAX_TRY_TIMES_DEFAULT, should_use_original_url=False):
        self.url = helper.get_clean_url(url)
        self.browser = browser
        self.existing_article_urls = existing_article_urls
        self.max_try_times = max_try_times if max_try_times else MAX_TRY_TIMES_DEFAULT
        self.write_to_db_func = write_to_db_func
        self.logfile = logfile
        self.should_use_original_url = should_use_original_url

    def crawl(self):
        self.logfile.write('\n')
        self.enter_site()
        self.expand_post()

    def enter_site(self):
        post_root_url = self.url
        if not self.should_use_original_url:
            if post_root_url.endswith('/'):
                post_root_url += 'posts'
            else:
                post_root_url += '/posts'
        self.browser.get(post_root_url)
        helper.wait()

    def log_crawler(self, viewed_count, new_count, existing_count, empty_count):
        timestamp = 'crawler_timestamp_{}: viewed {} posts, add {} new posts, existing {} posts in database, empty response count #{} \n'.format(helper.now(), viewed_count, new_count, existing_count, empty_count)
        self.logfile.write(timestamp)

    def expand_post(self):
        viewed_count = 0
        new_count = 0
        empty_count = 0

        while empty_count < self.max_try_times:
            self.log_crawler(viewed_count, new_count, len(self.existing_article_urls), empty_count)

            # # check if browser is hanging or site is loaded to the end
            # height_before, height_after = self.scroll()
            # if height_after <= height_before:
            #     break
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
                        self.write_to_db_func(p_url)

                # reset empty count check when new_count > 0
                empty_count = 0
                self.existing_article_urls += new_post_urls

    def remove_old_post_urls(self, post_urls):
        return list(set(post_urls) - set(self.existing_article_urls))

    def get_post_urls(self):
        soup = BeautifulSoup(self.browser.page_source, 'html.parser')
        post_elements = soup.find_all('div', {'class': 'userContentWrapper'})
        return [ppa_helper.get_post_url(post) for post in post_elements]

    def scroll(self):
        height_before_scroll = self.browser.execute_script("return document.body.scrollHeight")
        # scroll
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        helper.wait(10)
        # compare height to see if there's new element loaded
        height_after_scroll = self.browser.execute_script("return document.body.scrollHeight")

        return height_before_scroll, height_after_scroll
