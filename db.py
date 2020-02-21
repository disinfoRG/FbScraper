import sqlalchemy as db
from sqlalchemy.sql import text
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.sql import and_, or_, not_

# self-defined
import db_helper
from settings import DB_URL
from helper import helper

def connect_to_db():
    engine = create_engine(DB_URL)
    connection = engine.connect()
    metadata = MetaData()
    metadata.reflect(bind=engine)
    return engine, connection, metadata.tables

engine, connection, tables = connect_to_db()

def get_table_rows(table_name, where=None):
    table = tables[table_name] 
    query = table.select()
    if where is not None:
        whereclause = text(where)
        query = query.where(whereclause)
    
    items = [dict(x) for x in connection.execute(query).fetchall()]

    return items    



def is_record_existed(table,column,value):
    query = 'select count(*) from {}'.format(table)
    where = '{} = "{}"'.format(column, value)
    textual_sql = '{} where {}'.format(query,where)
    stmt = text(textual_sql)
    exec = connection.execute(stmt)
    count = exec.scalar()
    
    if count > 0:
        return True
    return False

def get_single_value_of_records_from_table(table, column, where):
    query = 'select {} from {}'.format(column, table)
    textual_sql = '{} where {}'.format(query, where)
    stmt = text(textual_sql)
    exe = connection.execute(stmt)
    return [dict(x)[column] for x in exe.fetchall()]

def get_records(textual_sql):
    stmt = text(textual_sql)
    exe = connection.execute(stmt)
    result = [dict(x) for x in exe.fetchall()]
    connection.connection.commit()
    return result

def get_record(textual_sql):
    stmt = text(textual_sql)
    exe = connection.execute(stmt)
    result = dict(exe.fetchone())
    connection.connection.commit()
    return result

def execute_sql(textual_sql):
    stmt = text(textual_sql)
    exe = connection.execute(stmt)

def get_sites_need_to_crawl():
    where_next_snapshot_at = 'JSON_EXTRACT(site_info, "$.next_snapshot_at") <= {}'.format(helper.now())
    where_first_snapshot_at = 'JSON_EXTRACT(site_info, "$.first_snapshot_at") = null'
    query = 'select site_id, url from Site'
    textual_sql = '{} where {} or {}'.format(query, where_next_snapshot_at, where_first_snapshot_at)
    stmt = text(textual_sql)
    exe = connection.execute(stmt)
    return [dict(x) for x in exe.fetchall()]

def get_site_list(site_type):
    # select * from Site where is_active=1 and type='fb_page';
    site_table = tables["Site"]
    query = db.select([site_table.c.site_id, site_table.c.name, site_table.c.url]).where(
        db.and_(
            site_table.c.is_active == 1,
            site_table.c.type == site_type,
        )        
    )
    site_infos = [dict(x) for x in connection.execute(query).fetchall()]

    return site_infos

def update_page(item):
    table_site = tables['Site']
    site_id = item['site_id']
    whereclause = text('site_id = {}'.format(site_id))
    query = db.update(table_site, whereclause)
    site_info = item['author']
    values = {
        'site_info': site_info,
    }
    exe = connection.execute(query, values)
    return site_id    

def get_safe_value(v):
    try:
        return text(v)
    except:
        return v

def insert_record(record, table):
    query = db.insert(tables[table])
    # safe_record = {}

    # for k, v in record.items():
    #     safe_record[k] = get_safe_value(v)

    exe = connection.execute(query, record)
    return exe.inserted_primary_key

def insert_article(item, article_type):
    query = db.insert(tables['Article'])
    article = db_helper.get_article(item, article_type)
    exe = connection.execute(query, article)
    article['article_id'] = exe.inserted_primary_key
    return (article['article_id'], db_helper.get_merged_item(item, article))

def insert_post(item):
    id, merged_item = insert_article(item, 'post')
    insert_fb_post_snapshot(merged_item)
    return id

def insert_comment(item):
    id, merged_item = insert_article(item, 'comment')
    insert_fb_comment_snapshot(merged_item)   
    return id

def insert_fb_post_snapshot(merged_item):
    query = db.insert(tables['FBPostSnapshot'])
    snapshot = db_helper.get_fb_snapshot(merged_item, 'post')
    exe = connection.execute(query, snapshot)
 
def insert_fb_comment_snapshot(merged_item):
    query = db.insert(tables['FBCommentSnapshot'])
    snapshot = db_helper.get_fb_snapshot(merged_item, 'comment')
    exe = connection.execute(query, snapshot)

def main():
    table = 'Article'
    column = 'url'
    where = 'site_id={}'.format(75)
    values = get_single_value_of_records_from_table(table,column,where)
    print('hold')

    a_id = 2300
    where = 'article_id > {}'.format(a_id)
    a_list = get_table_rows('Article', where)
    print('hold')

if __name__ == "__main__":
   main() 