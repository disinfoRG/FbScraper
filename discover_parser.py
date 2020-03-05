from bs4 import BeautifulSoup
import re
from helper import helper

class DiscoverParser:
    def __init__(self, raw_html=None):
        if raw_html:
            self.set_soup(raw_html)

    def set_soup(self, raw_html):
        self.soup = BeautifulSoup(raw_html, 'html.parser')

    def get_post_urls(self, raw_html=None):
        if raw_html:
            self.set_soup(raw_html)
        post_elements = self.soup.find_all('div', {'class': 'userContentWrapper'})
        return [self.get_post_url(post) for post in post_elements]

    def get_post_url(self, post):
        result = None
        anchors = post.select('[data-testid="story-subtitle"] a')
        url_info = None
        for index, anchor in enumerate(anchors):
            hasTimestamp = len(anchor.select('abbr > span.timestampContent')) > 0

            if (hasTimestamp):
                url = anchor.get('href')
                if url:
                    url_info = helper.get_facebook_url_info(url)
                    if url_info['permalink']:
                        result = url_info['permalink']
                        break
                    elif url_info['original_url']:
                        result = url_info['original_url']
            
        return result

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

        
 
