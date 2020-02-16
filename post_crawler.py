from helper import helper
from selenium.common.exceptions import NoSuchElementException, MoveTargetOutOfBoundsException
import re
from urllib3.exceptions import MaxRetryError

class PostCrawler:
    def __init__(self, url, browser, write_to_db, logfile, max_try_times=3, is_logined=False, timeout=720):
        self.url = helper.get_clean_url(url)
        self.browser = browser
        self.post_node = None
        self.write_to_db = write_to_db
        self.logfile = logfile
        self.max_try_times = max_try_times
        self.is_logined = is_logined
        self.start_at = None
        self.timeout = timeout
        self.should_load_comment = False
        self.should_turn_off_comment_filter = False

    def log_crawler(self, depth, comment_loaders_total, clicked_count, empty_count):
        timestamp = 'crawler_timestamp_{}: expanding comments at level #{}, found comment loader total is {}, has clicked loader count is {}, empty response count #{} \n'.format(helper.now(), depth, comment_loaders_total, clicked_count, empty_count)
        self.logfile.write(timestamp)        

    def crawl(self):
        self.start_at = helper.now()
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
        # to get the "current" post node 
        self.locate_target_post()
        return helper.get_html(self.post_node)

    def enter_site(self):
        post_root_url = self.url

        try:
            self.browser.get(post_root_url)
            success_status = 'crawler_timestamp_{}: successful to enter site with url "{}"'.format(helper.now(), post_root_url)
            self.logfile.write(success_status)
        except Exception as e:
            failed_status = 'crawler_timestamp_{}: failed to enter site with url "{}", error is {}'.format(helper.now(), post_root_url, helper.print_error(e))
            self.logfile.write(failed_status)
            
        if not self.is_logined:
            # window_block_selector = '#expanding_cta_close_button'
            # try:        
            #     helper.click_with_move(window_block_selector, self.browser)
            # except Exception as e:
            #     helper.print_error(e, window_block_selector)

            block_selector = '#headerArea'
            try:
                helper.remove_element(block_selector, self.browser)
                removed_block_text = 'crawler_timestamp_{}: removed block element for non-logined browsing with selector="{}" \n'.format(helper.now(), block_selector)
                self.logfile.write(removed_block_text)
            except Exception as e:
                helper.print_error(e, block_selector)
                is_robot_block = self.is_robot_check()
                if is_robot:
                    raise MaxRetryError
                is_login_block = self.is_login_check()
                if is_login_block:
                    raise MaxRetryError
            

    def locate_target_post(self):
        selector = '.permalinkPost' if self.is_logined else '.userContentWrapper'
        
        self.post_node = helper.get_element(self.browser, selector)

        if not self.post_node:
            post_not_found = 'crawler_timestamp_{}: failed and article not found with selector "{}", article url is {} \n'.format(helper.now(), selector, self.url)
            self.logfile.write(post_not_found)
            return False
        else:
            post_is_found = 'crawler_timestamp_{}: success and article is located with selector "{}", article url is {} \n'.format(helper.now(), selector, self.url)
            self.logfile.write(post_is_found)
            return True

    def is_robot_check(self):
        is_robot_url = re.match('.*/checkpoint.*', self.browser.current_url)
        if is_robot_url:
            return True
        return False

    def is_login_check(self):
        is_login_url = re.match('.*/login.*', self.browser.current_url)
        if is_login_url:
            return True
        # id of button with text: "忘記帳號？" but not the id for page of "稍後再說"
        is_forced_login = True if len(self.browser.find_elements_by_css_selector('#login_link')) > 0 else False
        if is_forced_login:
            return True
        return False

    def expand_comment(self):
        if not self.post_node:
            return

        self.show_comment()

        if self.should_turn_off_comment_filter:
            self.turn_off_comment_filter()

        is_login_page = re.match('.*/login.*', self.browser.current_url)
        if is_login_page:
            self.browser.back()
            helper.wait()
            self.locate_target_post()

        if self.should_load_comment:
            self.load_comment(0)
            self.load_comment(1)

    def show_comment(self):
        if not self.is_logined:
            display_comment_selector = '.userContentWrapper [data-testid="UFI2CommentsCount/root"]'
            try:
                helper.click_with_move(display_comment_selector, self.browser, timeout=0)
                helper.wait()
            except Exception as e:
                helper.print_error(e, display_comment_selector)

    def turn_off_comment_filter(self):
        filter_menu_selector = '[data-testid="UFI2ViewOptionsSelector/root"] a[data-testid="UFI2ViewOptionsSelector/link"]'
        unfiltered_option_selector = '[data-testid="UFI2ViewOptionsSelector/menuRoot"] [data-ordering="RANKED_UNFILTERED"]'
        
        try:
            helper.click_with_move(filter_menu_selector, self.browser)
            helper.wait()
            helper.click_with_move(unfiltered_option_selector, self.browser)
            helper.wait()
            # selector = '[data-testid="UFI2ViewOptionsSelector/root"]'
            # c_filter_button = self.post_node.find_element_by_css_selector(selector)

            # helper.click_with_move(c_filter_button, self.browser, should_offset=True)
            # self.logfile.write('crawler_timestamp_{}: clicked comment filter button \n'.format(helper.now()))
            # helper.wait()

            # c_filter_menu = helper.get_element(self.browser, '[data-testid="UFI2ViewOptionsSelector/menuRoot"]')
            # self.logfile.write('crawler_timestamp_{}: comment filter menu is shown \n'.format(helper.now()))
            # helper.wait()

            # c_no_filter = helper.get_element(c_filter_menu, '[data-ordering="RANKED_UNFILTERED"]')
            # helper.click_with_move(c_no_filter, self.browser, should_offset=True)
            # self.logfile.write('crawler_timestamp_{}: clicked comment filter "RANKED_UNFILTERED" \n'.format(helper.now()))
            # helper.wait()
        except Exception as e:
            selector = '{} and {}'.format(filter_menu_selector, unfiltered_option_selector)
            failed_status = 'crawler_timestamp_{}: failed to turn off comment filter with selector "{}", error is {} \n'.format(helper.now(), selector, helper.print_error(e))
            self.logfile.write(failed_status)
        
    def load_comment(self, depth, clicked_max_times=50):
        comment_expander_selector = '[data-testid="UFI2CommentsPagerRenderer/pager_depth_{}"]'.format(depth)

        try:
            clicked_count = 0
            empty_count = 0
            comment_loaders_total = 0
            self.log_crawler(depth, comment_loaders_total, clicked_count, empty_count)

            while (helper.now() - self.start_at) < self.timeout and empty_count < self.max_try_times and clicked_count < clicked_max_times:
                comment_loaders = self.post_node.find_elements_by_css_selector(comment_expander_selector)
                comment_loaders_total = len(comment_loaders)
                is_clicked = False
                if comment_loaders_total > 0:
                    try:
                        is_clicked = helper.click_with_move(comment_expander_selector, self.browser)

                    except MoveTargetOutOfBoundsException as e:
                        # https://www.facebook.com/photo.php?fbid=3321929767823884&set=p.3321929767823884&type=3&theater
                        dialog_close_button = self.browser.find_element_by_link_text('關閉')
                        if dialog_close_button is not None:
                            cls_html = helper.get_html(dialog_close_button)
                            helper.print_error(e, cls_html)
                        else:
                            helper.print_error(e)
                        is_clicked = helper.click(close_button, self.browser)
    
                if not is_clicked:
                    empty_count += 1
                else:
                    clicked_count += 1

                self.log_crawler(depth, comment_loaders_total, clicked_count, empty_count)
                helper.wait()
                
        except Exception as e:
            failed_status = 'crawler_timestamp_{}: failed to load comment at depth level #{} with selector "{}", error is {} \n'.format(helper.now(), depth, comment_expander_selector, helper.print_error(e))
            self.logfile.write(failed_status)

def main():
    # 12min = 12*60 = 720sec
    # article_url = 'https://www.facebook.com/almondbrother/posts/3070894019610988'
    # article_url = 'https://www.facebook.com/travelmoviemusic/posts/2780616305352791'
    # article_url = 'https://www.facebook.com/twherohan/posts/2689813484589132'
    # article_url = 'https://www.facebook.com/almondbrother/posts/725869957939281'
    article_url = 'https://www.facebook.com/todayreview88/posts/2283660345270675'
    # article_url = 'https://www.facebook.com/eatnews/posts/488393351879106'

    from config import fb
    fb.start(False)
    browser = fb.driver

    from logger import Logger
    fpath = 'test_post_crawler_{}.log'.format(helper.now())
    logfile = Logger(open(fpath, 'a', buffering=1))

    pc = PostCrawler(article_url, browser, print, logfile)
    pc.crawl()
    browser.quit()
    
if __name__ == '__main__':
    main()