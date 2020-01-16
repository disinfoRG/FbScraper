import helper

class PostCrawler:
    def __init__(self, url, browser, write_to_db):
        self.url = helper.get_clean_url(url)
        self.browser = browser
        self.post_node = None
        self.write_to_db = write_to_db
    def crawl(self):
        self.enter_site()
        self.locate_target_post()
        self.expand_comment()
        raw_html = self.get_raw_html()
        self.write_to_db(raw_html)
    def get_raw_html(self):
        # return self.browser.page_source # failed for https://www.facebook.com/znk168/posts/412649276099554
        return helper.get_html(self.post_node)
    def enter_site(self):
        post_root_url = self.url
        self.browser.get(post_root_url)
        helper.wait()
    def locate_target_post(self):
        self.post_node = helper.get_element(self.browser, '.permalinkPost')
    def expand_comment(self):
        self.turn_off_comment_filter()
        self.load_comment(0,3)
        self.load_comment(1,3)
    def turn_off_comment_filter(self):
        c_filter_buttons = self.post_node.find_elements_by_css_selector('[data-testid="UFI2ViewOptionsSelector/root"]')
        for cfb in c_filter_buttons:
            helper.click(cfb, self.browser)
            helper.wait()
            c_filter_menu = helper.get_element(self.browser, '[data-testid="UFI2ViewOptionsSelector/menuRoot"]')
            helper.wait()
            c_no_filter = helper.get_element(c_filter_menu, '[data-ordering="RANKED_UNFILTERED"]')
            helper.click(c_no_filter, self.browser)
            helper.wait()
    def load_comment(self, depth, check_times):
        comment_expander_selector = '[data-testid="UFI2CommentsPagerRenderer/pager_depth_{}"]'.format(depth)
        count = 0
        while count < check_times:
            comment_loaders = self.post_node.find_elements_by_css_selector(comment_expander_selector)
            if len(comment_loaders) > 0:
                for c_loader in comment_loaders:
                    # print(c_loader.get_attribute('innerText'))
                    helper.click(c_loader, self.browser)
                    helper.wait()
            count += 1
            helper.wait()