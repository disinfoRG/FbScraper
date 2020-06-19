import logging

import fbscraper.facebook as fb
from fbscraper.actions.update import UpdateCrawler

logger = logging.getLogger(__name__)


def update(browser, db, article, limit_sec):
    try:
        crawler = UpdateCrawler(
            article_url=article["url"],
            db=db,
            article_id=article["article_id"],
            browser=browser,
            limit_sec=limit_sec,
        )

        crawler.crawl_and_save()
    except fb.SecurityCheckError as e:
        logger.error(e)
    except Exception as e:
        logger.debug(e)
