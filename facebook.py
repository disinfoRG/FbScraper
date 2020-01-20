import os
import json
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.common.exceptions import WebDriverException, NoSuchWindowException
from urllib3.exceptions import MaxRetryError

# self-defined
import helper

class Facebook:
    def __init__(self, email, password, browser_type, executable_path, is_headless):        
        self.email = email
        self.password = password
        self.browser_type = browser_type
        self.executable_path = executable_path
        self.is_headless = is_headless
        self.cookie_path = './{}_cookie.json'.format(email)
        self.session_path = './{}_session.json'.format(browser_type)
        self.entrance_url = 'https://www.facebook.com'
        self.driver = None
        self.session_status = self.configure_browser(browser_type, is_headless, executable_path)

    def start(self):
        if self.session_status == 'attached_session':
            return

        if self.is_login_success():
            return

        # sign in only if it is a new browser and not loggedin
        self.login()

    def login(self):
        if self.has_cookie():
            self.login_with_cookie()
        else:
            self.login_with_account()

        if self.is_login_success():
            self.save_cookie()

    def has_cookie(self):
        return os.path.exists(self.cookie_path)
    def has_session(self):
        return os.path.exists(self.session_path)

    def is_login_success(self, timeout=20):
        logined_selector = '#sideNav'

        try:
            helper.wait_element(logined_selector, self.driver)
            print(' -----  login success')
            return True
        except:
            return False

    def login_with_cookie(self):
        print(' -----  login_with_cookie')

        if self.has_cookie():
            cookie_list = []
            with open(self.cookie_path, 'r', encoding='utf-8') as f:
                cookie_list = json.loads(f.read())
            if len(cookie_list) > 0:
                self.driver.get(self.entrance_url)
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
        try:
            helper.keyin_by_selector('#email', self.email, self.driver, 5)
            helper.keyin_by_selector('#pass', self.password, self.driver, 5)
            helper.click_without_move('#loginbutton', self.driver)
        except:
            pass

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

    def configure_browser(self, browser_type, is_headless, executable_path, tried_count=0):
        if tried_count > 2:
            raise Exception('Failed to configure browser (can be due to Network Error)')

        try:
            session = self.set_session(browser_type, is_headless, executable_path)

            # verify if the session work by checking if window with url exists or by connecting to a random site
            if self.driver.current_url is not None:
                pass
            else:
                self.min_reload_get(self.entrance_url)

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
        except Exception as e:
            helper.print_error(e)
        
        # create a new browser instead of using the previous
        if self.has_session():
            os.remove(self.session_path)
        
        tried_count += 1
        return self.configure_browser(browser_type, is_headless, executable_path, tried_count)

    def configure_headless_options(self, options):
        options.set_headless()
        options.add_argument("start-maximized"); # open Browser in maximized mode
        options.add_argument("disable-infobars"); # disabling infobars
        options.add_argument("--disable-extensions"); # disabling extensions
        options.add_argument("--disable-gpu"); # applicable to windows os only
        options.add_argument("--disable-dev-shm-usage"); # overcome limited resource problems
        options.add_argument("--no-sandbox"); # Bypass OS security model

    def set_session(self, browser_type, is_headless, executable_path):
        try:
            self.attach_to_session()
            return 'attached_session'
        except TypeError:
            # previous session not found
            pass
        except Exception as e:
            helper.print_error(e)
            pass

        # the selection of browser
        if browser_type == "Chrome":
            try:
                options = webdriver.ChromeOptions()

                if is_headless is True:
                    self.configure_headless_options(options)

                if executable_path is not None:
                    self.driver = webdriver.Chrome(executable_path=executable_path, options=options)
                else:
                    self.driver = webdriver.Chrome(options=options)
            except AttributeError as e:
                helper.print_error(e)
                pass

        if browser_type == "Firefox":
            try:
                options = webdriver.FirefoxOptions()
                if is_headless is True:
                    self.configure_headless_options(options)

                if executable_path is not None:
                    self.driver = webdriver.Firefox(executable_path=executable_path, options=options)
                else:
                    self.driver = webdriver.Firefox(options=options)
            except AttributeError as e:
                helper.print_error(e)
                pass

        # save browser's info for reusage
        executor_url = self.driver.command_executor._url
        session_id = self.driver.session_id
        self.save_session(executor_url, session_id)

        return 'new_session'

    def get_session(self):
        print( " -----  loading previous browser's session")

        try:
            if self.has_session():
                with open(self.session_path, 'r', encoding='utf-8') as f:
                    session = json.loads(f.read())        
                    executor_url = session['executor_url']
                    session_id = session['session_id']
                    print('executor_url: {}'.format(executor_url))
                    print('session_id: {}'.format(session_id))
                    print(" ----- previous browser's session loaded")        
                    return session
        except:
            return None

    def save_session(self, executor_url, session_id):
        print( " -----  saving browser's session")
        print('executor_url: {}'.format(executor_url))
        print('session_id: {}'.format(session_id))
        session = {
            'executor_url': executor_url,
            'session_id': session_id
        }
        json_session = json.dumps(session)
        with open(self.session_path, "w") as f:
            f.write(json_session)
            print(" ----- current browser's session made")

    def attach_to_session(self):
        session = self.get_session()
        self.driver = self.create_driver_with_session(session)
        
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
        except Exception as e:
            helper.print_error(e)        
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