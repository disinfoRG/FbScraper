import zlib
import time

def get_merged_item(item, db_row):
    return {**item, **db_row}

def get_article(item, article_type='post'):
    article = {}
    
    item_url = item['url']
    url = item_url
    url_hash = zlib.crc32(item_url.encode())
    site_id = item['site_id']
    first_snapshot_at = item['first_snapshot_at']
    last_snapshot_at = item['last_snapshot_at']
    next_snapshot_at = item['next_snapshot_at']
    redirect_to = item['redirect_to']
    snapshot_count = item['snapshot_count']

    if article_type == 'post':
        article['article_type'] = 'FBPost'
    elif article_type == 'comment':
        article['article_type'] = 'FBComment'
    article['site_id'] = site_id
    article['url'] = url
    article['url_hash'] = url_hash
    article['first_snapshot_at'] = first_snapshot_at
    article['last_snapshot_at'] = last_snapshot_at
    article['next_snapshot_at'] = next_snapshot_at
    article['redirect_to'] = redirect_to
    article['snapshot_count'] = snapshot_count
    article['created_at'] = int(time.time())

    return article

def get_fb_snapshot(item, snapshot_type='post'):
    article_id = item['article_id']
    snapshot_at = item['last_snapshot_at']
    raw_data = item['raw_data']
    author = item['author']['permanent_id']
    author_info = item['author']
    reactions = {k.lower():v for k, v in item['reaction'].items()}
    reactions['reactions'] = reactions.pop('total', None)

    snapshot = {
        'author_info': author_info,
        'article_id': article_id,
        'snapshot_at': snapshot_at,
        'raw_data': raw_data,
        'author': author,
        'reactions': reactions,
    }

    if snapshot_type == 'post':
        fb_post_info = {
            'id': item['id'],
            'type': item['type'],
            'content': item['content'],
        }
        snapshot['fb_post_info'] = fb_post_info

        snapshot['shared_url'] = item['url']
        snapshot['reactions']['shares'] = item['share']
        snapshot['reactions']['comments'] = item['comment']
    elif snapshot_type == 'comment':
        fb_comment_info = {
            'id': item['id'],
            'content': item['content'],
        }
        snapshot['fb_comment_info'] = fb_comment_info

        snapshot['reply_to'] = item['reply_to_article_id']

    return snapshot