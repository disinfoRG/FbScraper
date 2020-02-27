import requests
import json
from tqdm import tqdm

# self-defined
import db_manager as dbm
from helper import helper
from settings import AIRTABLE_API_KEY

headers = {
   'authorization': 'Bearer {}'.format(AIRTABLE_API_KEY),
   'content-type': 'application/json'
}

summary_table_lookup = {
    'Site': ['recmeI4nlHaM43xg9'],
    'Article': ['recjf05FCnMWjZ0qX'],
    'FBPostSnapshot': ['recQreiLjFlGYCR1E'],
    'FBCommentSnapshot': ['rec45ZLNdVgDmoFic'],
}

json_columns_lookup = {
    'Site': ['config', 'site_info'],
    'Article': [],
    'FBPostSnapshot': ['author_info', 'reactions', 'fb_post_info'],
    'FBCommentSnapshot': ['author_info', 'reactions', 'fb_comment_info'],
}

def get_latest_id(table):
    url = 'https://api.airtable.com/v0/app6uF2BLO7AdMQvn/{}_Summary?fields%5B%5D=latest_id&filterByFormula=SEARCH(%22{}%22%2Ctable)'.format(table, table)
    try:
        res = requests.request('GET', url=url, headers=headers)
        return res.json()['records'][0]['fields']['latest_id']
    except Exception as e:
        helper.print_error(e)
        return None

def sync_db_by_table(table, primary_id_column, more_where=None):
    print('====== Uploading Table: {} ======'.format(table))

    # n = How many elements each list should have 
    def divide_chunks(l, n=10): 
        
        # looping till length l 
        for i in range(0, len(l), n):  
            yield l[i:i + n] 

    latest_id = get_latest_id(table)
    where = '{} > {}'.format(primary_id_column, latest_id)
    if more_where is not None:
        where = where + ' and {}'.format(more_where)
    rows = dbm.get_rows_by_table(table, where)
    print('---- syncing {} records with selector: where = {} ----'.format(len(rows), where))

    url = 'https://api.airtable.com/v0/app6uF2BLO7AdMQvn/{}'.format(table)
    rows_by_10 = list(divide_chunks(rows))
    
    with tqdm(total=len(rows)) as pbar:
        for ten_rows in rows_by_10:

            data = {
            'records': []
            }

            for row in ten_rows:
                row['link_to_other_tables'] = summary_table_lookup[table]
                
                for column_name in json_columns_lookup[table]:
                    try:
                        if row[column_name] is not None:
                            row[column_name] = json.dumps(row[column_name])
                            continue
                    except KeyError as e:
                        print('Table {} - Column "{}" does not exist in Row {}'.format(table, column_name, row))
                        helper.print_error(e)
                        pass
                    except Exception as e:
                        print('For Id: {}, Table: {}, Row: {}, Column: {}, JSON failed to parse the selected Column into string.'.fomrat(row[primary_id_column], table, row, column_name))
                        helper.print_error(e)
                        pass

                data['records'].append({'fields': row})
            
            res = requests.request('POST', url=url, headers=headers, data=json.dumps(data))
            pbar.update(len(data['records']))

            helper.wait(1)

def sync_db_all_tables():
    update_check_times = 2
    for update_count in range(update_check_times):
        sync_db_by_table('Site', 'site_id', 'is_active=1 and type="fb_page"')
        sync_db_by_table('Article', 'article_id')
        sync_db_by_table('FBPostSnapshot', 'article_id')
        sync_db_by_table('FBCommentSnapshot', 'article_id')

if __name__ == '__main__':
    sync_db_all_tables()
    print('hold')