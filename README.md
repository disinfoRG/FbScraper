# Quick Start
## Run database server
每次開發時啟動container：docker start -a fbscraper_database
```sh
docker run --name fbscraper_database -e 'MYSQL_ROOT_PASSWORD=<your_db_password>' -p 3306:3306 -p 33060:33060 -d mysql:5.7.29
```

## Create database
```sh
mysql -u root -p -e 'CREATE DATABASE <your_db_name> CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'
```

## Apply latest schema to database
```sh
docker build -t fbscraper_image --build-arg CACHEBUST=$(date +%s) . \
&& docker run --env DB_URL=mysql+pymysql://root:<your_db_password>@127.0.0.1:3306/<your_db_name> \
--network=host --rm --name fbscraper_container -it fbscraper_image \
pipenv run alembic upgrade head \
&& docker rmi fbscraper_image
```

## Refresh database's site list
You need an API key from Airtable generated [here](https://airtable.com/account).
```sh
docker build -t fbscraper_image --build-arg CACHEBUST=$(date +%s) . \
&& docker run --env DB_URL=mysql+pymysql://root:<your_db_password>@127.0.0.1:3306/<your_db_name> \
--env AIRTABLE_API_KEY=<your_api_key> \
--env SITE_TYPES=["Fb 專頁", "Fb 公開社團"] \
--network=host --rm --name fbscraper_container -it fbscraper_image \
pipenv run scrapy crawl updateSites \
&& docker rmi fbscraper_image
```

## Discover a site's new article urls
```sh
docker build -t fbscraper_image --build-arg CACHEBUST=$(date +%s) . \
&& docker run --env DB_URL=mysql+pymysql://root:<your_db_password>@127.0.0.1:3306/<your_db_name> \
--network=host --rm --name fbscraper_container -it fbscraper_image \
python3 fb_site.py <SITE_ID> \
&& docker rmi fbscraper_image
```

## Update a site's articles
```sh
docker build -t fbscraper_image --build-arg CACHEBUST=$(date +%s) . \
&& docker run --env DB_URL=mysql+pymysql://root:<your_db_password>@127.0.0.1:3306/<your_db_name> \
--network=host --rm --name fbscraper_container -it fbscraper_image \
python3 fb_site.py <SITE_ID> \
&& docker rmi fbscraper_image
```

## Update an article
```sh
docker build -t fbscraper_image --build-arg CACHEBUST=$(date +%s) . \
&& docker run --env DB_URL=mysql+pymysql://root:<your_db_password>@127.0.0.1:3306/<your_db_name> \
--network=host --rm --name fbscraper_container -it fbscraper_image \
python3 fb_post.py <ARTICLE_ID> \
&& docker rmi fbscraper_image
```