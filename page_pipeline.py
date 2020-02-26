import zlib
import time
from helper import helper


class PagePipeline:
    def __init__(self, post_urls, site_id, db_manager, logfile):
        self.post_urls = post_urls
        self.db_manager = db_manager
        self.site_id = site_id
        self.logfile = logfile

    def pipe(self):
        for p_url in self.post_urls:
            if self.is_post_existed(p_url):
                continue
            self.write_post(p_url)

    def is_post_existed(self, url):
        # select count(*) from FBPostSnapshot where url=post['url']
        return self.db_manager.is_article_existed('url_hash', zlib.crc32(url.encode()))

    def log_pipeline(self, db_table, db_id, data):
        timestamp = 'pipeline_timestamp_{}: insert to database, table = {}, id = {}, data = {} \n'.format(helper.now(), db_table, db_id, data)
        self.logfile.write(timestamp)

    def write_post(self, url):
        p = dict()

        p['first_snapshot_at'] = 0
        p['last_snapshot_at'] = 0
        p['next_snapshot_at'] = -1
        p['snapshot_count'] = 0
        p['url_hash'] = zlib.crc32(url.encode())
        p['url'] = url
        p['site_id'] = self.site_id
        p['article_type'] = 'FBPost'
        p['created_at'] = int(time.time())
        p['redirect_to'] = None

        db_id = self.db_manager.insert_article(p)
        self.log_pipeline('Article', db_id, p)


def main():
    import db_manager
    parsed = ['https://www.facebook.com/watchout.tw/posts/1469132613244947', 'https://www.facebook.com/watchout.tw/posts/1469027029922172']
    pipeline = PagePipeline(parsed, 75, db_manager)
    pipeline.pipe()
    print('pause')


if __name__ == "__main__":
    main()

        
 

