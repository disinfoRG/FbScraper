import logging
logger = logging.getLogger(__name__)
from helper import helper, SelfDefinedError
from selenium.common.exceptions import MoveTargetOutOfBoundsException
import re
from config import DEFAULT_IS_LOGINED, DEFAULT_MAX_TRY_TIMES, \
    DEFAULT_SHOULD_LOAD_COMMENT, DEFAULT_SHOULD_TURN_OFF_COMMENT_FILTER
from fbscraper.actions.update.update_parser import UpdateParser
from fbscraper.actions.update.update_pipeline import UpdatePipeline

parser = UpdateParser()
pipeline = UpdatePipeline()


class UpdateCrawler:
    def __init__(self, article_url, article_id, db, browser, timeout, max_try_times=DEFAULT_MAX_TRY_TIMES, is_logined=DEFAULT_IS_LOGINED):
        self.article_url = article_url
        self.article_id = article_id
        self.db = db
        self.browser = browser
        self.post_selector = '.permalinkPost' if is_logined else '.userContentWrapper'
        self.post_node = None
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
        self.start_at = helper.now()
        self.enter_site()

        is_located = self.locate_target_post()
        if is_located:
            try:
                self.expand_comment()
                should_relocate_for_loaded_comment = True
            except:
                should_relocate_for_loaded_comment = False
                # continue to save() without comment
                # sometimes failed to expand comment due to random slow browser condition
                pass
        else:
            should_relocate_for_loaded_comment = False
            logger.debug(f'[post_crawler] Cannot locate target post with selector={self.post_selector}')

        if should_relocate_for_loaded_comment:
            self.locate_target_post()

        # save html with relocated post node
        self.save()

    def save(self):
        raw_html = helper.get_html(self.post_node) if self.post_node else parser.get_post_raw_html(self.browser.page_source)
        pipeline.update_article(self.db, self.article_id, raw_html)

    def enter_site(self):
        self.browser.get(self.article_url)
        # scroll to trigger any hidden security check
        helper.scroll(self.browser)

        is_robot_block = self.is_robot_check()
        if is_robot_block:
            raise SelfDefinedError('Encountered security check if user is a robot')

        is_login_block = self.is_login_check()
        if is_login_block:
            raise SelfDefinedError('Encountered security check requiring user to login')

        success_status = 'crawler_timestamp_{}: successful to enter site with url "{}"'.format(helper.now(), self.article_url)
        logger.debug(success_status)

        if not self.is_logined:
            block_selector = '#headerArea'
            helper.remove_element_by_selector(block_selector, self.browser)
            removed_block_text = 'crawler_timestamp_{}: removed block element for non-logined browsing with selector="{}" \n'.format(helper.now(), block_selector)
            logger.debug(removed_block_text)

    def locate_target_post(self):
        self.post_node = helper.get_element(self.browser, self.post_selector)

        if not self.post_node:
            post_not_found = 'crawler_timestamp_{}: failed and article not found with selector "{}", article url is {} \n'.format(helper.now(), self.post_selector, self.article_url)
            logger.debug(post_not_found)
            result = False
        else:
            post_is_found = 'crawler_timestamp_{}: success and article is located with selector "{}", article url is {} \n'.format(helper.now(), self.post_selector, self.article_url)
            logger.debug(post_is_found)
            result = True

        return result

    def is_robot_check(self):
        # is_robot_url
        if re.match('.*/checkpoint.*', self.browser.current_url):
            result = True
        # is_forced_robot_verify
        elif len(self.browser.find_elements_by_css_selector('#captcha')) > 0:
            result = True
        else:
            result = False

        return result

    def is_login_check(self):
        # is_login_url
        if re.match('.*/login.*', self.browser.current_url):
            result = True
        # id of button with text: "忘記帳號？" but not the id for page of "稍後再說"
        # is_forced_login_verify
        elif len(self.browser.find_elements_by_css_selector('#login_link')) > 0:
            result = True
        else:
            result = False

        return result

    def expand_comment(self):
        if not self.post_node:
            return

        self.show_comment()

        if self.should_turn_off_comment_filter:
            self.turn_off_comment_filter()

        if self.should_load_comment:
            self.load_comment(0)
            self.load_comment(1)

    def show_comment(self):
        if not self.is_logined:
            display_comment_selector = '.userContentWrapper [data-testid="UFI2CommentsCount/root"]'
            helper.click_with_move(display_comment_selector, self.browser, timeout=0)
            helper.wait()

    def turn_off_comment_filter(self):
        filter_menu_link_selector = '[data-testid="UFI2ViewOptionsSelector/root"] [data-testid="UFI2ViewOptionsSelector/link"]'
        filter_menu_selector = '[data-testid="UFI2ViewOptionsSelector/menuRoot"]'
        unfiltered_option_selector = '[data-testid="UFI2ViewOptionsSelector/menuRoot"] [data-ordering="RANKED_UNFILTERED"]'

        helper.click_with_move(filter_menu_link_selector, self.browser)
        logger.debug('crawler_timestamp_{}: clicked comment filter button with selector="{}" \n'.format(helper.now(), filter_menu_link_selector))
        helper.move_to_element_by_selector(filter_menu_selector, self.browser)
        logger.debug('crawler_timestamp_{}: comment filter menu is shown with selector="{}" \n'.format(helper.now(), filter_menu_selector))
        helper.click_with_move(unfiltered_option_selector, self.browser)
        logger.debug('crawler_timestamp_{}: clicked comment filter "RANKED_UNFILTERED" with selector="{}" \n'.format(helper.now(), unfiltered_option_selector))

    def load_comment(self, depth, clicked_max_times=50):
        comment_expander_selector = '[data-testid="UFI2CommentsPagerRenderer/pager_depth_{}"]'.format(depth)
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
                        logger.error(helper.print_error(e, cls_html))
                    else:
                        logger.error(helper.print_error(e))
                    is_clicked = helper.click(dialog_close_button, self.browser)

            if not is_clicked:
                empty_count += 1
            else:
                clicked_count += 1

            self.log_crawler(depth, comment_loaders_total, clicked_count, empty_count)
            helper.wait()

        crawled_time = helper.now() - self.start_at
        time_status = '[{}][update_crawler.py - load_comment] Timeout: {}, Crawled: {}. is_timeout={}'.format(helper.now(), self.timeout, crawled_time, self.timeout < crawled_time)
        logger.debug(time_status)