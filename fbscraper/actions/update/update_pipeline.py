import logging
logger = logging.getLogger(__name__)
from helper import helper
from config import STATUS_SUCCESS, DEFAULT_NEXT_SNAPSHOT_AT_INTERVAL


def log_pipeline(result):
    timestamp = '[{}] pipeline result: {} \n'.format(helper.now(), result)
    logger.debug(timestamp)


def update_article(db, article_id, raw_data):
    snapshot_at = helper.now()
    snapshot_article(db, snapshot_at, article_id, raw_data)
    refresh_article_snapshot_history(db, article_id, snapshot_at)


def snapshot_article(db, snapshot_at, article_id, raw_data):
    snapshot = dict()
    snapshot['snapshot_at'] = snapshot_at
    snapshot['raw_data'] = raw_data
    snapshot['article_id'] = article_id
    db.insert_article_snapshot(snapshot)
    log_pipeline(f'[{STATUS_SUCCESS}] insert ArticleSnapshot #{article_id}')


def refresh_article_snapshot_history(db, article_id, snapshot_at):
    article = dict()
    original_article = db.get_article_by_id(article_id=article_id)

    article['article_id'] = article_id
    article['last_snapshot_at'] = snapshot_at
    article['next_snapshot_at'] = snapshot_at + DEFAULT_NEXT_SNAPSHOT_AT_INTERVAL
    article['snapshot_count'] = original_article['snapshot_count']+1
    if original_article['first_snapshot_at'] == 0:
        article['first_snapshot_at'] = snapshot_at
    else:
        article['first_snapshot_at'] = original_article['first_snapshot_at']
    db.update_article(**article)
    log_pipeline(f'[{STATUS_SUCCESS}] update Article #{article_id} after ArticleSnapshot inserted')
