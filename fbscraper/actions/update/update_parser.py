from bs4 import BeautifulSoup


def get_post_raw_html(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')

    if len(soup.select('.permalinkPost')) > 0:
        result = str(soup.select('.permalinkPost')[0])
    elif len(soup.select('.userContentWrapper')) > 0:
        result = str(soup.select('.userContentWrapper')[0])
    else:
        # return whole page's html if cannot locate post node
        # ex. failed for non-existing article: https://www.facebook.com/fuqidao168/posts/2466415456951685
        # ex. failed for some video post: https://www.facebook.com/znk168/posts/412649276099554
        result = page_source

    return result


if __name__ == '__main__':
    from helper import helper
    from config import fb
    fb.start(False)
    post_url = 'https://www.facebook.com/eatnews/posts/468883017163473'
    fb.driver.get(post_url)
    helper.wait()
    parsed_post = get_post_raw_html(fb.driver.page_source)



