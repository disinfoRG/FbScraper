#!/usr/bin/env python

import argparse
import pugsql
import time
import multiprocessing
from fbscraper.settings import LOG_LEVEL, LOG_FORMAT, LOG_DATEFMT
import logging

logging.basicConfig(
    format=LOG_FORMAT,
    datefmt=LOG_DATEFMT,
    level=LOG_LEVEL,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("fb_site.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# self-defined
import fbscraper.facebook as fb
from fbscraper.actions.discover import DiscoverCrawler
from fbscraper.actions.update import UpdateCrawler
from fbscraper.settings import (
    SITE_DEFAULT_LIMIT_SEC,
    POST_DEFAULT_LIMIT_SEC,
    DB_URL,
    DEFAULT_BROWSER_TYPE,
    DEFAULT_EXECUTABLE_PATH,
)

db = pugsql.module("queries")
db.connect(DB_URL)


def update_all(site_id, article_limit_sec):
    articles_len = next(
        db.get_articles_outdated_count_by_site_id(site_id=site_id, now=int(time.time()))
    )["count"]
    if articles_len == 0:
        return

    articles = db.get_articles_outdated_by_site_id(
        site_id=site_id, now=int(time.time())
    )

    browser = fb.create_driver_without_session(
        browser_type=DEFAULT_BROWSER_TYPE,
        executable_path=DEFAULT_EXECUTABLE_PATH,
        is_headless=True,
    )

    count = 0
    for article in articles:
        count += 1
        article_id = article["article_id"]
        article_url = article["url"]
        logger.info(f"({count}/{articles_len}) start to update article id {article_id}")

        try:
            crawler = UpdateCrawler(
                article_url=article_url,
                db=db,
                article_id=article_id,
                browser=browser,
                limit_sec=article_limit_sec,
            )

            crawler.crawl_and_save()

        except fb.SecurityCheckError as e:
            logger.error(e)
            break
        except Exception as e:
            logger.debug(e)

        logger.info(f"({count}/{articles_len}) end to update article id {article_id}")

    if browser:
        browser.quit()


def update(site_id, article_limit_sec, limit_sec):
    p = multiprocessing.Process(target=update_all, args=(site_id, article_limit_sec,))
    p.start()

    time.sleep(limit_sec)
    # terminate
    p.terminate()
    # Cleanup
    p.join()


def discover(site_id, limit_sec):
    site = db.get_site_by_id(site_id=site_id)
    site_url = site["url"]

    existing_article_urls = [
        x["url"] for x in db.get_article_urls_of_site(site_id=site_id)
    ]
    db.update_site_crawl_time(site_id=site_id, last_crawl_at=int(time.time()))
    try:
        browser = fb.create_driver_without_session(
            browser_type=DEFAULT_BROWSER_TYPE,
            executable_path=DEFAULT_EXECUTABLE_PATH,
            is_headless=True,
        )

        crawler = DiscoverCrawler(
            browser=browser,
            db=db,
            site_url=site_url,
            site_id=site_id,
            existing_article_urls=existing_article_urls,
            limit_sec=limit_sec,
        )

        crawler.crawl_and_save()

        browser.quit()
    except fb.SecurityCheckError as e:
        logger.error(e)
    except Exception as e:
        logger.debug(e)


def main(args):
    print(args)
    if args.command == "discover":
        discover(args)
    elif args.command == "update":
        update(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    cmds = parser.add_subparsers(title="sub command", dest="command", required=True)

    discover_cmd = cmds.add_parser("discover", help="do discover")
    discover_cmd.add_argument(
        "id", type=int, help="id of the site to work on",
    )
    discover_cmd.add_argument(
        "--limit-sec", type=int, help="process run time limit in seconds", default=3000
    )

    update_cmd = cmds.add_parser("update", help="do update")
    update_cmd.add_argument(
        "id", type=int, help="id of the site to work on",
    )

    update_cmd.add_argument(
        "--limit-sec", type=int, help="process run time limit in seconds", default=3000
    )
    update_cmd.add_argument(
        "--article-limit-sec", type=int, help="max load time in seconds for a post", default=POST_DEFAULT_LIMIT_SEC
    )

    args = parser.parse_args()
    main(args)
