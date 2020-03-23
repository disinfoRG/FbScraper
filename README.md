# Quick Start
## Run database server
每次開發時啟動container：docker start -a fbscraper_database
```sh
docker run --name fbscraper_database -e 'MYSQL_ROOT_PASSWORD=YOUR_DB_PASSWORD' -p 3306:3306 -p 33060:33060 -d mysql:5.7.29
```

## Create database
```sh
docker exec -it fbscraper_database mysql -u root -pYOUR_DB_PASSWORD -e 'CREATE DATABASE YOUR_DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'
```

## Clone and Enter Repository's Root Folder
```sh
git clone https://github.com/disinfoRG/FbScraper.git \
&& cd FbScraper
```

## Apply latest schema to database
```sh
docker build -t fbscraper_image --build-arg CACHEBUST=$(date +%s) . \
&& docker run --env DB_URL=mysql+pymysql://root:YOUR_DB_PASSWORD@127.0.0.1:3306/YOUR_DB_NAME \
--network=host --rm --name FBSCRAPER_CONTAINER -it fbscraper_image \
alembic upgrade head \
&& docker rmi fbscraper_image
```

## Refresh database's site list
You need an API key from Airtable generated [here](https://airtable.com/account) for YOUR_AIRTABLE_API_KEY
```sh
docker build -t fbscraper_image --build-arg CACHEBUST=$(date +%s) . \
&& docker run --env DB_URL=mysql+pymysql://root:YOUR_DB_PASSWORD@127.0.0.1:3306/YOUR_DB_NAME \
--env AIRTABLE_API_KEY=YOUR_AIRTABLE_API_KEY \
--env SITE_TYPES='["Fb 專頁", "Fb 公開社團"]' \
--network=host --rm --name FBSCRAPER_CONTAINER -it fbscraper_image \
scrapy crawl updateSites \
&& docker rmi fbscraper_image
```

## Discover a site's new article urls
```sh
docker build -t fbscraper_image --build-arg CACHEBUST=$(date +%s) . \
&& docker run --env DB_URL=mysql+pymysql://root:YOUR_DB_PASSWORD@127.0.0.1:3306/YOUR_DB_NAME \
--network=host --rm --name FBSCRAPER_CONTAINER -it fbscraper_image \
python3 fb_site.py SITE_ID \
&& docker rmi fbscraper_image
```

## Update a site's articles
```sh
docker build -t fbscraper_image --build-arg CACHEBUST=$(date +%s) . \
&& docker run --env DB_URL=mysql+pymysql://root:YOUR_DB_PASSWORD@127.0.0.1:3306/YOUR_DB_NAME \
--network=host --rm --name FBSCRAPER_CONTAINER -it fbscraper_image \
python3 fb_site.py SITE_ID --update \
&& docker rmi fbscraper_image
```

## Update an article
```sh
docker build -t fbscraper_image --build-arg CACHEBUST=$(date +%s) . \
&& docker run --env DB_URL=mysql+pymysql://root:YOUR_DB_PASSWORD@127.0.0.1:3306/YOUR_DB_NAME \
--network=host --rm --name fbscraper_container -it fbscraper_image \
python3 fb_post.py ARTICLE_ID \
&& docker rmi fbscraper_image
```

# Note
- `--build-arg CACHEBUST=$(date +%s)`: with this argurment docker will rebuild the repo with `pipenv install --system`
- if you don't want to build everytime: only run `docker build` once to get `fbscraper_image`, don't run `docker rmi`, and then `docker run`
- replace uppercase to what you want: YOUR_DB_PASSWORD, YOUR_DB_NAME, YOUR_AIRTABLE_API_KEY, SITE_ID, ARTICLE_ID