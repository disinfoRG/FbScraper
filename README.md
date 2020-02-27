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
$ SCRAPY_PROJECT=sitesAirtable pipenv run scrapy crawl updateSites
```
5. discover new post urls for at most 100 different facebook pages using login email and password
```sh
$ pipenv run python3 fb_handler.py --discover --page --login --cpu 1 --max 100
```
6. update snapshot without login at most 1000 articles for facebook page of site id  = 53 
```sh
$ pipenv run python3 fb_handler.py --discover --page --cpu 1 --max 1000 --site 53
```
# Command
- -d, --discover
    - save article urls for sites
- -u, --update
    - save html for articles    
- -g, --group
    - facebook group
- -p, --page 
    - facebook page    
- -l, --login
    - apply facebook login, default is without login
- -t, --timeout
    - timeout for a site discover or an article update    
- -nh, --non-headless
    - browser in non-headless mode, default is headless
- -m, --max
    - max amount of sites(by discover) or articles(by update) want to be accomplished, default is 2
- -c, --cpu
    - how many cpu processes run at the same time, default is 2
- -b, --between
    - time break before continueing next site discover or article update, default is random time between 0 second to 120 second
- -n, --note
    - additional note to be viewed on CLI
- -s, --site
    - discover and update sites or articles from specific site id
- -a, --auto
    - max times of automatically switch between login and without-login for any error, default auto-switch max times is 0
## Example
-
    ```
    python3 fb_handler.py --discover --page --login --max 100 --cpu 1 --note onethingmake80@gmail.com_id_71190_total_67700 --auto 2 
    ```
    - `--discover --page`: crawl new article urls for facebook pages
    - `--login`: using login account with email and password saved in local .env or environment variables
    - `--cpu 1`: discover using one Chrome(= cpu argument number) at a time for one facebook page
    - `--max 100`: for at most 100 different facebook pages
    - `--auto 2`: automatically switch for two times bewtween login mode and without login mode if encountered any error faield crawling, like a security check.
    - `--note onethingmake80@gmail.com_id_71190_total_67700`: an easy reminder of what the command was doing, so you can just any string there which will not effect how the program run.
- 
    ```
    python3 fb_handler.py --update --group --max 10000 --cpu 2 --note auto_switch_login_with_onethingmake80@gmail.com_id_34382_total_10858 --auto 1
    ```
    - `--update --group`: create snapshots of raw html for article urls
    - `--max 10000`: update at most 10000 article urls of all facebook groups
    - `--cpu 2`: using two Chrome(= cpu argument number) at a time for two article urls
    - `--auto 1`: automatically switch for one time bewtween login mode and without login mode if encountered any error faield crawling, like a security check.
    - `--note auto_switch_login_with_onethingmake80@gmail.com_id_34382_total_10858`: an easy reminder of what the command was doing, so you can just any string there which will not effect how the program run.


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

