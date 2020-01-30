import helper
from multiprocessing import Pool
import db_manager
from discover import discover_one
from update import update_one

def release_hanging_chromes():
    pids = db_manager.get_hanging_chrome_pids()

    for pid in pids:
        kill_chrome_command = "\
            kill %s 2>&1 \
            && wait %s \
        " % (pid, pid)
        os.system(kill_chrome_command)
        db_manager.remove_chrome_with_pid(pid)

def get_available_cookies()
    fb_login_cookies = []
    for fname in os.listdir('.'):
        if re.match('_cookie.json', fname):
            fb_login_cookies.append(fname)

    occupied_cookies = get_working_chrome_cookies()
    available_cookies = list(set(fb_login_cookies) - set(occupied_cookies))

    return available_cookies

def discover_site(site):
    db_manager.tag_site_working(site)
    discover_one(site)
    db_manager.tag_site_done(site)

def update_article(article):
    db_manager.tag_article_working(article)
    update_one(article)
    db_manager.tag_article_done(article)

def main():
    sites = db_manager.get_sites_tagged_need_to_crawl()
    articles = db_manager.get_articles_tagged_need_to_update()

    if len(sites) == 0 and len(articles) == 0:
        return

    release_hanging_chromes()
    available_cookies = get_available_cookies()

    WORKER_DISCOVER = 'discover'
    WORKER_UPDATE = 'update'
    worker_type = WORKER_DISCOVER
    site_tasks = []
    article_tasks = []
    for c in available_cookies:
        if worker_type == WORKER_DISCOVER and len(sites) > 0:
            s = sites.pop()
            site_tasks.append(s)
            worker_type = WORKER_UPDATE
        elif worker_type == WORKER_UPDATE and len(articles) > 0:
            a = articles.pop()
            article_tasks.append(a)
            worker_type = WORKER_DISCOVER
        else:
            break
    
    with Pool(5) as p:
        p.map(discover_site, site_tasks)

    with Pool(5) as p:
        p.map(update_article, article_tasks)
    