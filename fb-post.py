#!/usr/bin/env python

import argparse
import pugsql
from fbscraper.settings import LOG_LEVEL, LOG_FORMAT, LOG_DATEFMT, LOG_FILENAME
import logging

logging.basicConfig(
    format=LOG_FORMAT,
    datefmt=LOG_DATEFMT,
    level=LOG_LEVEL,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILENAME, encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# self-defined
import fbscraper.driver.post
import fbscraper.facebook as fb
from fbscraper.settings import (
    POST_DEFAULT_LIMIT_SEC,
    DB_URL,
    DEFAULT_BROWSER_TYPE,
    DEFAULT_EXECUTABLE_PATH,
)

db = pugsql.module("queries")
db.connect(DB_URL)


def update(args):
    article = db.get_article_by_id(article_id=args.id)
    browser = fb.create_driver_without_session()
    fbscraper.driver.post.update(browser, db, article, args.limit_sec)

    if browser:
        browser.quit()


def main(args):
    if args.command == "update":
        update(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    cmds = parser.add_subparsers(title="sub command", dest="command", required=True)

    update_cmd = cmds.add_parser("update", help="do update")
    update_cmd.add_argument(
        "id", type=int, help="id of the article to work on",
    )
    update_cmd.add_argument(
        "--limit-sec",
        type=int,
        help="process run time limit in seconds",
        default=POST_DEFAULT_LIMIT_SEC,
    )

    args = parser.parse_args()
    main(args)
