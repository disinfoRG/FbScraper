#!/usr/bin/env python
import argparse
import pugsql
import time
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
import fb_post
import fbscraper.facebook as fb
from fbscraper.actions.discover import DiscoverCrawler
from fbscraper.settings import (
    SITE_DEFAULT_LIMIT_SEC,
    DB_URL,
    DEFAULT_BROWSER_TYPE,
    DEFAULT_EXECUTABLE_PATH,
    DEFAULT_IS_HEADLESS,
)

db = pugsql.module("queries")
db.connect(DB_URL)


def update(site_id, headful):
    articles = db.get_articles_outdated_by_site_id(
        site_id=site_id, now=int(time.time())
    )
    for article in articles:
        article_id = str(article["article_id"])
        args = [article_id] if not headful else [article_id, "--headful"]
        fb_post.main(args)


def discover(site_id, headful):
    site = db.get_site_by_id(site_id=site_id)
    site_url = site["url"]

    existing_article_urls = [
        x["url"] for x in db.get_article_urls_of_site(site_id=site_id)
    ]

    try:
        browser = fb.create_driver_without_session(
            browser_type=DEFAULT_BROWSER_TYPE,
            executable_path=DEFAULT_EXECUTABLE_PATH,
            is_headless=(not headful),
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


def main():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "site_id", type=int, help="by default, discover article urls for given site id",
    )
    argument_parser.add_argument(
        "--headful",
        action="store_true",
        help="run selenium in headful mode",
        default=(not DEFAULT_IS_HEADLESS),
    )
    argument_parser.add_argument(
        "--update",
        action="store_true",
        help="snapshot html of site's discovered articles",
        default=(not DEFAULT_IS_HEADLESS),
    )
    args = argument_parser.parse_args()

    logger.info(f"start with site id {args.site_id}")

    if not args.update:
        discover(site_id=args.site_id, headful=args.headful)
    else:
        update(site_id=args.site_id, headful=args.headful)

    logger.info(f"end with site id {args.site_id}")


if __name__ == "__main__":
    main()
