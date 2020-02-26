# Running
0. install required packages
```sh
$ pip install pipenv
$ pipenv install
```
1. set webdriver
For below, replace <PATH_TO_WEBDRIVER> to the absolute path to the webdriver (aka. chromedriver) on your local computer
```sh
$ echo CHROMEDRIVER_BIN=<PATH_TO_WEBDRIVER> >> .env
```
2. set database url
```sh
$ echo DB_URL=mysql+pymysql://root:mysecret@127.0.0.1:3306/NewsScraping >> .env
```
3. set email and password for login
replace <YOUR_EMAIL> and <YOUR_PASSWORD> to your facebook's email and password
```sh
$ echo FB_EMAIL=<YOUR_EMAIL> >> .env
$ echo FB_PASSWORD=<YOUR_PASSWORD> >> .env
```
4. update database from NewsScraping (https://github.com/disinfoRG/NewsScraping/blob/master/README.md#running)

Required instruction from README.md#running as below:
Then update your site table.  You need an API key from Airtable generated [here](https://airtable.com/account).  Add `AIRTABLE_API_KEY=<your_api_key>` to `.env`, and then:
```sh
$ cd NewsScraping && pipenv install
$ pipenv run alembic upgrade head
$ pipenv run scrapy crawl updateSites
```
5. crawl new post urls for all sites
```sh
$ pipenv run python discover.py --all
```
6. snapshot all FBPost's articles
```sh
$ pipenv run python update.py --all
```
7. turn on headless mode
```sh
in config.py, change False to True
fb = Facebook(FB_EMAIL, FB_PASSWORD, 'Chrome', True, CHROMEDRIVER_BIN)
```

# Architecture
## Handler (Main Function, aka. called by cronjob on Middle2)
- discover.py, update.py
    - decide the target url list for spider to crawl and parse
    - decide how different spiders to work together
## Scheduler (Now not used on Middle2)
- scheduler.py
    - decide how often or when to run which handler (aka. discover.py or update.py)
## Spider (xxx now can be: page or post)
- xxx_spider.py
    - temporary center for all arguments later used to feed in crawler, parser, and pipeline
    - decide how crawler, parser, and pipeline work together
- xxx_crawler.py
    - input: url, output: html
    - principle: output be maximum html of a url with minimum parsing
    - process
        - enter site by url
        - scroll, click and expand the webpage if in need
        - save whole page's html, but sometimes save only part of the html for whole page's html may too much and broke the database pipeline (especially async-loaded posts in sinlge page website)
    - note: may add callbacks to use parser or pipeline, or a totally independent instance
- xxx_parser.py
    - input: html, output: interesting data
    - principle: output be mostly structured than analogy
    - process
        - load html into beautifulsoup (called it soup)
        - apply css selector on soup to get interesting data
    - note: may be used as a callback function in crawler, or a totally independent instance
- xxx_pipeline.py
    - input: html or data, output: write input into database
    - principle: output be minimum modification of input when writing into database
    - process
        - load input from parser or crawler
        - write input with specified id from spider into database
    - note: may be used as a callback function in crawler, or a totally independent instance
## Database
- db.py
    - implement the details to CRUD with database
- db_helper.py
    - abstract common or repeating steps from db.py
- db_manager.py
    - encapsulated db.py for others to use
## Browser
- facebook.py
    - based on webdriver and specialized for facebook
    - cookie_path for reusage to login without reentering email and password
    - session_path for reusage of running browser without reopening a new window
## Utils
- helper.py
    - concentration area of convenient functions and should be independent from any other files
## Configuration
- config.py
    - configure how to run browser (aka. facebook.py)
        - Chrome or Firefox
        - Browser's executalbe binary
        - Headless or not
        - Email and password to login
- settings.py
    - configure required arguments for browser and database

