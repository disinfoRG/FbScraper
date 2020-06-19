#!/usr/bin/env python

import sys
import pathlib
import subprocess
import argparse
import pugsql
import os
import multiprocessing
import time
import logging
import fbscraper.driver.post
import fbscraper.driver.site
from fbscraper import facebook as fb
from fbscraper.settings import (
    LOG_FORMAT,
    LOG_DATEFMT,
    LOG_LEVEL,
    LOG_FILENAME,
    SITE_DEFAULT_LIMIT_SEC,
    POST_DEFAULT_LIMIT_SEC,
)

queries = pugsql.module("queries/")
queries.connect(os.getenv("DB_URL"))

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


def discover(args):
    browser = fb.create_driver_without_session()
    sites = queries.get_sites_to_discover()
    for site in sites:
        fbscraper.driver.site.discover(browser, queries, site, args.site_limit_sec)


def update(args):
    browser = fb.create_driver_without_session()
    sites = queries.get_sites_to_discover()
    for site in sites:
        fbscraper.driver.site.update(
            browser, queries, site["site_id"], args.article_limit_sec
        )


def try_subcommands(skip_commands=[]):
    """
    Try git-style subcommands.
    """
    if len(sys.argv) > 1 and sys.argv not in skip_commands:
        binname = pathlib.Path(__file__)
        sub_cmd = (
            binname.parent.resolve() / f"{binname.stem}-{sys.argv[1]}{binname.suffix}"
        )
        try:
            sys.exit(subprocess.run([sub_cmd, *sys.argv[2:]]).returncode)
        except FileNotFoundError:
            pass


def main(args):
    target_func = None
    if args.command == "discover":
        target_func = discover
    elif args.command == "update":
        target_func = update

    if target_func:
        p = multiprocessing.Process(target=target_func, args=(args,))
        p.start()

        time.sleep(args.limit_sec)
        # terminate
        p.terminate()
        # Cleanup
        p.join()


if __name__ == "__main__":
    try_subcommands(skip_commands=["post", "site"])

    parser = argparse.ArgumentParser()
    cmds = parser.add_subparsers(title="sub command", dest="command", required=True)
    discover_cmd = cmds.add_parser("discover", help="do discover")
    discover_cmd.add_argument(
        "--limit-sec", type=int, help="process run time limit in seconds", default=3000
    )
    discover_cmd.add_argument(
        "--site-limit-sec",
        type=int,
        help="max load time in seconds for a site",
        default=SITE_DEFAULT_LIMIT_SEC,
    )

    update_cmd = cmds.add_parser("update", help="do update")
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
