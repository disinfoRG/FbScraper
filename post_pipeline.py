import zlib
import helper

class PostPipeline():
    def __init__(self, post_urls, article_id, db_manager, next_snapshot_at_interval=3600):
        self.post_urls = post_urls
        self.db_manager = db_manager
        self.article_id = article_id
        self.snapshot_at = None
        self.next_snapshot_at_interval = next_snapshot_at_interval
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
        self.db_manager.insert_article_snapshot(sa)

    def update_article(self):
        p = {}
        snapshot_at = self.snapshot_at
        article = self.db_manager.get_article_by_id(self.article_id)

        if article['first_snapshot_at'] == 0:
            p['first_snapshot_at'] = snapshot_at
        p['last_snapshot_at'] = snapshot_at
        p['next_snapshot_at'] = snapshot_at + self.next_snapshot_at_interval
        p['snapshot_count'] = article['snapshot_count'] + 1
        p['article_id'] = self.article_id
        
        self.db_manager.update_article(p)
    
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
    parsed = ['https://www.facebook.com/watchout.tw/posts/1469132613244947', 'https://www.facebook.com/watchout.tw/posts/1469027029922172']
    pipeline = PagePipeline(parsed, 75, db_manager)
    pipeline.pipe()
    print('pause')

if __name__ == "__main__":
    main()

        
 

