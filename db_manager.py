import db
import helper

def get_articles_need_to_update(site_id=None):
    sql_text = None
    now = helper.now()
    if site_id is not None:
        sql_text = 'select * from Article where next_snapshot_at <= {} and article_type="FBPost" and site_id={}'.format(now, site_id)
    else:
        sql_text = 'select * from Article where next_snapshot_at <= {} and article_type="FBPost"'.format(now)
    return db.get_records(sql_text)

def get_article_by_id(id):
    sql_text = 'select * from Article where article_id={}'.format(id)
    return db.get_record(sql_text)

def insert_article_snapshot(s):
    return db.insert_record(s, 'ArticleSnapshot')

def is_article_existed(column, value):
    return db.is_record_existed('Article',column,value)

def get_articles_by_site_id(site_id):
    where = 'site_id={}'.format(site_id)
    return db.get_single_value_of_records_from_table('Article', 'url', where)

def get_sites_need_to_crawl():
    return db.get_fb_page_list()
    # return db.get_sites_need_to_crawl()

def get_fb_page_list():
    try:
        return db.get_fb_page_list()
    except Exception as e:
        helper.print_error(e)
        return None    

def insert_article(article_obj):
    db_article_type = article_obj['article_type']
    article_type_for_insert_article = None

    if db_article_type == 'FBPost':
        article_type_for_insert_article = 'post'
    elif db_article_type == 'FBComment':
        article_type_for_insert_article = 'comment'
    else:
        article_type_for_insert_article = 'article'
    
    try:
        id,_ = db.insert_article(article_obj, article_type_for_insert_article)
        return id
    except Exception as e:
        helper.print_error(e)
        return None

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

def main():
    a_list = get_articles_need_to_update(94)
    print('hold')
if __name__ == "__main__":
    main()