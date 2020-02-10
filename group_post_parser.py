from bs4 import BeautifulSoup
import time
import re
from random import uniform


class PostParser:
    def __init__(self, fb_browser, post_url):
        self.post_url = post_url
        self.fb_browser = fb_browser
        self.fb_browser.driver.get(post_url)
        time.sleep(uniform(2, 4))
        self.post_html = self.fb_browser.driver.page_source

        self.soup = BeautifulSoup(self.post_html, 'html.parser')

    def get_post_id(self):
        if 'story_fbid' in self.post_url:
            post_id = re.search('story_fbid=(\d+)', self.post_url).group(1)
        else:
            post_id = self.post_url.strip('/').split('/')[-1]
        return post_id

    def get_post_type(self):
        if 'posts' in self.post_url:
            post_type = 'post'
        elif 'videos' in self.post_url:
            post_type = 'video'
        elif 'story_fbid' in self.post_url:
            post_type = 'story'
        elif 'photos' in self.post_url:
            post_type = 'photo'
        else:
            post_type = 'unknown'

        return post_type

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

    def get_reactions(self):
        reactions = dict()
        # comment count
        comment_count_str = self.soup.find('a', {'data-testid': 'UFI2CommentsCount/root'}).text
        comment_count = re.search('(\d+)', comment_count_str).group(1)
        reactions["comments"] = int(comment_count)

        # share count
        share_count_str = self.soup.find('a', {'data-testid': 'UFI2SharesCount/root'}).text
        share_count = re.search('(\d+)', share_count_str).group(1)
        reactions["shares"] = int(share_count)

        # sticker reactions
        reaction_btn = self.fb_browser.driver.find_element_by_class_name('_81hb')
        self.fb_browser.driver.execute_script('arguments[0].click()', reaction_btn)
        time.sleep(5)
        reaction_ele = self.fb_browser.driver.find_element_by_css_selector('ul[defaultactivetabkey="all"')
        reaction_texts = [x.get_attribute('aria-label') for x in reaction_ele.find_elements_by_css_selector('span[aria-label]')]
        index_of_total = [i for i, t in enumerate(reaction_texts) if '心情' in t][0]
        total_count_str = re.search('(\d+)', reaction_texts[index_of_total]).group(1)
        reactions["reactions"] = int(total_count_str)

        reaction_ch_to_eng = {"讚": "like", "大心": "love", "哈": "haha", "哇": "wow", "怒": "anger"}
        for t in reaction_texts[index_of_total+1:]:
            for k in reaction_ch_to_eng:
                if k in t:
                    count_str = re.search('(\d+)', t).group(1)
                    reactions[reaction_ch_to_eng[k]] = int(count_str)
                    reaction_ch_to_eng.pop(k)
                    break

        # close reaction panel
        close_btn = self.fb_browser.driver.find_element_by_css_selector('a[data-testid="reactions_profile_browser:close"]')
        self.fb_browser.driver.execute_script('arguments[0].click()', close_btn)

        return reactions


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
        c['url'] = ppa_helper.get_comment_url(comment)
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


if __name__ == '__main__':
    from config import fb
    fb.start()
    post_url = 'https://www.facebook.com/eatnews/posts/468883017163473'
    p = PostParser(fb, post_url)
    parsed_post = p.parse()



