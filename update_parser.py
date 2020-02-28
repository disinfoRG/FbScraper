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

    def get_publish_time(self):
        publish_time = self.soup.find('abbr', {'class': 'livetimestamp'})['data-utime']
        return publish_time

    def get_post_author(self):
        author_element = self.soup.find('span', {'class': 'fwb fcg'}).find('a')
        author_id = re.search('id=(\d+)', author_element['data-hovercard']).group(1)
        author_display_name = author_element.text
        return {'permenant_id': author_id, 'displayed_name': author_display_name}

    def get_post_content(self):
        try:
            content_text = self.soup.find('div', {'data-testid': 'post_message'}).text
            content_text = ' '.join(content_text.split())
        except AttributeError:
            content_text = ''
        return content_text

    def get_comments(self):
        comments = []

        c_sel_zero_level = helper.data_testidify('UFI2Comment/root_depth_{}'.format(0))
        c_sel_first_level = helper.data_testidify('UFI2Comment/root_depth_{}'.format(1))

        for c_node in self.soup.select(c_sel_zero_level):
            c = self.get_comment_info(c_node)
            comments.append(c)

        for c_node in self.soup.select(c_sel_first_level):
            c = self.get_comment_info(c_node)
            comments.append(c)

        return comments

    def get_comment_info(self, comment):
        c = {}
        c['url'] = self.get_comment_url(comment)
        c['raw_html'] = str(comment)
        return c

    def parse(self):
        fb_post_details = {'content': self.get_post_content(),
                           'type': self.get_post_type(),
                           'id': self.get_post_id(),
                           'publish_at': self.get_publish_time()}

        author_info = self.get_post_author()

        post_infos = {'snapshot_at': int(time.time()),
                      'raw_data': self.post_html,
                      'shared_url': self.post_url,
                      'reactions': self.get_reactions(),
                      'author_info': author_info,
                      'author': author_info['permenant_id'],
                      'fb_post_info': fb_post_details,
                      }

        return post_infos
    
    def get_comment_url(self, comment_node):
        permalink_node = None
        permalink_href = None
        
        url_selector = helper.data_testidify('UFI2CommentActionLinks/root')
        url_nodes = comment_node.select(url_selector)

        try:
            permalink_node = url_nodes[0].select('li:nth-child(3) > a')
            permalink_href = permalink_node[0].get('href')
        except NoSuchElementException:
            # url_node.get_attribute('innerHTML')
            # '<li class="_6coj"><span aria-hidden="true" class="_6cok">&nbsp;·&nbsp;</span><a class="_6qw7" data-ft="{&quot;tn&quot;:&quot;N&quot;}" href="https://www.facebook.com/eatnews/posts/470559583662483?comment_id=470610556990719"><abbr data-tooltip-content="2020年1月1日 星期三下午1:51" data-hover="tooltip" minimize="true" class="livetimestamp" data-utime="1577857868" data-minimize="true">1天</abbr></a></li>'
            # selenium.common.exceptions.NoSuchElementException: Message: no such element: Unable to locate element: {"method":"css selector","selector":"li:nth-child(3) > a"}
            # 'https://www.facebook.com/eatnews/posts/470559583662483?comment_id=470610556990719'
            permalink_href = url_nodes[0].select('a')[0].get('href')
        except Exception as e:
            Helper.print_error(e)
            pass

        return permalink_href


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



