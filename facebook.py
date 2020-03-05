import logging
logger = logging.getLogger(__name__)
import os
import json
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.common.exceptions import WebDriverException, NoSuchWindowException, TimeoutException
from urllib3.exceptions import MaxRetryError

# self-defined
from helper import helper

class Facebook:
    def __init__(self, email, password, browser_type, executable_path, is_headless=True, reuse_session_id=None):
        self.email = email
        self.password = password
        self.browser_type = browser_type
        self.executable_path = executable_path
        self.is_headless = is_headless
        self.reuse_session_id = reuse_session_id
        self.cookie_path = './{}_cookie.json'.format(email)
        self.session_path = None if not reuse_session_id else './{}_{}_working_session.json'.format(email, reuse_session_id)
        self.entrance_url = 'https://www.facebook.com'
        self.tmp_url = 'https://www.google.com'
        self.driver = None
        self.session_status = None

    def start(self, should_login=True):
        if should_login:
            self.session_status = self.configure_session()

            if self.session_status == 'attached_session':
                return

            if self.is_login_success():
                return

            # sign in only if it is a new browser and not loggedin
            self.login()
        else:
            self.configure_session(False)

    def login(self):
        if self.has_cookie():
            self.login_with_cookie()
        else:
            self.login_with_account()

        if self.is_login_success():
            self.save_cookie()

    def has_cookie(self):
        return self.cookie_path and os.path.exists(self.cookie_path)

    def has_session(self):
        return self.session_path and os.path.exists(self.session_path)

    def is_login_success(self, timeout=20):
        result = None
        logined_selector = '#sideNav'

        try:
            helper.wait_element_by_selector(logined_selector, self.driver)
            print(' -----  login success')
            result = True
        except TimeoutException:
            result = False

        return result

    def login_with_cookie(self):
        print(' -----  login_with_cookie')

        if self.has_cookie():
            cookie_list = []
            with open(self.cookie_path, 'r', encoding='utf-8') as f:
                cookie_list = json.loads(f.read())
            if len(cookie_list) > 0:
                self.driver.get(self.tmp_url)
                for c in cookie_list:
                    if 'expiry' in c:
                        cookie = {}
                        cookie['domain'] = c['domain']
                        cookie['name'] = c['name']
                        cookie['value'] = c['value']
                        cookie['path'] = c['path']
                        cookie['expiry'] = int(c['expiry'])
                        self.driver.add_cookie(cookie)
                self.driver.get(self.entrance_url)


    def login_with_account(self):
        print(' -----  login_with_account')
        self.min_reload_get(self.entrance_url)
        helper.keyin_by_selector('#email', self.email, self.driver, 5)
        helper.keyin_by_selector('#pass', self.password, self.driver, 5)
        helper.click_without_move('#loginbutton', self.driver)

    def save_cookie(self):
        cookie = json.dumps(self.driver.get_cookies())
        with open(self.cookie_path, 'w') as f:
            f.write(cookie)
            print(' -----  cookies saved')

    def min_reload_get(self, url):
        now_url = self.driver.current_url
        if now_url == url:
            return
        self.driver.get(url)

    def configure_session(self, should_use_remote_webdriver=True):
        return self.configure_browser(self.browser_type, self.is_headless, self.executable_path, self.reuse_session_id, should_use_remote_webdriver)

    def configure_browser(self, browser_type, is_headless, executable_path, reuse_session_id, should_use_remote_webdriver, tried_count=0):
        if tried_count > 2:
            raise Exception('Failed to configure browser (can be due to Network Error)')

        try:
            session = self.set_session(browser_type, is_headless, executable_path, reuse_session_id, should_use_remote_webdriver)

            # verify if the session work by checking if window with url exists or by connecting to a random site
            if self.driver.current_url is not None:
                pass
            else:
                self.min_reload_get(self.tmp_url)

            return session
        except NoSuchWindowException:
            # no such window: window was already closed
            # running webdriver(chromedriver, foxdriver) exists and session file exists, but caused by the browser window (not program, aka Chrome, Firefox) of the session file was closed, and get message like "chrome not reachable"
            pass
        except WebDriverException:
            # chrome not reachable
            # running webdriver(chromedriver, foxdriver) exists and session file exists, but caused by the browser program (aka Chrome, Firefox) of the session file was closed, and get message like "chrome not reachable"
            pass
        except  MaxRetryError:
            # Connection refused
            # casued session file exists, but running webdriver(chromedriver, foxdriver) is not found
            pass

        # create a new browser instead of using the previous
        if self.has_session():
            os.remove(self.session_path)

        tried_count += 1
        return self.configure_browser(browser_type, is_headless, executable_path, reuse_session_id, should_use_remote_webdriver, tried_count)

    def add_common_options(self, options):
        options.add_argument("--start-maximized"); # open Browser in maximized mode
        # options.add_argument("--disable-infobars"); # disabling infobars
        options.add_argument("--disable-extensions"); # disabling extensions
    def add_headless_options(self, options):
        options.headless = True
        options.add_argument("--disable-gpu"); # applicable to windows os only
        options.add_argument("--disable-dev-shm-usage"); # overcome limited resource problems
        options.add_argument("--no-sandbox"); # Bypass OS security model

    def set_session(self, browser_type, is_headless, executable_path, reuse_session_id, should_use_remote_webdriver):
        if should_use_remote_webdriver:
            if reuse_session_id is not None:
                try:
                    self.attach_to_session()
                    return 'attached_session'
                except TypeError:
                    # previous session not found
                    pass

        # the selection of browser
        if browser_type == "Chrome":
            options = webdriver.ChromeOptions()
            self.add_common_options(options)
            if is_headless is True:
                self.add_headless_options(options)

            if executable_path is not None:
                self.driver = webdriver.Chrome(executable_path=executable_path, options=options)
            else:
                self.driver = webdriver.Chrome(options=options)

        if browser_type == "Firefox":
            options = webdriver.FirefoxOptions()
            self.add_common_options(options)
            if is_headless is True:
                self.add_headless_options(options)

            if executable_path is not None:
                self.driver = webdriver.Firefox(executable_path=executable_path, options=options)
            else:
                self.driver = webdriver.Firefox(options=options)

        if should_use_remote_webdriver:
            # save browser's info for reusage
            executor_url = self.driver.command_executor._url
            session_id = self.driver.session_id
            self.save_session(executor_url, session_id)

            return 'new_session'

    def get_session(self):
        print( " -----  loading previous browser's session")
        result = None

        if self.has_session():
            with open(self.session_path, 'r', encoding='utf-8') as f:
                session = json.loads(f.read())
                executor_url = session['executor_url']
                session_id = session['session_id']
                print('executor_url: {}'.format(executor_url))
                print('session_id: {}'.format(session_id))
                print(" ----- previous browser's session loaded")
                result = session

        return result

    def save_session(self, executor_url, session_id):
        print( " -----  saving browser's session")
        print('executor_url: {}'.format(executor_url))
        print('session_id: {}'.format(session_id))
        session = {
            'executor_url': executor_url,
            'session_id': session_id
        }
        json_session = json.dumps(session)
        fpath = './{}_session_{}.json'.format(self.email, self.reuse_session_id)
        self.session_path = fpath
        with open(fpath, "w") as f:
            f.write(json_session)
            print(" ----- current browser's session made")

    def attach_to_session(self):
        session = self.get_session()
        self.driver = self.create_driver_with_session(session)

    @classmethod
    def create_driver_with_session(self, session):
        executor_url = session['executor_url']
        session_id = session['session_id']
        new_driver = None

        try:
            # Save the original function, so we can revert our patch
            org_command_execute = RemoteWebDriver.execute

            def new_command_execute(self, command, params=None):
                if command == "newSession":
                    # Mock the response
                    return {'success': 0, 'value': None, 'sessionId': session_id}
                else:
                    return org_command_execute(self, command, params)

            # Patch the function before creating the driver object
            RemoteWebDriver.execute = new_command_execute

            new_driver = webdriver.Remote(command_executor=executor_url, desired_capabilities={})
            new_driver.session_id = session_id

            # Replace the patched function with original function
            RemoteWebDriver.execute = org_command_execute
        except NoSuchWindowException:
            logger.error(helper.print_error(e))
            # try another way, which will create a new dummy window
            new_driver = webdriver.Remote(command_executor=executor_url, desired_capabilities={})
            new_driver.session_id = session_id

        return new_driver

def main():
    from settings import FB_EMAIL, FB_PASSWORD, CHROMEDRIVER_BIN
    fb = Facebook(FB_EMAIL, FB_PASSWORD, 'Chrome', CHROMEDRIVER_BIN, False)
    fb.login()
if __name__ == '__main__':
    main()
