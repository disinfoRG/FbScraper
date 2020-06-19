from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    MoveTargetOutOfBoundsException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
    NoSuchWindowException,
    TimeoutException,
)
import re
import logging

logger = logging.getLogger(__name__)

from fbscraper.settings import DEFAULT_BROWSER_TYPE, DEFAULT_EXECUTABLE_PATH


class SecurityCheckError(Exception):
    pass


def _wait_element_by_selector(
    driver,
    selector,
    expected_condition="presence_of_element_located",  #'visibility_of_element_located'
    timeout=5,
):
    try:
        wait = WebDriverWait(driver, timeout=timeout)
        condition = getattr(EC, expected_condition)((By.CSS_SELECTOR, selector))
        return wait.until(condition)
    except TimeoutException as e:
        logger.error(
            f"(condition='{expected_condition}', selector='{selector}', timeout={timeout}) Cannot find element"
        )
        raise


def _keyin_by_selector(driver, selector, value):
    ele = _wait_element_by_selector(driver=driver, selector=selector)
    ele.clear()
    ele.send_keys(value)
    driver.implicitly_wait(1)


def click_by_selector(driver, selector):
    result = None
    ele = _wait_element_by_selector(
        driver=driver, selector=selector, expected_condition="element_to_be_clickable"
    )

    try:
        ele.click()
        result = True
    except Exception as e:
        logger.warning(
            f"(selector='{selector}') Javascript's direct triggered click event does not work"
        )

    try:
        logger.debug(
            f"(selector='{selector}') Try mouse move to element's position and click"
        )

        # work better than queue up and then perform with one line code: ActionChains(driver).move_to_element(ele).click(ele).perform()
        ActionChains(driver).move_to_element(ele).perform()
        ActionChains(driver).click(ele).perform()

        result = True
    except StaleElementReferenceException as e:
        # [StaleElementReferenceException] stale element reference: element is not attached to the page document
        # actually click still work, The element may have been removed and re-added to the screen, since it was located. Such as an element being relocated. This can happen typically with a javascript framework when values are updated and the web element is rebuilt.
        logger.warning(
            f"(selector='{selector}') Occasionally, element is stale. It is due to sometimes element rebuilt for javascript framework's value update and then element cannot be referenced or located. Page refresh may help."
        )
        result = False
    except ElementClickInterceptedException as e:
        # target is blocked by other element, should remove the blocker element
        logger.error(f"(selector='{selector}') Click is blocked by other element")
        raise
    except MoveTargetOutOfBoundsException as e:
        # Webpage unavailable for any mouse interaction
        # Thrown when the target provided to the ActionsChains move() method is invalid, i.e. out of document.
        logger.error(
            f"(selector='{selector}') Webpage or mouse move crashed. Page refresh may help."
        )
        raise
    except Exception as e:
        # print selector because default error will not show
        logger.error(f"(selector='{selector}') Other click exception occurred.")
        raise

    return result


def move_to_element_by_selector(driver, selector):
    try:
        ele = _wait_element_by_selector(driver=driver, selector=selector)
        ActionChains(driver).move_to_element(ele).perform()
    except Exception as e:
        # print selector because default error will not show
        logger.error(f"(selector='{selector}') Cannot move mouse to element")
        raise


def create_driver_without_session(
    browser_type=DEFAULT_BROWSER_TYPE,
    executable_path=DEFAULT_EXECUTABLE_PATH,
    is_headless=True,
):
    result = None
    options = None

    if browser_type == "Chrome":
        options = webdriver.chrome.options.Options()
    elif browser_type == "Firefox":
        options = webdriver.firefox.options.Options()

    # base options
    # open Browser in maximized mode
    options.add_argument("--start-maximized")
    # seems infobars not supported by Chrome
    options.add_argument("--disable-infobars")
    # disabling extensions
    options.add_argument("--disable-extensions")

    # headless options
    options.headless = is_headless
    if is_headless:
        # applicable to windows os only
        options.add_argument("--disable-gpu")
        # overcome limited resource problems
        options.add_argument("--disable-dev-shm-usage")
        # Bypass OS security model
        options.add_argument("--no-sandbox")

    # the selection of browser
    if browser_type == "Chrome":
        if executable_path:
            result = webdriver.Chrome(executable_path=executable_path, options=options)
        else:
            # browser's executable_path is in PATH
            result = webdriver.Chrome(options=options)
    elif browser_type == "Firefox":
        if executable_path:
            result = webdriver.Firefox(executable_path=executable_path, options=options)
        else:
            # browser's executable_path is in PATH
            result = webdriver.Firefox(options=options)

    return result


