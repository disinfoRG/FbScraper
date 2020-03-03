from bs4 import BeautifulSoup
import time
import re
from random import uniform


class UpdateParser:
    def __init__(self, raw_html=None):
        if raw_html:
            self.set_soup(raw_html)

    def set_soup(self, raw_html):
        self.soup = BeautifulSoup(raw_html, 'html.parser')
    
    def get_post_raw_html(self, page_source=None):
        if page_source:
            self.set_soup(page_source)

        try:
            selector = '.permalinkPost'
            raw_html = str(self.soup.select(selector)[0])
            return raw_html
        except:
            pass

        try:
            selector = '.userContentWrapper'
            raw_html = str(self.soup.select(selector)[0])
            return raw_html
        except:
            pass

        # return whole page's html if cannot locate post node  
        # ex. failed for non-existing article: https://www.facebook.com/fuqidao168/posts/2466415456951685
        # ex. failed for some video post: https://www.facebook.com/znk168/posts/412649276099554        
        return page_source

if __name__ == '__main__':
    from helper import helper
    from config import fb
    fb.start(False)
    post_url = 'https://www.facebook.com/eatnews/posts/468883017163473'
    fb.driver.get(post_url)
    helper.wait()
    parser = UpdateParser()
    parsed_post = parser.get_post_raw_html(fb.driver.page_source)
    print()



