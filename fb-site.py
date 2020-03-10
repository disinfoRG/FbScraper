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
        logging.FileHandler("fb-site.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# self-defined
import fbscraper.facebook as fb
from fbscraper.actions.discover import DiscoverCrawler
from fbscraper.settings import (
    SITE_DEFAULT_LIMIT_SEC,
    DB_URL,
    DEFAULT_BROWSER_TYPE,
    DEFAULT_EXECUTABLE_PATH,
    DEFAULT_IS_HEADLESS,
)


def main():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "site_id", type=int, help="specify site id for discover",
    )
    argument_parser.add_argument(
        "--headful",
        action="store_true",
        help="run selenium in headful mode",
        default=(not DEFAULT_IS_HEADLESS),
    )
    args = argument_parser.parse_args()
    site_id = args.site_id

    logger.info(f"start with site id {site_id}")

    db = pugsql.module("queries")
    db.connect(DB_URL)

    site = db.get_site_by_id(site_id=site_id)
    site_url = site["url"]

    existing_article_urls = [
        x["url"] for x in db.get_article_urls_of_site(site_id=site_id)
    ]

    try:
        browser = fb.create_driver_without_session(
            browser_type=DEFAULT_BROWSER_TYPE,
            executable_path=DEFAULT_EXECUTABLE_PATH,
            is_headless=(not args.headful),
        )

        crawler = DiscoverCrawler(
            browser=browser,
            db=db,
            site_url=site_url,
            site_id=site_id,
            existing_article_urls=existing_article_urls,
            limit_sec=SITE_DEFAULT_LIMIT_SEC,
        )

        crawler.crawl_and_save()

        browser.close()
        browser.quit()
    except fb.SecurityCheckError as e:
        logger.error(e)
    except Exception as e:
        logger.debug(e)

    logger.info(f"end with site id {site_id}")


if __name__ == "__main__":
    main()
