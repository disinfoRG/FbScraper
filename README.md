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
4. Update your site table.  You need an API key from Airtable generated [here](https://airtable.com/account).  Add `AIRTABLE_API_KEY=<your_api_key>` to `.env`, and then:
```sh
$ pipenv run scrapy crawl updateSites
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
## Manual
- -d, --discover
    - save article urls for sites
- -u, --update
    - save raw html for article urls 
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
    python3 fb_handler.py --discover --page --login --max 100 --cpu 1 --note onethingmake80@gmail.com_id_71190_total_67700 --auto 2 --timeout 5800 
    ```
    - `--discover --page`: crawl new article urls for facebook pages
    - `--login`: using login account with email and password saved in local .env or environment variables
    - `--cpu 1`: discover using one Chrome(= cpu argument number) at a time for one facebook page
    - `--max 100`: for at most 100 different facebook pages
    - `--auto 2`: automatically switch for two times bewtween login mode and without login mode if encountered any error faield crawling, like a security check.
    - `--note onethingmake80@gmail.com_id_71190_total_67700`: an easy reminder of what the command was doing, so you can just any string there which will not effect how the program run.
    - `--timeout 5800`: discover for one site at most of 5800 seconds, after 5800 seconds the Chrome process will be terminated

    ```
    python3 fb_handler.py --update --group --max 10000 --cpu 2 --note auto_switch_login_with_onethingmake80@gmail.com_id_34382_total_10858 --auto 1 --site 53 --between 100 --non-headless
    ```
    - `--update --group`: create snapshots of raw html for article urls
    - `--max 10000`: update at most 10000 article urls of all facebook groups
    - `--cpu 2`: using two Chrome(= cpu argument number) at a time for two article urls
    - `--auto 1`: automatically switch for one time bewtween login mode and without login mode if encountered any error faield crawling, like a security check.
    - `--note auto_switch_login_with_onethingmake80@gmail.com_id_34382_total_10858`: an easy reminder of what the command was doing, so you can just any string there which will not effect how the program run.
    - `--site 53`: only update article urls of site id = 53
    - `--between 100`: force program to rest for 100 seconds between two update times (for this example, one update time run two Chrome each for one article url)
    - `--non-headless`: turn off headless mode, which means when updating the Chrome will be visible as GUI on the screen

# Architecture
## Handler (Main Function, aka. called by cronjob on Middle2)
- xxx_handler.py
    - decide the target url list for spider to crawl and parse
    - decide how different spiders to work together
## Spider (xxx now can be: discover or update)
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
- queries
    - implement the details to CRUD with database
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
    - configure default arguments
    - `DISCOVER_ACTION = 'discover'`
    - `UPDATE_ACTION = 'update'`
    - `GROUP_SITE_TYPE = 'fb_public_group'`
    - `PAGE_SITE_TYPE = 'fb_page'`
    - `DISCOVER_TIMEOUT = 60*60`
    - `UPDATE_TIMEOUT = 60*10`
    - `UPDATE_CRAWLER_TIMEOUT = UPDATE_TIMEOUT - 60*1`
    - `DEFAULT_IS_LOGINED = False`
    - `DEFAULT_IS_HEADLESS = True`
    - `DEFAULT_MAX_AMOUNT_OF_ITEMS = 1`
    - `DEFAULT_N_AMOUNT_IN_A_CHUNK = 1`
    - `ITEM_PROCESS_COUNTDOWN_DESCRIPTION = 'Item Process Countdown'`
    - `TAKE_A_BREAK_COUNTDOWN_DESCRIPTION = 'Take A Break Countdown'`
    - `DEFAULT_BREAK_BETWEEN_PROCESS = 60*2`
    - `DEFAULT_MAX_AUTO_TIMES = 0`
- settings.py
    - configure required arguments for browser and database
    - `CHROMEDRIVER_BIN`: browser's executalbe binary path
    - `DB_URL`: url to connect to database, ex. mysql+pymysql://root:mysecret@127.0.0.1:3306/FbScraping
    - `AIRTABLE_API_KEY`: to update table Site in database
    - `FB_EMAIL`: email to login facebook
    - `FB_PASSWORD`: password to login facebook

# File Relationship
## `python3 fb_hanlder.py --discover` related files
- discover_spider.py
- discover_crawler.py
- discover_parser.py
- discover_pipeline.py
## `python3 fb_hanlder.py --update` related files
- update_spider.py
- update_crawler.py
- update_parser.py
- update_pipeline.py