from bs4 import BeautifulSoup
import re
from helper import helper

class DiscoverParser:
    def __init__(self, raw_html=None):
        if raw_html:
            self.set_soup(raw_html)

    def set_soup(self, raw_html):
        self.soup = BeautifulSoup(raw_html, 'html.parser')

    def parse(self):
        parsed = {}
        parsed['posts'] = self.get_posts()
        parsed['comments'] = self.get_comments()
        return parsed

    def get_posts(self):
        posts = []
        for post_node in self.soup.select('.userContentWrapper'):
            p = self.get_post_info(post_node)
            posts.append(p)
        return posts

    def get_post_info(self, post):
        p = {}
        p['url'] = self.get_post_url(post)
        return p

    def get_post_urls(self, raw_html=None):
        if raw_html:
            self.set_soup(raw_html)
        post_elements = self.soup.find_all('div', {'class': 'userContentWrapper'})
        return [self.get_post_url(post) for post in post_elements]

    def get_post_url(self, post):
        anchors = post.select('[data-testid="story-subtitle"] a')
        url_info = None
        for index, anchor in enumerate(anchors):
            try:
                hasTimestamp = anchor.select('abbr > span.timestampContent')

                if (hasTimestamp):
                    url = anchor.get('href')
                    url_info = helper.get_facebook_url_info(url)
                    if url_info['permalink'] is not None:
                        return url_info['permalink']
                    elif url_info['original_url'] is not None:
                        return url_info['original_url']
                    pass
            except:
                pass
            
        return None


def main():
    import json

    page = None
    fname = 'site_74_posts_5_snapshotAt_1578891269.json'
    with open(fname,'r') as f:
        page = json.load(f)

    ppa = DiscoverParser(page['raw_html'])
    parsed = ppa.parse()
    return parsed

if __name__ == "__main__":
    main()

        
 
