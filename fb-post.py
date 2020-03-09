#!/usr/bin/env python

import argparse
import pugsql
from settings import LOG_LEVEL, LOG_FORMAT, LOG_DATEFMT
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
import facebook as fb
from fbscraper.actions.update import UpdateCrawler
from settings import (
    POST_DEFAULT_TIMEOUT,
    DB_URL,
    DEFAULT_BROWSER_TYPE,
    DEFAULT_EXECUTABLE_PATH,
    DEFAULT_IS_HEADLESS,
)


def main():
    article_id = None
    browser = None

    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "article_id", help="specify article id for update",
    )
    args = argument_parser.parse_args()

    if args.article_id:
        try:
            article_id = int(args.article_id)
        except Exception as e:
            raise Exception("Please give a valid article id for update")

    logger.info(f"start with article id {article_id}")

    db = pugsql.module("queries")
    db.connect(DB_URL)

    article = db.get_article_by_id(article_id=article_id)
    article_url = article["url"]

    try:
        browser = fb.create_driver_without_session(
            browser_type=DEFAULT_BROWSER_TYPE,
            executable_path=DEFAULT_EXECUTABLE_PATH,
            is_headless=DEFAULT_IS_HEADLESS,
        )

        crawler = UpdateCrawler(
            article_url=article_url,
            db=db,
            article_id=article_id,
            browser=browser,
            timeout=POST_DEFAULT_TIMEOUT,
        )

        crawler.crawl_and_save()
    except fb.SecurityCheckError as e:
        logger.error(e)
    except Exception as e:
        logger.debug(e)

    if browser:
        browser.close()
        browser.quit()

    logger.info(f"end with article id {article_id}")


if __name__ == "__main__":
    main()
