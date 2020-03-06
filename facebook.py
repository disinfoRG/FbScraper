from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.common.exceptions import NoSuchWindowException, TimeoutException
import json
import logging
logger = logging.getLogger(__name__)

# self-defined
from helper import helper

def create_driver_without_session(browser_type='Chrome', executable_path=None, is_headless=True):
    result = None
    options = None

    if browser_type == 'Chrome':
        options = webdriver.chrome.options.Options()
    elif browser_type == 'Firefox':
        options = webdriver.firefox.options.Options()

    # base options
    options.add_argument('--start-maximized'); # open Browser in maximized mode
    options.add_argument('--disable-infobars'); # seems infobars not supported by Chrome
    options.add_argument('--disable-extensions'); # disabling extensions

    # headless options
    options.headless = is_headless
    if is_headless:
        options.add_argument('--disable-gpu'); # applicable to windows os only
        options.add_argument('--disable-dev-shm-usage'); # overcome limited resource problems
        options.add_argument('--no-sandbox'); # Bypass OS security model

    # the selection of browser
    if browser_type == 'Chrome':
        if executable_path:
            result = webdriver.Chrome(executable_path=executable_path, options=options)
        else:
            # browser's executable_path is in PATH
            result = webdriver.Chrome(options=options)
    elif browser_type == 'Firefox':
        if executable_path:
            result = webdriver.Firefox(executable_path=executable_path, options=options)
        else:
            # browser's executable_path is in PATH
            result = webdriver.Firefox(options=options)

    return result

def login_with_account(driver=None, email=None, password=None):
    logger.info(' -----  login_with_account')
    driver.get('https://www.facebook.com')

    helper.keyin_by_selector('#email', email, driver, 5)
    helper.keyin_by_selector('#pass', password, driver, 5)
    helper.click_without_move('#loginbutton', driver)

def is_login_success(driver, timeout=10):
    result = None

    try:
        helper.wait_element_by_selector(selector='#sideNav',
                                        driver=driver,
                                        timeout=timeout)
        logger.info(' -----  login success')
        result = True
    except TimeoutException:
        result = False

    return result

if __name__ == '__main__':
    test_all()
