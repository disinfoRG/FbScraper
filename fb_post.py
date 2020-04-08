#!/usr/bin/env python

import argparse
import pugsql
from fbscraper.settings import LOG_LEVEL, LOG_FORMAT, LOG_DATEFMT
import logging

logging.basicConfig(
    format=LOG_FORMAT,
    datefmt=LOG_DATEFMT,
    level=LOG_LEVEL,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("fb_post.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# self-defined
import fbscraper.facebook as fb
from fbscraper.actions.update import UpdateCrawler
from fbscraper.settings import (
    POST_DEFAULT_LIMIT_SEC,
    DB_URL,
    DEFAULT_BROWSER_TYPE,
    DEFAULT_EXECUTABLE_PATH,
)


def update(args):
    db = pugsql.module("queries")
    db.connect(DB_URL)

    article = db.get_article_by_id(article_id=args.article_id)
    article_url = article["url"]

    try:
        browser = fb.create_driver_without_session(
            browser_type=DEFAULT_BROWSER_TYPE,
            executable_path=DEFAULT_EXECUTABLE_PATH,
            is_headless=True,
        )

        crawler = UpdateCrawler(
            article_url=article_url,
            db=db,
            article_id=args.article_id,
            browser=browser,
            limit_sec=POST_DEFAULT_LIMIT_SEC,
        )

        crawler.crawl_and_save()

        browser.quit()
    except fb.SecurityCheckError as e:
        logger.error(e)
    except Exception as e:
        logger.debug(e)


def main(args):
    if args.command == "update":
        update(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    cmds = parser.add_subparsers(title="sub command", dest="command", required=True)

    update_cmd = cmds.add_parser("update", help="do update")
    update_cmd.add_argument(
        "site-id", type=int, help="id of the site to work on",
    )

    args = parser.parse_args()
    main(args)
