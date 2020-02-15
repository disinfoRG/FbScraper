import re
from helper import helper

def get_post_url(post):
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