def login_with_account(driver=None, email=None, password=None):
    logger.info(" -----  login_with_account")
    driver.get("https://www.facebook.com")

    _keyin_by_selector(driver=driver, selector="#email", value=email)
    _keyin_by_selector(driver=driver, selector="#pass", value=password)
    click_by_selector(driver=driver, selector="#loginbutton")


def is_login_success(driver, timeout=10):
    try:
        _wait_element_by_selector(selector="#sideNav", driver=driver, timeout=timeout)
        logger.info(" -----  login success")
        result = True
    except TimeoutException:
        result = False

    return result


def raise_if_security_check(driver):
    logger.debug(" ----- checking if encountered facebook's security check")

    # scroll to trigger any hidden security check
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    is_robot_url = re.match(".*/checkpoint.*", driver.current_url)
    is_forced_robot_verify = len(driver.find_elements_by_css_selector("#captcha")) > 0
    if is_robot_url or is_forced_robot_verify:
        raise SecurityCheckError("Encountered security check if user is a robot")
    logger.debug(" ----- no robot check")

    is_login_url = re.match(".*/login.*", driver.current_url)
    # id of button with text: "忘記帳號？" but not the id for page of "稍後再說"
    is_forced_login_verify = (
        len(driver.find_elements_by_css_selector("#login_link")) > 0
    )
    if is_login_url or is_forced_login_verify:
        raise SecurityCheckError("Encountered security check requiring user to login")
    logger.debug(" ----- no login check")


