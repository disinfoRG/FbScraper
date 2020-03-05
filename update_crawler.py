import logging
logger = logging.getLogger(__name__)
from helper import helper, SelfDefinedError
from selenium.common.exceptions import NoSuchElementException, MoveTargetOutOfBoundsException
import re
import time
from config import DEFAULT_IS_LOGINED, DEFAULT_MAX_TRY_TIMES, DEFAULT_SHOULD_LOAD_COMMENT, DEFAULT_SHOULD_TURN_OFF_COMMENT_FILTER
from update_parser import UpdateParser

class UpdateCrawler:
    def __init__(self, article_url, browser, parser, pipeline, timeout, max_try_times=DEFAULT_MAX_TRY_TIMES, is_logined=DEFAULT_IS_LOGINED):
        self.article_url = helper.get_clean_url(article_url)
        self.browser = browser
        self.post_node = None
        self.parser = parser
        self.pipeline = pipeline
        self.max_try_times = max_try_times
        self.is_logined = is_logined
        self.start_at = None
        self.timeout = timeout
        self.should_load_comment = DEFAULT_SHOULD_LOAD_COMMENT
        self.should_turn_off_comment_filter = DEFAULT_SHOULD_TURN_OFF_COMMENT_FILTER

    def log_crawler(self, depth, comment_loaders_total, clicked_count, empty_count):
        timestamp = 'crawler_timestamp_{}: expanding comments at level #{}, found comment loader total is {}, has clicked loader count is {}, empty response count #{} \n'.format(helper.now(), depth, comment_loaders_total, clicked_count, empty_count)
        logger.debug(timestamp)

    def crawl(self):
        try:
            self.start_at = helper.now()
            self.enter_site()
            is_located = self.locate_target_post()

            if is_located:
                self.expand_comment()
            else:
                selector = '.permalinkPost' if self.is_logined else '.userContentWrapper'
                raise NoSuchElementException('[post_crawler] Cannot locate target post with selector={}'.format(selector))

            self.save()
            logger.debug(f'[INFO] Article {self.article_id} update successfully.')

        except Exception as e:
            self.save()
            note = 'url={}, is_logined={}'.format(self.article_url, self.is_logined)
            logger.error(f"{e}, note: {note}")
            raise

    def save(self):
        raw_html = self.parser.get_post_raw_html(self.browser.page_source)
        try:
            self.pipeline and self.pipeline.update_article(raw_html)
        except Exception as e:
            logger.error(e)
            raise

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
            logger.debug(success_status)
        except Exception as e:
            failed_status = 'crawler_timestamp_{}: failed to enter site with url "{}", error is {}'.format(helper.now(), post_root_url, helper.print_error(e))
            logger.debug(failed_status)
            raise

        if not self.is_logined:
            block_selector = '#headerArea'
            try:
                helper.remove_element_by_selector(block_selector, self.browser)
                removed_block_text = 'crawler_timestamp_{}: removed block element for non-logined browsing with selector="{}" \n'.format(helper.now(), block_selector)
                logger.debug(removed_block_text)
            except Exception as e:
                logger.error(f"{e}, note: {block_selector}")

    def locate_target_post(self):
        selector = '.permalinkPost' if self.is_logined else '.userContentWrapper'

        self.post_node = helper.get_element(self.browser, selector)

        if not self.post_node:
            post_not_found = 'crawler_timestamp_{}: failed and article not found with selector "{}", article url is {} \n'.format(helper.now(), selector, self.article_url)
            logger.debug(post_not_found)
            return False
        else:
            post_is_found = 'crawler_timestamp_{}: success and article is located with selector "{}", article url is {} \n'.format(helper.now(), selector, self.article_url)
            logger.debug(post_is_found)
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
                logger.error(f"{e}, note: {display_comment_selector}")

    def turn_off_comment_filter(self):
        filter_menu_link_selector = '[data-testid="UFI2ViewOptionsSelector/root"] [data-testid="UFI2ViewOptionsSelector/link"]'
        filter_menu_selector = '[data-testid="UFI2ViewOptionsSelector/menuRoot"]'
        unfiltered_option_selector = '[data-testid="UFI2ViewOptionsSelector/menuRoot"] [data-ordering="RANKED_UNFILTERED"]'

        try:
            helper.click_with_move(filter_menu_link_selector, self.browser)
            logger.debug('crawler_timestamp_{}: clicked comment filter button with selector="{}" \n'.format(helper.now(), filter_menu_link_selector))
            helper.move_to_element_by_selector(filter_menu_selector, self.browser)
            logger.debug('crawler_timestamp_{}: comment filter menu is shown with selector="{}" \n'.format(helper.now(), filter_menu_selector))
            helper.click_with_move(unfiltered_option_selector, self.browser)
            logger.debug('crawler_timestamp_{}: clicked comment filter "RANKED_UNFILTERED" with selector="{}" \n'.format(helper.now(), unfiltered_option_selector))
        except Exception as e:
            selector = '{} and {}'.format(filter_menu_link_selector, unfiltered_option_selector)
            failed_status = 'crawler_timestamp_{}: failed to turn off comment filter with selector "{}", error is {} \n'.format(helper.now(), selector, helper.print_error(e))
            logger.debug(failed_status)

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
                            logger.error(f"{e}, note: {cls_html}")
                        else:
                            logger.error(e)
                        is_clicked = helper.click(close_button, self.browser)

                if not is_clicked:
                    empty_count += 1
                else:
                    clicked_count += 1

                self.log_crawler(depth, comment_loaders_total, clicked_count, empty_count)
                helper.wait()

        except Exception as e:
            failed_status = 'crawler_timestamp_{}: failed to load comment at depth level #{} with selector "{}", error is {} \n'.format(helper.now(), depth, comment_expander_selector, helper.print_error(e))
            logger.debug(failed_status)

        crawled_time = helper.now() - self.start_at
        time_status = '[{}][update_crawler.py - load_comment] Timeout: {}, Crawled: {}. is_timeout={}'.format(helper.now(), self.timeout, crawled_time, self.timeout < crawled_time)
        logger.debug(time_status)
