from bs4 import BeautifulSoup
from helper import helper


class DiscoverParser:
    def __init__(self):
        pass

    def get_post_urls(self, raw_html):
        soup = BeautifulSoup(raw_html, 'html.parser')
        post_elements = soup.find_all('div', {'class': 'userContentWrapper'})
        return [self.get_post_url(post) for post in post_elements]

    @staticmethod
    def get_post_url(post):
        result = None
        anchors = post.select('[data-testid="story-subtitle"] a')
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

    fname = 'site_74_posts_5_snapshotAt_1578891269.json'
    with open(fname,'r') as f:
        page = json.load(f)

    ppa = DiscoverParser()
    post_urls = ppa.get_post_urls(page['raw_html'])
    return post_urls


if __name__ == "__main__":
    main()
