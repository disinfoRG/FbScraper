from post_spider import PostSpider
import argparse
import helper
import db_manager

def update_all(browser):
    articles = db_manager.get_articles_need_to_update(94)
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
        article = dict()
        article['article_id'] = 13491
        article['url'] = 'https://www.facebook.com/hsiweiC/posts/480714952637723'
        update_one(article, browser)

if __name__ == '__main__':
    main()
