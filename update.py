from post_spider import PostSpider
import argparse
import helper
import db_manager

def update_all(browser):
    articles = db_manager.get_articles_need_to_update()
    for a in articles:
        try:
            update_one(a, browser)
        except Exception as e:
            helper.print_error(e)

def update_one(article, browser):
    article_id = article['article_id']
    article_url = article['url']
    ps = PostSpider(article_url, article_id, browser)
    ps.work()

def test(browser):
    article = dict()
    article['article_id'] = 14259
    article['url'] = 'https://www.facebook.com/znk168/posts/412649276099554'
    # article['url'] = 'https://www.facebook.com/185537762220181/posts/2426555417632575'
    update_one(article, browser)

def main():
    from config import fb
    fb.start()
    browser = fb.driver

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--all', action='store_true',
                        help='update all posts in db')
    args = parser.parse_args()
    if args.all:
        update_all(browser)
    else:
        test(browser)

if __name__ == '__main__':
    main()
