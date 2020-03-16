# Running
## Refresh database's site list
docker build -t fbscraper_image --build-arg CACHEBUST=$(date +%s) . \
&& docker run --env DB_URL=mysql+pymysql://root:mysecret@127.0.0.1:3306/FbScraping \
--env SITE_TYPES=["Fb 專頁", "Fb 公開社團"] \
--network=host --rm --name fbscraper_container -it fbscraper_image \
pipenv run scrapy crawl updateSites \
&& docker rmi fbscraper_image

## Discover a site's new article urls
```sh
docker build -t fbscraper_image --build-arg CACHEBUST=$(date +%s) . \
&& docker run --env DB_URL=mysql+pymysql://root:mysecret@127.0.0.1:3306/FbScraping \
--network=host --rm --name fbscraper_container -it fbscraper_image \
python3 fb_site.py <SITE_ID> \
&& docker rmi fbscraper_image
```

## Update a site's articles
```sh
docker build -t fbscraper_image --build-arg CACHEBUST=$(date +%s) . \
&& docker run --env DB_URL=mysql+pymysql://root:mysecret@127.0.0.1:3306/FbScraping \
--network=host --rm --name fbscraper_container -it fbscraper_image \
python3 fb_site.py <SITE_ID> \
&& docker rmi fbscraper_image
```

## Update an article
```sh
docker build -t fbscraper_image --build-arg CACHEBUST=$(date +%s) . \
&& docker run --env DB_URL=mysql+pymysql://root:mysecret@127.0.0.1:3306/FbScraping \
--network=host --rm --name fbscraper_container -it fbscraper_image \
python3 fb_post.py <ARTICLE_ID> \
&& docker rmi fbscraper_image
```