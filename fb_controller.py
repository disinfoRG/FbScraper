import json
import os
import re
import threading
import random

# self-defined
from helper import helper
import db_manager
from discover import main as discover
# from update import update_one

WORKER_TYPE_DISCOVER = 'discover'
WORKER_TYPE_UPDATE = 'update'

class FbController:
    def __init__(self, password_by_email):
        self.session_ids = []
        self.working_session_ids = []
        self.hanging_session_ids = []
        self.cookie_ids = []
        self.occupied_cookie_ids = []
        self.session_id_by_cookie_id = {}
        self.cookie_id_by_session_id = {}
        self.password_by_email = password_by_email
        self.thread_pool = []

    def has_available_cookie(self):
        available_cookie_ids = self.get_available_cookie_ids()
        if len(available_cookie_ids) == 0:
            if len(self.working_session_ids) == len(self.cookie_ids):
                return False
        return True

    def control(self):
        self.update_cookie_and_session_ids()
        if not self.has_available_cookie():
            return

        sites = db_manager.get_sites_tagged_need_to_discover()
        articles = db_manager.get_articles_tagged_need_to_update()
        if len(sites) == 0 and len(articles) == 0:
            return

        self.release_hanging_browsers()
        available_cookie_ids = self.get_available_cookie_ids()

        worker_type = WORKER_TYPE_DISCOVER
        site_tasks = []
        article_tasks = []
        for cookie_id in available_cookie_ids:
            task = {}
            task['cookie_id'] = cookie_id
            if worker_type == WORKER_TYPE_DISCOVER and len(sites) > 0:
                site = sites.pop(0)
                task['site'] = site
                site_tasks.append(task)
                worker_type = WORKER_TYPE_UPDATE
            elif worker_type == WORKER_TYPE_UPDATE and len(articles) > 0:
                article = articles.pop(0)
                task['article'] = article
                article_tasks.append(task)
                worker_type = WORKER_TYPE_DISCOVER
            else:
                break

        for s_task in site_tasks:
            t = threading.Thread(target=self.discover_site,args=[s_task])
            t.daemon = False
            self.thread_pool.append(t)

        for a_task in article_tasks:
            t = threading.Thread(target=self.update_article,args=[a_task])
            t.daemon = False
            self.thread_pool.append(t)

        self.start()

    def start(self):
        if len(self.thread_pool) > 0:
            for t in self.thread_pool:
                t.start()

    def update_cookie_and_session_ids(self):
        for email in self.password_by_email.keys():
            self.cookie_ids.append(email)

        for fname in os.listdir('.'):
            # if re.match('.*_cookie.json', fname):
            #     email = re.findall('(.*)_cookie.json', fname)[0]
            #     self.cookie_ids.append(email)
            if re.match('.*_session.json', fname):
                if re.match('.*_working_session.json', fname):
                    m = re.findall('(.*)_(.*)_working_session.json', fname)[0]
                    email = m[0]
                    sid = m[1]
                    self.occupied_cookie_ids.append(email)
                    self.session_ids.append(sid)
                    self.working_session_ids.append(sid)
                    self.cookie_id_by_session_id[sid] = email
                    self.session_id_by_cookie_id[email] = sid
                if re.match('.*_hanging_session.json', fname):
                    m = re.findall('(.*)_(.*)_hanging_session.json', fname)[0]
                    email = m[0]
                    sid = m[1]
                    self.occupied_cookie_ids.append(email)
                    self.session_ids.append(sid)
                    self.hanging_session_ids.append(sid)
                    self.cookie_id_by_session_id[sid] = email
                    self.session_id_by_cookie_id[email] = sid

    def release_session(self, session_id, cookie_id):
        if session_id in self.hanging_session_ids:
            self.hanging_session_ids.remove(session_id)
        elif session_id in self.working_session_ids:
            self.working_session_ids.remove(session_id)
            
        if cookie_id in self.occupied_cookie_ids:
            self.occupied_cookie_ids.remove(cookie_id)

        if session_id in self.cookie_id_by_session_id:
            del self.cookie_id_by_session_id[session_id]

        if cookie_id in self.session_id_by_cookie_id:
            del self.session_id_by_cookie_id[cookie_id]

    def kill_session_process(self, session_path):
        session = {}
        with open(session_path, 'r', encoding='utf-8') as f:
            session = json.loads(f.read())
        # from facebook import Facebook
        # browser = Facebook.create_driver_with_session(session)
        # browser.quit()
        os.remove(session_path)

    def release_hanging_browsers(self):
        sids = self.hanging_session_ids

        for sid in sids:
            cid = self.cookie_id_by_session_id[sid]
            session_path = './{}_{}_hanging_session.json'.format(cid, sid)

            if helper.has_file(session_path):
                try:
                    self.kill_session_process(session_path)
                    self.release_session(sid, cid)
                except Exception as e:
                    helper.print_error(e)
            
    def get_available_cookie_ids(self):
        return list(set(self.cookie_ids) - set(self.occupied_cookie_ids))
    
    def discover_site(self, task):
        site = task['site']
        email = task['cookie_id']
        password = self.password_by_email[email]

        cid = email
        sid = int(random.uniform(2, 30000000000))
        session_path = './z_testing_discover_siteid{}_{}_{}_working_session.json'.format(site['site_id'], cid, sid)
        fworking = open(session_path, 'a', buffering=1)
        fworking.write('discover is working')
        fworking.close()


        # db_manager.tag_site_working(site)
        # discover(is_controller_mode=True, controller_site=site, controller_email=email, controller_password=password)
        # db_manager.tag_site_done(site)

    def update_article(self, task):
        # db_manager.tag_article_working(article)
        # update_one(article)
        # db_manager.tag_article_done(article)

        article = task['article']
        email = task['cookie_id']
        password = self.password_by_email[email]

        cid = email
        sid = int(random.uniform(2, 30000000000))
        session_path = './z_testing_update_articleid{}_{}_{}_working_session.json'.format(article['article_id'], cid, sid)
        fworking = open(session_path, 'a', buffering=1)
        fworking.write('update is working')
        fworking.close()        
    

def main():
    password_by_email = {}

    email = 'onethingmake80@gmail.com'
    password = "pcti5p8i7kwxygipsq"
    password_by_email[email] = password

    email2 = 'oohdontworrybehappy@gmail.com'
    password2 ="mhY8vVn3wq43NBzUvq"
    password_by_email[email2] = password2

    # site = dict()
    # site['site_id'] = 66
    # site['url'] = 'https://www.facebook.com/jesusSavesF13/'
    # fbc = FbController(password_by_email)
    # task = {}
    # task['site'] = site
    # task['cookie_id'] = email
    # fbc.discover_site(task)
    # c_list = fbc.control()

    fbc = FbController(password_by_email)
    fbc.control()
    
    print('hold')

if __name__ == '__main__':
    main()