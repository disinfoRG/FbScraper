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
        logging.FileHandler("fb-post.log", encoding="utf-8"),
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
    DEFAULT_IS_HEADLESS,
)


def main():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "article_id", type=int, help="specify article id for update",
    )
    argument_parser.add_argument(
        "--headful",
        action="store_true",
        help="run selenium in headful mode",
        default=(not DEFAULT_IS_HEADLESS),
    )
    args = argument_parser.parse_args()
    article_id = args.article_id

    logger.info(f"start with article id {article_id}")

    db = pugsql.module("queries")
    db.connect(DB_URL)

    article = db.get_article_by_id(article_id=article_id)
    article_url = article["url"]

    try:
        browser = fb.create_driver_without_session(
            browser_type=DEFAULT_BROWSER_TYPE,
            executable_path=DEFAULT_EXECUTABLE_PATH,
            is_headless=(not args.headful),
        )

        crawler = UpdateCrawler(
            article_url=article_url,
            db=db,
            article_id=article_id,
            browser=browser,
            limit_sec=POST_DEFAULT_LIMIT_SEC,
        )

        crawler.crawl_and_save()

        browser.close()
        browser.quit()
    except fb.SecurityCheckError as e:
        logger.error(e)
    except Exception as e:
        logger.debug(e)

    logger.info(f"end with article id {article_id}")


if __name__ == "__main__":
    main()
