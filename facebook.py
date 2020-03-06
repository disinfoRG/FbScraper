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

# --------------- TEST ---------------

def test_create_driver_without_session():
    result = None

    # test_create_driver_without_session
    logger.debug('--------- Test create browser without session: START ---------')
    try:
        from settings import CHROMEDRIVER_BIN
        browser_type = 'Chrome'
        executable_path = CHROMEDRIVER_BIN
        is_headless = False

        driver = create_driver_without_session(browser_type=browser_type, 
                                                    executable_path=executable_path, 
                                                    is_headless=is_headless)

        from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
        is_driver = isinstance(driver, ChromeWebDriver)
        if not is_driver:
            raise Exception('driver failed')

        # WRONG url='google.com'
        # selenium.common.exceptions.InvalidArgumentException: Message: invalid argument
        url = 'https://g0v.hackmd.io/0MGGecVSSkunT5DWAHFC9Q' 
        driver.get(url)
        if not driver.current_url == url:
            raise Exception('get url failed')

        result = driver
    except:
        logger.debug('--------- Test create browser without session: FAILED ---------')
        result = False
        raise

    logger.debug('--------- Test create browser without session: SUCCESS ---------')
    return result

def test_login_with_account(driver):
    result = None

    logger.debug('--------- Test login with email and password: START ---------')
    try:
        from settings import FB_EMAIL, FB_PASSWORD
        email = FB_EMAIL
        password = FB_PASSWORD 
        login_with_account(driver=driver, email=email, password=password)

        result = True
    except:
        logger.debug('--------- Test login with email and password: FAILED ---------')
        result = False
        raise

    logger.debug('--------- Test login with email and password: SUCCESS ---------')
    return result

def test_is_login_success(driver):  
    result = None

    # test_is_login_success
    logger.debug('--------- Test is login success: START ---------')
    try:
        if not is_login_success(driver):
            raise Exception('Login failed')

        result = True
    except:
        logger.debug('--------- Test is login success: FAILED ---------')
        result = False
        raise

    logger.debug('--------- Test is login success: SUCCESS ---------')    
    return result

def test_all():
    import new_facebook as nf

    driver = test_create_driver_without_session()
    test_login_with_account(driver)
    test_is_login_success(driver)

    driver.close()
    driver.quit()

    logger.debug()
    
if __name__ == '__main__':
    test_all()
