import helper
from selenium.common.exceptions import NoSuchElementException

class GroupPostCrawler:
    def __init__(self, url, browser, write_to_db, logfile, max_try_times=3):
        self.url = helper.get_clean_url(url)
        self.browser = browser
        self.post_node = None
        self.write_to_db = write_to_db
        self.logfile = logfile
        self.max_try_times = max_try_times

    def log_crawler(self, depth, comment_loaders_total, clicked_count, empty_count):
        timestamp = 'crawler_timestamp_{}: expanding comments at level #{}, found comment loader total is {}, has clicked loader count is {}, empty response count #{} \n'.format(helper.now(), depth, comment_loaders_total, clicked_count, empty_count)
        self.logfile.write(timestamp)        

    def crawl(self):
        self.logfile.write('\n')
        self.enter_site()
        is_located = self.locate_target_post()

        if is_located:
            self.expand_comment()
            raw_html = self.get_raw_html()
            self.write_to_db and self.write_to_db(raw_html)
        else:
            raise NoSuchElementException

    def get_raw_html(self):
        # return self.browser.page_source # failed for https://www.facebook.com/znk168/posts/412649276099554
        return helper.get_html(self.post_node)

    def enter_site(self):
        post_root_url = self.url

        try:
            self.browser.get(post_root_url)
            success_status = 'crawler_timestamp_{}: successful to enter site with url "{}"'.format(helper.now(), post_root_url)
            self.logfile.write(success_status)
            helper.wait()
        except Exception as e:
            failed_status = 'crawler_timestamp_{}: failed to enter site with url "{}", error is {}'.format(helper.now(), post_root_url, helper.print_error(e))
            self.logfile.write(failed_status)

    def locate_target_post(self):
        selector = '.userContentWrapper'
        self.post_node = helper.get_element(self.browser, selector)

        if not self.post_node:
            post_not_found = 'crawler_timestamp_{}: failed and article not found with selector "{}", article url is {} \n'.format(helper.now(), selector, self.url)
            self.logfile.write(post_not_found)
            return False
        else:
            post_is_found = 'crawler_timestamp_{}: success and article is located with selector "{}", article url is {} \n'.format(helper.now(), selector, self.url)
            self.logfile.write(post_is_found)
            return True

    def expand_comment(self):
        if not self.post_node:
            return

        self.turn_off_comment_filter()
        self.load_comment(0)
        # self.load_comment(1)

    def turn_off_comment_filter(self):
        selector = '[data-testid="UFI2ViewOptionsSelector/root"]'

        try:
            c_filter_button = self.post_node.find_element_by_css_selector(selector)

            helper.click(c_filter_button, self.browser)
            self.logfile.write('crawler_timestamp_{}: clicked comment filter button \n'.format(helper.now()))
            helper.wait()

            c_filter_menu = helper.get_element(self.browser, '[data-testid="UFI2ViewOptionsSelector/menuRoot"]')
            self.logfile.write('crawler_timestamp_{}: comment filter menu is shown \n'.format(helper.now()))
            helper.wait()

            c_no_filter = helper.get_element(c_filter_menu, '[data-ordering="RANKED_UNFILTERED"]')
            helper.click(c_no_filter, self.browser)
            self.logfile.write('crawler_timestamp_{}: clicked comment filter "RANKED_UNFILTERED" \n'.format(helper.now()))
            helper.wait()
        except Exception as e:
            failed_status = 'crawler_timestamp_{}: failed to turn off comment filter with selector "{}", error is {} \n'.format(helper.now(), selector, helper.print_error(e))
            self.logfile.write(failed_status)
        
    def load_comment(self, depth):
        comment_expander_selector = '[data-testid="UFI2CommentsPagerRenderer/pager_depth_{}"]'.format(depth)

        try:
            empty_count = 0
            while empty_count < self.max_try_times:
                comment_loaders = self.post_node.find_elements_by_css_selector(comment_expander_selector)
                comment_loaders_total = len(comment_loaders)
                clicked_count = 0

                if comment_loaders_total > 0:
                    empty_count = 0

                    for c_loader in comment_loaders:
                        # print(c_loader.get_attribute('innerText'))
                        is_clicked = helper.click(c_loader, self.browser)
                        if is_clicked:
                            helper.wait()
                            clicked_count += 1
                            self.log_crawler(depth, comment_loaders_total, clicked_count, empty_count)
                        else:
                            pass
                elif clicked_count == 0 or comment_loaders_total == 0:
                    empty_count += 1
                    self.log_crawler(depth, comment_loaders_total, clicked_count, empty_count)

                helper.wait()
        except Exception as e:
            failed_status = 'crawler_timestamp_{}: failed to load comment at depth level #{} with selector "{}", error is {} \n'.format(helper.now(), depth, comment_expander_selector, helper.print_error(e))
            self.logfile.write(failed_status)

def main():
    article_url = 'https://www.facebook.com/almondbrother/posts/3070894019610988'

    from config import fb
    fb.start()
    browser = fb.driver

    from logger import Logger
    fpath = 'test_post_crawler_{}.log'.format(helper.now())
    logfile = Logger(open(fpath, 'a', buffering=1))

    pc = PostCrawler(article_url, browser, print, logfile)
    pc.crawl()
    

if __name__ == '__main__':
    main()