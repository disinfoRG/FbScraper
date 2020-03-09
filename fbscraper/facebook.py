from selenium import webdriver
from selenium.common.exceptions import NoSuchWindowException, TimeoutException
import re
import logging

logger = logging.getLogger(__name__)

# self-defined
from .helper import helper


class SecurityCheckError(Exception):
    pass


def create_driver_without_session(
    browser_type="Chrome", executable_path=None, is_headless=True
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

    helper.keyin_by_selector("#email", email, driver, 5)
    helper.keyin_by_selector("#pass", password, driver, 5)
    helper.click_without_move("#loginbutton", driver)


def is_login_success(driver, timeout=10):
    try:
        helper.wait_element_by_selector(
            selector="#sideNav", driver=driver, timeout=timeout
        )
        logger.info(" -----  login success")
        result = True
    except TimeoutException:
        result = False

    return result


def raise_if_security_check(driver):
    logger.debug(" ----- checking if encountered facebook's security check")

    # scroll to trigger any hidden security check
    helper.scroll(driver)

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
