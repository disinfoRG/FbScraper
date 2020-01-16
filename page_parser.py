from bs4 import BeautifulSoup
import re
import helper
import page_parser_helper as ppa_helper

class PageParser:
    def __init__(self, raw_html):
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
        p['url'] = ppa_helper.get_post_url(post)
        return p

def main():
    import json

    page = None
    fname = 'site_74_posts_5_snapshotAt_1578891269.json'
    with open(fname,'r') as f:
        page = json.load(f)

    ppa = PageParser(page['raw_html'])
    parsed = ppa.parse()
    return parsed

if __name__ == "__main__":
    main()

        
 
