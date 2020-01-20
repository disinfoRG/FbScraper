### Running
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
$ pipenv run alembic upgrade head
$ cd airtable
$ pipenv run scrapy runspider airtable/spiders/updateSites.py
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
