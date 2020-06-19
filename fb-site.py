#!/usr/bin/env python

import argparse
import pugsql
import time
import multiprocessing
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
import fbscraper.driver.site
import fbscraper.facebook as fb
from fbscraper.settings import (
    SITE_DEFAULT_LIMIT_SEC,
    POST_DEFAULT_LIMIT_SEC,
    DB_URL,
    DEFAULT_BROWSER_TYPE,
    DEFAULT_EXECUTABLE_PATH,
)


db = pugsql.module("queries")
db.connect(DB_URL)


def update(args):
    browser = fb.create_driver_without_session()
    p = multiprocessing.Process(
        target=fbscraper.driver.site.update,
        args=(browser, db, args.id, args.article_limit_sec,),
    )
    p.start()

    time.sleep(args.limit_sec)
    # terminate
    p.terminate()
    # Cleanup
    p.join()


def discover(args):
    site = db.get_site_by_id(site_id=args.id)
    browser = fb.create_driver_without_session()

    fbscraper.driver.site.discover(browser, db, site, args.limit_sec)

    if browser:
        browser.quit()


def main(args):
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
        "--article-limit-sec",
        type=int,
        help="max load time in seconds for a post",
        default=POST_DEFAULT_LIMIT_SEC,
    )

    args = parser.parse_args()
    main(args)
