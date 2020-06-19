import time
import logging

import fbscraper.driver.post
import fbscraper.facebook as fb
from fbscraper.actions.discover import DiscoverCrawler


logger = logging.getLogger(__name__)


def discover(browser, db, site, limit_sec):
    existing_article_urls = [
        x["url"] for x in db.get_article_urls_of_site(site_id=site["site_id"])
    ]
    db.update_site_crawl_time(site_id=site["site_id"], last_crawl_at=int(time.time()))
    try:
        crawler = DiscoverCrawler(
            browser=browser,
            db=db,
            site_url=site["url"],
            site_id=site["site_id"],
            existing_article_urls=existing_article_urls,
            limit_sec=limit_sec,
        )

        crawler.crawl_and_save()
    except fb.SecurityCheckError as e:
        logger.error(e)
    except Exception as e:
        logger.debug(e)


def find_articles(db, site_id):
    articles_len = next(
        db.get_articles_outdated_count_by_site_id(site_id=site_id, now=int(time.time()))
    )["count"]
    if articles_len == 0:
        return []

    articles = db.get_articles_outdated_by_site_id(
        site_id=site_id, now=int(time.time())
    )
    return articles


def update(browser, db, site_id, article_limit_sec):
    articles = find_articles(db, site_id)
    for i, article in enumerate(articles):
        i += 1
        fbscraper.driver.post.update(browser, db, article, article_limit_sec)
