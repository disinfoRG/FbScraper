import zlib
import helper

STATUS_SUCCESS = 'SUCCESS'
STATUS_FAILED = 'FAILED'

class PostPipeline():
    def __init__(self, post_urls, article_id, db_manager, logfile, next_snapshot_at_interval=3600):
        self.post_urls = post_urls
        self.db_manager = db_manager
        self.article_id = article_id
        self.snapshot_at = None
        self.next_snapshot_at_interval = next_snapshot_at_interval
        self.logfile = logfile

    def log_pipeline(self, db_action, db_table, db_id, result, status):
        timestamp = '[pipeline_timestamp_{}] status: {}, database action: {}, table: {}, id: {}, result: {} \n'.format(helper.now(), status, db_action, db_table, db_id, result)
        self.logfile.write(timestamp)

    def pipe(self):
        for p_url in self.post_urls:
            if self.is_post_existed(p_url):
                continue
            self.write_post(p_url)         

    def pipe_single_post_raw_data(self, raw_data):
        self.snapshot_at = helper.now()
        self.snapshot_article(raw_data)
        self.update_article()

    def is_post_existed(self, url):
        # select count(*) from FBPostSnapshot where url=post['url']
        return self.db_manager.is_article_existed('url_hash', zlib.crc32(url.encode()))

    def snapshot_article(self, raw_data):
        sa = {}
        sa['snapshot_at'] = self.snapshot_at
        sa['raw_data'] = raw_data
        sa['article_id'] = self.article_id

        db_id = None
        try:
            db_id = self.db_manager.insert_article_snapshot(sa)
            self.log_pipeline('insert', 'ArticleSnapshot', db_id, sa, STATUS_SUCCESS)
        except Exception as e:
            self.log_pipeline('insert', 'ArticleSnapshot', db_id, helper.print_error(e), STATUS_FAILED)

    def update_article(self):
        article_id = self.article_id

        try:
            p = {}
            snapshot_at = self.snapshot_at
            article = self.db_manager.get_article_by_id(article_id)

            if article['first_snapshot_at'] == 0:
                p['first_snapshot_at'] = snapshot_at
            p['last_snapshot_at'] = snapshot_at
            p['next_snapshot_at'] = snapshot_at + self.next_snapshot_at_interval
            p['snapshot_count'] = article['snapshot_count'] + 1
            p['article_id'] = article_id
            
            self.db_manager.update_article(p)
            self.log_pipeline('update', 'Article', article_id, p, STATUS_SUCCESS)
        except Exception as e:
            self.log_pipeline('update', 'Article', article_id, helper.print_error(e), STATUS_FAILED)
        
    def write_post(self, post):
        p = {}
        p['article_id'] = self.article_id
        p['snapshot_at'] = self.snapshot_at
        p['raw_data'] = self.raw_html
        p['author'] = parsed['author']
        p['shared_url'] = parsed['shared_url']
        p['reactions'] = parsed['reactions']
        p['fb_post_info'] = parsed['fb_post_info']
        p['author_info'] = parsed['author_info']
        self.db_manager.insert_post(p)

def main():
    import db_manager
    from logger import Logger

    fpath = 'test_post_pipeline_{}.log'.format(helper.now())
    logfile = Logger(open(fpath, 'a', buffering=1))
    pipeline = PostPipeline([], 1426, db_manager, logfile)
    raw_data = 'sssaAAAAaaa'
    pipeline.pipe_single_post_raw_data(raw_data)
    print('pause')

if __name__ == "__main__":
    main()

        
 

