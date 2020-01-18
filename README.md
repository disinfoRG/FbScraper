test
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

# 粉絲頁 - get_page
- 文章 - get_post
    - 留言 - get_post_comment

# 文章 - get_post
- 所屬粉絲頁的id - page_id
- 永久網址和id - get_post_url
- 文字內容 - get_post_content
- 發布時間 - get_post_published_at
- 互動情形 - get_post_reaction
    - 各互動類別的數字 - TOTAL
    - 互動總數 - LIKE, LOVE, HAHA, WOW, SORRY, ANGER
- 作者 - get_post_author
    - 永久id（粉絲頁即為粉絲頁的真實id，126566854060637）- permanent_id
    - 顯示id（粉絲頁即為粉絲頁顯示的帳號id，ex. verachen.taiwan）- displayed_id
    - 顯示名稱（粉絲頁即為粉絲頁名稱，ex. 陳雪甄 Vera Chen）- displayed_name
- 留言情形
    - 留言（參考下方的「留言」）
    - 留言總數
- 分享情形
    - 分享者
        - 永久id（粉絲頁即為粉絲頁的真實id，126566854060637）
        - 顯示id（粉絲頁即為粉絲頁顯示的帳號id，ex. verachen.taiwan）
        - 顯示名稱（粉絲頁即為粉絲頁名稱，ex. 陳雪甄 Vera Chen）
    - 分享總數
- 爬蟲時間
- raw data

# 留言 - get_post_comment
- 所屬post的id - post_id
- 永久網址和id - get_comment_url
- 文字內容 - get_comment_content
- 發布時間 - get_comment_published_at
- 互動情形 - get_comment_reaction
    - 互動總數
    - 分享總數
- 留言者 - get_comment_author
    - 永久id（粉絲頁即為粉絲頁的真實id，126566854060637）
    - 顯示id（粉絲頁即為粉絲頁顯示的帳號id，ex. verachen.taiwan）
    - 顯示名稱（粉絲頁即為粉絲頁名稱，ex. 陳雪甄 Vera Chen）
- 回應哪一則留言(id，其實就是永久網址) - get_comment_reply_to
- 爬蟲時間
- raw data

# TODO
- [x] 轉成 python script
- [x] 加 get_page
- [x] 加入 page_id 到 post
- [x] 加入 post_id 到 comment
- [x] 加 share 數、comment 數到 FBPostSnapshot 的 reactions
- [x] Selenium 改用 Chromedriver
- [x] 資料庫中文編碼的問題
- [x] 寫使用方法的文件
- [] 改成可以 deploy 到 middle2 上
  - [x] db connect 移到環境變數
  - [x] fb 登入移到環境變數
  - [x] Chromdriver 路徑移到環境變數
- [ ] 測試
- [ ] deploy 到 middle2
- [x] 把留言寫進資料庫
- [ ] 整合到 NewScraping
- [x] comment reply_to which post, comment reply_to which comment
- [ ] scroll 全部，或是抓指定數量的新文章
- [ ] 同步 snapshot_at 和 snapshot_count
- [ ] 確認有抓到留言中的留言
- [ ] 分析留言的不同reactions（從reacitons裡的snpashot）
- [ ] 其他code中的TODO


# Questions

- [ ] 單純分享沒文字的post，應該抓什麼作為 content 及 post id，且有時 url 不會連到粉絲頁上，ex. https://www.facebook.com/verachen.taiwan/posts/2790994537617842?tn=-R 和 https://www.facebook.com/165534787282102/photos/a.255463651622548/767099380458970/?type=3&__xts__%5B0%5D=68.ARAMwcbwZ58elIUaMkQIyuZQhtHS52bSjidiOipZQihDVTxAF2O4N3pLuSJIL2XUkEmRZvJI1DKHdrQyufMepox_gblp8G4s0WWqKwYmx2I1f3YV1TbwpplzKPormyAvFLRoPj17xW_pms5R9YBAAT6gEdpeG7spBJ3htjeorDDmzdY8rNykA9mseCRcajsRMqzWxe9YohgpnoW1oZIZ1B5GXbgNc3BiPoDwDlPFZMtP0efQICr9phiNfkC-1CyM4kmNMtkykBz0mxFtTq4yVKPODGMRFgCn4gerBJmOSjAR1ZDngWTx4E5LQR8M9V9W73tz-UdMpR5Kq9msSmOC4PU&__tn__=-R

- [ ] StaleElementReferenceException in comment of comment (comment.py)
[StaleElementReferenceException] stale element reference: element is not attached to the page document

- [x] ElementClickInterceptedException in click a link (page.py)
ElementClickInterceptedException('element click intercepted: Element <a class="see_more_link" onclick="var func = function(e) { e.preventDefault(); }; var parent = Parent.byClass(this, &quot;text_exposed_root&quot;); if (parent &amp;&amp; parent.getAttribute(&quot;id&quot;) == &quot;id_5e09ac54f28066b69338123&quot;) { CSS.addClass(parent, &quot;text_exposed&quot;); Arbiter.inform(&quot;reflow&quot;); }; func(event); " data-ft="{&quot;tn&quot;:&quot;e&quot;}" href="#" role="button">...</a> is not clickable at point (444, 8). Other element would receive the click: <span class="_1vp5">...</span>\n  (Session info: headless chrome=79.0.3945.88)', None, None)

- [ ] IndexError in get_post_author (post.py)
=== Start: Site: 176 - https://www.facebook.com/hsiweiC/ ===
Post Total: 23
---- #0 Post -----
e
IndexError('list index out of range')
File "/Users/ta-shunlee/Documents/facebook-nbs/post.py", line 165, in get_post_author: [IndexError] list index out of range