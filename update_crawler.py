from helper import helper, SelfDefinedError
from selenium.common.exceptions import NoSuchElementException, MoveTargetOutOfBoundsException
import re
from config import DEFAULT_IS_LOGINED, UPDATE_CRAWLER_TIMEOUT
from update_parser import UpdateParser

class UpdateCrawler:
    def __init__(self, article_url, browser, parser, pipeline, logfile, timeout, max_try_times=3, is_logined=DEFAULT_IS_LOGINED):
        self.article_url = helper.get_clean_url(article_url)
        self.browser = browser
        self.post_node = None
        self.parser = parser
        self.pipeline = pipeline
        self.logfile = logfile
        self.max_try_times = max_try_times
        self.is_logined = is_logined
        self.start_at = None
        self.timeout = timeout
        self.should_load_comment = True
        self.should_turn_off_comment_filter = True

    def log_crawler(self, depth, comment_loaders_total, clicked_count, empty_count):
        timestamp = 'crawler_timestamp_{}: expanding comments at level #{}, found comment loader total is {}, has clicked loader count is {}, empty response count #{} \n'.format(helper.now(), depth, comment_loaders_total, clicked_count, empty_count)
        self.logfile and self.logfile.write(timestamp)        

    def crawl(self):
        try:
            self.start_at = helper.now()
            self.logfile and self.logfile.write('\n')
            self.enter_site()
            is_located = self.locate_target_post()

            if is_located:
                self.expand_comment()
            else:
                selector = '.permalinkPost' if self.is_logined else '.userContentWrapper'
                raise NoSuchElementException('[post_crawler] Cannot locate target post with selector={}'.format(selector))

            self.save()
        except Exception as e:
            self.save()
            note = 'url={}, is_logined={}'.format(self.article_url, self.is_logined)
            helper.print_error(e, note)
            raise

    def save(self):
        raw_html = self.get_raw_html()
        try:
            self.pipeline and self.pipeline.pipe_single_post_raw_data(raw_html)
        except Exception as e:
            helper.print_error(e)
            raise

    def get_raw_html(self):
        return self.parser.get_post_raw_html(self.browser.page_source)


    def enter_site(self):
        post_root_url = self.article_url

        try:
            self.browser.get(post_root_url)
            helper.scroll(self.browser)

            is_robot_block = self.is_robot_check()
            if is_robot_block:
                raise SelfDefinedError('Encountered security check if user is a robot')

            is_login_block = self.is_login_check()
            if is_login_block:
                raise SelfDefinedError('Encountered security check requiring user to login')

            success_status = 'crawler_timestamp_{}: successful to enter site with url "{}"'.format(helper.now(), post_root_url)
            self.logfile and self.logfile.write(success_status)
        except Exception as e:
            failed_status = 'crawler_timestamp_{}: failed to enter site with url "{}", error is {}'.format(helper.now(), post_root_url, helper.print_error(e))
            self.logfile and self.logfile.write(failed_status)
            raise

        if not self.is_logined:
            # window_block_selector = '#expanding_cta_close_button'
            # try:        
            #     helper.click_with_move(window_block_selector, self.browser)
            # except Exception as e:
            #     helper.print_error(e, window_block_selector)
            block_selector = '#headerArea'
            try:
                helper.remove_element_by_selector(block_selector, self.browser)
                removed_block_text = 'crawler_timestamp_{}: removed block element for non-logined browsing with selector="{}" \n'.format(helper.now(), block_selector)
                self.logfile and self.logfile.write(removed_block_text)
            except Exception as e:
                helper.print_error(e, block_selector)

    def locate_target_post(self):
        selector = '.permalinkPost' if self.is_logined else '.userContentWrapper'
        
        self.post_node = helper.get_element(self.browser, selector)

        if not self.post_node:
            post_not_found = 'crawler_timestamp_{}: failed and article not found with selector "{}", article url is {} \n'.format(helper.now(), selector, self.article_url)
            self.logfile and self.logfile.write(post_not_found)
            return False
        else:
            post_is_found = 'crawler_timestamp_{}: success and article is located with selector "{}", article url is {} \n'.format(helper.now(), selector, self.article_url)
            self.logfile and self.logfile.write(post_is_found)
            return True

    def is_robot_check(self):
        is_robot_url = re.match('.*/checkpoint.*', self.browser.current_url)
        if is_robot_url:
            return True
        is_forced_robot_verify = True if len(self.browser.find_elements_by_css_selector('#captcha')) > 0 else False
        if is_forced_robot_verify:
            return True
        return False

    def is_login_check(self):
        is_login_url = re.match('.*/login.*', self.browser.current_url)
        if is_login_url:
            return True
        # id of button with text: "忘記帳號？" but not the id for page of "稍後再說"
        is_forced_login_verify = True if len(self.browser.find_elements_by_css_selector('#login_link')) > 0 else False
        if is_forced_login_verify:
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
        filter_menu_link_selector = '[data-testid="UFI2ViewOptionsSelector/root"] [data-testid="UFI2ViewOptionsSelector/link"]'
        filter_menu_selector = '[data-testid="UFI2ViewOptionsSelector/menuRoot"]'
        unfiltered_option_selector = '[data-testid="UFI2ViewOptionsSelector/menuRoot"] [data-ordering="RANKED_UNFILTERED"]'
        
        try:
            helper.click_with_move(filter_menu_link_selector, self.browser)
            self.logfile and self.logfile.write('crawler_timestamp_{}: clicked comment filter button with selector="{}" \n'.format(helper.now(), filter_menu_link_selector))
            helper.move_to_element_by_selector(filter_menu_selector, self.browser)
            self.logfile and self.logfile.write('crawler_timestamp_{}: comment filter menu is shown with selector="{}" \n'.format(helper.now(), filter_menu_selector))
            helper.click_with_move(unfiltered_option_selector, self.browser)
            self.logfile and self.logfile.write('crawler_timestamp_{}: clicked comment filter "RANKED_UNFILTERED" with selector="{}" \n'.format(helper.now(), unfiltered_option_selector))
        except Exception as e:
            selector = '{} and {}'.format(filter_menu_link_selector, unfiltered_option_selector)
            failed_status = 'crawler_timestamp_{}: failed to turn off comment filter with selector "{}", error is {} \n'.format(helper.now(), selector, helper.print_error(e))
            self.logfile and self.logfile.write(failed_status)
        
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
            self.logfile and self.logfile.write(failed_status)

        crawled_time = helper.now() - self.start_at
        time_status = '[{}][update_crawler.py - load_comment] Timeout: {}, Crawled: {}. is_timeout={}'.format(helper.now(), self.timeout, crawled_time, self.timeout < crawled_time)
        print(time_status)

