import logging
logger = logging.getLogger(__name__)
import zlib
from helper import helper
from config import STATUS_SUCCESS, DEFAULT_NEXT_SNAPSHOT_AT_INTERVAL

class UpdatePipeline():
    def __init__(self, article_id, db, next_snapshot_at_interval=DEFAULT_NEXT_SNAPSHOT_AT_INTERVAL):
        self.db = db
        self.article_id = article_id
        self.snapshot_at = None
        self.next_snapshot_at_interval = next_snapshot_at_interval

    def log_pipeline(self, result):
        timestamp = '[{}] pipeline result: {} \n'.format(helper.now(), result)
        logger.debug(timestamp)

    def update_article(self, raw_data):
        self.snapshot_at = helper.now()
        self.snapshot_article(raw_data)
        self.refresh_article_snapshot_history()

    def snapshot_article(self, raw_data):
        snapshot = dict()
        snapshot['snapshot_at'] = self.snapshot_at
        snapshot['raw_data'] = raw_data
        snapshot['article_id'] = self.article_id
        self.db.insert_article_snapshot(snapshot)
        self.log_pipeline(f'[{STATUS_SUCCESS}] insert ArticleSnapshot #{self.article_id}')

    def refresh_article_snapshot_history(self):
        article = dict()
        original_article = self.db.get_article_by_id(article_id=self.article_id)

        article['article_id'] = self.article_id
        article['last_snapshot_at'] = self.snapshot_at
        article['next_snapshot_at'] = self.snapshot_at + self.next_snapshot_at_interval
        article['snapshot_count'] = original_article['snapshot_count']+1
        if original_article['first_snapshot_at'] == 0:
            article['first_snapshot_at'] = self.snapshot_at
        else:
            article['first_snapshot_at'] = original_article['first_snapshot_at']
        self.db.update_article(**article)
        self.log_pipeline(f'[{STATUS_SUCCESS}] update Article #{self.article_id} after ArticleSnapshot inserted')
