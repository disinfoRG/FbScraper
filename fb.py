#!/usr/bin/env python

import sys
import pathlib
import subprocess
import argparse
import fb_site
import pugsql
import os
import multiprocessing
import time
from fbscraper.settings import (
    SITE_DEFAULT_LIMIT_SEC,
    POST_DEFAULT_LIMIT_SEC,
)

queries = pugsql.module("queries/")
queries.connect(os.getenv("DB_URL"))


def discover(args):
    sites = queries.get_sites_to_discover()
    for site in sites:
        fb_site.discover(site["site_id"], limit_sec=SITE_DEFAULT_LIMIT_SEC)


def update(args):
    sites = queries.get_sites_to_discover()
    for site in sites[::-1]:
        fb_site.update(site["site_id"], limit_sec=POST_DEFAULT_LIMIT_SEC)


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
    if args.command == "discover":
        discover(args)
    elif args.command == "update":
        update(args)


if __name__ == "__main__":
    try_subcommands(skip_commands=["post", "site"])

    parser = argparse.ArgumentParser()
    cmds = parser.add_subparsers(title="sub command", dest="command", required=True)
    discover_cmd = cmds.add_parser("discover", help="do discover")
    update_cmd = cmds.add_parser("update", help="do update")
    args = parser.parse_args()

    main(args)
