import helper
import page_parser_helper as ppa_helper
from bs4 import BeautifulSoup


class PageCrawler:
    def __init__(self, url, browser, existing_article_urls, write_to_db_func, max_try_times=3):
        self.url = helper.get_clean_url(url)
        self.browser = browser
        self.existing_article_urls = existing_article_urls
        self.max_try_times = max_try_times
        self.write_to_db_func = write_to_db_func

    def crawl(self):
        self.enter_site()
        self.expand_post()

    def enter_site(self):
        post_root_url = self.url
        if post_root_url.endswith('/'):
            post_root_url += 'posts'
        else:
            post_root_url += '/posts'
        self.browser.get(post_root_url)
        helper.wait()

    def expand_post(self):
        empty_count = 0
        while empty_count < self.max_try_times:
            height_before, height_after = self.scroll()
            if height_after <= height_before:
                break

            post_urls = self.get_post_urls()
            new_post_urls = self.remove_old_post_urls(post_urls)

            if len(new_post_urls) == 0:
                empty_count += 1
            else:
                for p_url in new_post_urls:
                    self.write_to_db_func(p_url)

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
        print(height_after_scroll, height_before_scroll)

        return height_before_scroll, height_after_scroll
