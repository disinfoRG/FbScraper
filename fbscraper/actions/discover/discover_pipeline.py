import logging
logger = logging.getLogger(__name__)
import zlib
from helper import helper
from config import STATUS_SUCCESS


class DiscoverPipeline:
    def __init__(self):
        pass

    def log_pipeline(self, result):
        timestamp = '[{}] pipeline result: {} \n'.format(helper.now(), result)
        logger.debug(timestamp)

    def insert_article(self, db, site_id, article_url):
        article = dict()

        article['first_snapshot_at'] = 0
        article['last_snapshot_at'] = 0
        article['next_snapshot_at'] = -1
        article['snapshot_count'] = 0
        article['url_hash'] = zlib.crc32(article_url.encode())
        article['url'] = article_url
        article['site_id'] = site_id
        article['article_type'] = 'FBPost'
        article['created_at'] = helper.now()
        article['redirect_to'] = None

        article_id = db.insert_article(article)
        self.log_pipeline(f'[{STATUS_SUCCESS}] insert Article #{article_id}')
