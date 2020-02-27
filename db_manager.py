import db
from helper import helper
import os
from config import PAGE_SITE_TYPE, GROUP_SITE_TYPE


def get_rows_by_table(table, where):
    try:
        return db.get_table_rows(table, where)
    except Exception as e:
        helper.print_error(e)
        return None 


def get_articles_never_update(site_type, site_id=None, amount=None):
    sql_text = None
    if site_id is not None:
        sql_text = 'select * from Article where snapshot_count=0 and article_type="FBPost" and site_id={}'.format(site_id)
    else:
        sql_text = 'select * from Article where snapshot_count=0 and article_type="FBPost"'

    if amount is not None:
        sql_text = '{} limit {}'.format(sql_text, amount)

    return db.get_records(sql_text)


def get_article_by_id(id):
    sql_text = 'select * from Article where article_id={}'.format(id)
    return db.get_record(sql_text)


def get_sites_need_to_crawl_by_ids(ids):
    ids_text = ', '.join(str(id) for id in ids)
    sql_text = 'select * from Site where site_id in ({})'.format(ids_text)
    return db.get_records(sql_text)    

def get_sites_tagged_need_to_discover():
    where_text = 'is_active = 1 and type = "fb_page"'
    sql_text = 'select * from Site where {}'.format(where_text)
    return db.get_records(sql_text)

def get_articles_tagged_need_to_update():
    now = helper.now()
    sql_text = 'select * from Article where next_snapshot_at <= {} and article_type="FBPost"'.format(now)
    return db.get_records(sql_text)    


def insert_article_snapshot(s):
    return db.insert_record(s, 'ArticleSnapshot')


def is_article_existed(column, value):
    return db.is_record_existed('Article',column,value)


def get_sites_need_to_crawl(site_type='fb_page', amount=None):
    sql_text = None
    sql_text = 'select * from Site where is_active=1 and type="{}"'.format(site_type)

    if amount is not None:
        sql_text = '{} limit {}'.format(sql_text, amount)

    return db.get_records(sql_text)


def insert_post(post_obj, also_insert_article=False):
    if also_insert_article:
        try:
            return db.insert_post(post_obj)
        except Exception as e:
            helper.print_error(e)
            return None
    try:
        return db.insert_record(post_obj, 'FBPostSnapshot')
    except Exception as e:
        helper.print_error(e)
        return None            
    

def insert_comment(comment_obj):
    try:
        return db.insert_comment(comment_obj)
    except Exception as e:
        helper.print_error(e)
        return None


def update_page(page_obj):
    try:
        return db.update_page(page_obj)
    except Exception as e:
        helper.print_error(e)
        return None


def update_article(article_obj):
    kv_pairs = []
    for k, v in article_obj.items():
        if k == 'article_id':
            continue
        kv = '{}={}'.format(k,v)
        kv_pairs.append(kv)
    key_value = ', '.join(str(x) for x in kv_pairs)
    
    where = 'article_id = {}'.format(article_obj['article_id'])
    sql_text = 'update Article set {} where {}'.format(key_value, where)
    return db.execute_sql(sql_text)