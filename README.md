# FbScraper

### Setup

#### Install Python packages
We use Python 3.7.  Install Python dependencies and run database migrations:

```sh
$ pip install pipenv
$ pipenv install --dev
```

#### Set up Database
We use MySQL (MariaDB 10).  To setup database connections:
1. Create a database.  Take a note of the database name, hostname, username, and password.
2. The database connection string will be `mysql+pymysql://<username>:<password>@<hostname>/<database name>`.  We use PyMySQL, so the connection string should starts with `mysql+pymysql` in order for SQLAlchemy to pick up the right driver.
3. Copy `.env.default` to `.env`.
4. Edit the value of `DB_URL` to be the connection string.  You can leave all other settings in `.env` as is for now.
5. Run db migrations with `pipenv run alembic upgrade head`


Then, update your site table.  First, you need an API key from Airtable generated [here](https://airtable.com/account) and the id of your base (see [here](https://airtable.com/api) for info).  Add the following variables to `.env`:
```sh
$ echo AIRTABLE_BASE_ID={id_of_your_airtable_base} >> .env
$ echo AIRTABLE_API_KEY={your_api_key} >> .env
$ echo SITE_TYPES=["{site_type_1}", "{site_type_2}",...] >> .env
```
Afterwards, do the following to update your site table
```sh
$ SCRAPY_PROJECT=sitesAirtable pipenv run scrapy crawl updateSites
```

### Running
1. Find new posts for all ACTIVE facebook pages/groups listed in Site table in database. Activity is determined by 'is_active' column in airtable.
```sh
$ python fb.py discover
```
    Optional Arguments:
            --limit-sec: process run time limit in seconds, default = 3000.
            --site-limit-sec: max load time in seconds for a site, default = 1800.

1. Revisit posts in database based on next_snapshot_at parameter in Article Table on the mysql database.
The function will save new html to ArticleSnapshot table and update the snapshot parameters in Article Table.
```sh
# update all
$ python fb.py update
```
    Optional Arguments:
            --limit-sec: process run time limit in seconds, default = 3000.
            --article-limit-sec: max load time in seconds for a post, default = 60.


1. Find new posts for a specified facebook page/group.
```sh
$ python fb.py site discover {site-id}
```
    Optional Arguments:
            --limit-sec: process run time limit in seconds, default = 3000.
            
1. Revisit posts in a specified facebook page/group.
```sh
$ python fb.py site update {site-id}
```
    Optional Arguments:
            --limit-sec: process run time limit in seconds, default = 3000.
            --article-limit-sec: max load time in seconds for a post, default = 60.