def test_robot_check(url):
    is_robot_url = re.match('.*/checkpoint.*', url)
    if is_robot_url:
        return True
    return False    

def main():
    # 12min = 12*60 = 720sec
    # article_url = 'https://www.facebook.com/travelmoviemusic/posts/2780616305352791' # 2 comments
    # article_url = 'https://www.facebook.com/twherohan/posts/2689813484589132' # thousands comments
    # article_url = 'https://www.facebook.com/almondbrother/posts/725869957939281' # video
    # article_url = 'https://www.facebook.com/todayreview88/posts/2283660345270675' # hundreds comments
    # article_url = 'https://www.facebook.com/eatnews/posts/488393351879106' # thounds shares
    # article_url = 'https://www.facebook.com/lovebakinglovehealthy/posts/1970662936284274' # no comments
    # article_url = 'https://www.facebook.com/fuqidao168/posts/2466415456951685' # non-existing article
    article_url = 'https://www.facebook.com/twherohan/posts/2461318357438647' # ten-thousands comments
    
    start_time = helper.now()
    print('[{}][main] Start'.format(start_time))

    from facebook import Facebook
    from settings import FB_EMAIL, FB_PASSWORD, CHROMEDRIVER_BIN

    fb = Facebook(FB_EMAIL, FB_PASSWORD, 'Chrome', CHROMEDRIVER_BIN, True)
    fb.start(False)
    browser = fb.driver

    from logger import Logger
    fpath = 'test_post_crawler_{}.log'.format(helper.now())
    logfile = Logger(open(fpath, 'a', buffering=1))

    
    # with open('cannot-locate-post-node_NoSuchElementException.html', 'w') as html_file:
    with open('test-timeout.html', 'w') as html_file:
        parser = UpdateParser()
        pc = UpdateCrawler(article_url, browser, parser, html_file.write, logfile, timeout=10)
        pc.crawl()

    browser.quit()

    end_time = helper.now()
    print('[{}][main] End, spent: {}'.format(end_time, end_time - start_time))
    
if __name__ == '__main__':
    main()