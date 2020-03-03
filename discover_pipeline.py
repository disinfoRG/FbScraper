import zlib
from helper import helper
from config import STATUS_SUCCESS

class DiscoverPipeline:
    def __init__(self, site_id, db, logfile):
        self.site_id = site_id
        self.db = db
        self.logfile = logfile

    def log_pipeline(self, result):
        timestamp = '[{}] pipeline result: {} \n'.format(helper.now(), result)
        self.logfile.write(timestamp)

    def insert_article(self, article_url):
        article = dict()

        article['first_snapshot_at'] = 0
        article['last_snapshot_at'] = 0
        article['next_snapshot_at'] = -1
        article['snapshot_count'] = 0
        article['url_hash'] = zlib.crc32(article_url.encode())
        article['url'] = article_url
        article['site_id'] = self.site_id
        article['article_type'] = 'FBPost'
        article['created_at'] = helper.now()
        article['redirect_to'] = None

        article_id = self.db.insert_article(article)
        self.log_pipeline(f'[{STATUS_SUCCESS}] insert Article #{article_id}')

def main():
    import db_manager
    parsed = ['https://www.facebook.com/watchout.tw/posts/1469132613244947', 'https://www.facebook.com/watchout.tw/posts/1469027029922172']
    pipeline = DiscoverPipeline(parsed, 75, db_manager)
    pipeline.pipe()
    print('pause')


if __name__ == "__main__":
    main()

        
 