def get_facebook_url_info(url):
    def get_post_id_and_type(_url):
        result = None
        # post
        # https://www.facebook.com/gushi.tw/posts/2497783880459937?__xts__%5B0%5D=68.ARDbW5UsQAib2f6AhUSWlUd14puN0S3wDD0lu_HWiKphufxnWorDIS6auvPx2XP5IF4WYa6E9Io1Xh54QKrzasCfyz-YIhfjbsvn2fgKtdTj9pueZWA2rwcqP3lfojWzsbP3L7UIdF6QPwSunxcFXgfqDBWXGZGi0USmENBzljNwiAhXokTqCegr1c43ybrmHgTokEiEbeWCvQuG1TnR2HBfodeOKXhqO_v4N5jr9VFUq3X4xl2goQ90NesQloptFubcudH3XmdWEnvggbff8TjEEpEtFBqE7tEAqfYAjBs5vqekgZKFrrrU9ZYWo33LZqLi6d0&__tn__=-R0.g
        if len(re.findall("\/posts\/(\w+)", _url)) > 0:
            result = {"id": re.findall("\/posts\/(\w+)", _url)[0], "type": "post"}
        # video
        # https://www.facebook.com/Wackyboys.Fans/videos/2452717014996864/?__xts__%5B0%5D=68.ARAvj4VDiok00FyWYH8Z6-CfMUuiKKlRIBfwnU6PmNEgcdDgBwP064gXAvQrk749Lk-G-eKK5cMLvuTvQtC3o3Q49y3btN7JDOb8CrsjxJB5FMNk7RPpmukw4N4HMmw94t3hH8_jmELHgcvd5YiHXFQcnvJ6OEqECZq_iL6ObarfUDnoUVAfo1SfVJzGg_ucWX5XzXFIkoCEjcEVs-zNOh4Vm4wtjngaKFyCvEvdh4C44l9DU5PHbHY0Z1WbGmoPvMA-zc5g8KqxfVXFMCNoab5FJ5zT9pWETZb9OVfe9wkWYBDXdsIVyhgMTiSdlfnIv_7ntDuyyepTzK7M&__tn__=-R
        elif len(re.findall("\/videos\/(\w+)", _url)) > 0:
            result = {"id": re.findall("\/videos\/(\w+)", _url)[0], "type": "video"}
        # photo
        # https://www.facebook.com/121570255108696/photos/a.123441864921535/539538693311848/?type=3&__xts__%5B0%5D=68.ARA6rYVIdTFoURfgtAk7MYP31YGVtprQD3XebhVwZrQJsFLn9p8IrndnWNqM20mN8uI4qJMJIlccHtAaPX3RfJWq73MaykNjGwTTuSEl48j8SDJ-sQtDzwhC7z5LRrWvtN4tdS1_4hZRXaRUxjgP7u6Vs-N8C7eRkwKBzZJ6jS16M1bru4QiXc3NlBHnx1QgrDMpsb7xVr5eZuZoaqVRisFkDMRymGkkmoZ_xbSUZXXTz-jhJQ2SSGeHHyMFl5eQqpVZYexFkylhdwSL4LBXZyQC1vCc6b7MGZ3dXz08OsSebylqdxNUFlTZgg4hpiktqCWc8UAkqXl7YzVxndTX2E8&__tn__=-R
        elif len(re.findall("\/photos\/.*\/(\w+)", _url)) > 0:
            result = {
                "id": re.findall("\/photos\/.*\/(\w+)", _url)[0],
                "type": "photo",
            }
        # story_fbid
        # https://www.facebook.com/permalink.php?story_fbid=636096237164329&id=185537762220181&__xts__%5B0%5D=68.ARDXxSWoo2rCRDwjx5S1lYqEcEfvBMn1UTxm5NhakAusCUlvWei7dO7PwFhzAiit3Whq7RrG5MT7R2dgrTVfZ1fZSK3bOF5VzuM5SzsV5c0O1QKfCEVEcnnH7_auDpVO6vAhUQqyWl1tpc87-S2r18n0tY3hHFgKo5jt3Bt-stjPxqUYnpgrvj_Olu0bhuoE7Lfu28jonlluTpEmqjmoI2l5RXDsdHiyCpgarTpO-VosE6UiYHQYlkWlCpjVrSk5EL1cddjfs_suqFtKzhI4zd607DOsUCEbnJqxrjN5JWU_g-tWE2O0bTUh4tTeQTIt3OrvuM1IFzUNNaX6UsLuZImCiPJ7pvO4XACaF8o7h1w9xzpT-NYlc2ux9Klk-JDjAaZJyfUBYGGkMxXnZouXovKMgbk_vqt1tm0Hh_kVSKKjfI6HXkB_osuy26i3gW85HTifiFZCd2vIk-pNIk7JL59b6LI0DjvRztbMNUhhQDnlf3IGrIY&__tn__=-R
        # https://www.facebook.com/permalink.php?story_fbid=539530269979357&id=121570255108696
        elif len(re.findall("story_fbid\=(\d+?)\D", _url)) > 0:
            result = {
                "id": re.findall("story_fbid\=(\d+?)\D", _url)[0],
                "type": "story_fbid",
            }
        return result

    def parse_common_type(_url, _type):
        result = None
        # for normal post, video, photo
        u = _url if _url.endswith("/") else _url + "/"
        r = "facebook.com\/(.*?)\/"
        m = re.findall(r, u)

        if len(m) == 0:
            if u.startswith("/"):
                r = "\/(.+?)\/{}s".format(_type)
            else:
                r = "(.+?)\/{}s".format(_type)
            m = re.findall(r, u)
            if len(m) > 0:
                result = m[0]
        return result

    def parse_story_fbid(_url, _type):
        result = None
        # for story_fbid (aka. https://www.facebook.com/permalink.php?story_fbid=636095870497699&id=185537762220181&__xts__%5B0%5D=68.ARCf_eRqNCjMHCrF1FpzArZumj35pO8phq9MYa8nTLqK9QsoboTD-EOTPFn_mFHto8H7O5ZJbcpGOek-9fi3s_TmxAuuai9GL1vBvNFnYp9niSdU3oDKRrt-HoYoogWDMbUcSt07miwVMcKiscOErEhQxNw4C8bN_pTJB-F_dRQwT1vjOApIZdAgUtlvJ_PxKcLrQa6ZuYCr_MVMdr2j2tlHXXe1bYOdYy-PlxJFdkwS4xyeJbZI6s16EuQ7Ityyz8j7rHoFgj028kQi0ckU77ioWVqbvbqrMRzfEVRmWUGepvI-Wj0sMcFo2XvuZjhUSH7C666eyLP3LetXW1wRQmYqBP2RNGnpawPtt8IgSc8dTmn64XNZw3Q91Rb9kC-9ZabNRTuzUuB4Mec9ANoOVoafbQVC5Yj-ATIac0BJ4dsSFO2KAzHNuVirEpkNb2UmaTxBX4noPXN2Yw3pjF4X-hiWlJrkwQRhI9uFmDHKGzP1ncHeuy_dDQ&__tn__=-R)
        if len(re.findall("\Wid\=(\d+)", _url)) > 0:
            result = re.findall("\Wid\=(\d+)", _url)[0]
        return result

    def get_permalink(_url_info):
        # all types of post can accessed by https://www.facebook.com/{page_id}/posts/{post_id}
        return "https://www.facebook.com/{page_id}/posts/{post_id}".format(**_url_info)

    switcher = {
        "post": parse_common_type,
        "video": parse_common_type,
        "photo": parse_common_type,
        "story_fbid": parse_story_fbid,
    }

    post_info = get_post_id_and_type(url)
    url_type = post_info["type"]
    parse_url_root_id_func = switcher.get(url_type, lambda: None)

    url_info = {}
    url_info["page_id"] = parse_url_root_id_func(url, url_type)
    url_info["post_id"] = post_info["id"]
    url_info["permalink"] = get_permalink(url_info)
    url_info["type"] = post_info["type"]
    url_info["original_url"] = url

    return url_info
