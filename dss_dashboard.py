import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from selenium.webdriver.firefox.service import Service
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv, find_dotenv
import os
from sentry_sdk import capture_exception

import os

#os.environ["TMPDIR"] = "/home/ryan/tmp"

load_dotenv(find_dotenv())  # Load the .env file


class WebAutomation:

    def __init__(self):
        self.driver = None

        try:
            options = FirefoxOptions()
            options.add_argument("--headless=new")
            options.headless = True

            # service = Service("/snap/bin/firefox.geckodriver")
            # self.driver = webdriver.Firefox(service=service)

            self.driver = webdriver.Firefox(options=options)

            # chrome_options = webdriver.ChromeOptions()
            # chrome_options.add_argument('--ignore-certificate-errors')
            # chrome_options.add_argument('--disable-dev-shm-usage')
            # chrome_options.add_argument('--disable-extensions')
            # chrome_options.add_argument('--no-sandbox')
            # chrome_options.add_argument('--disable-dev-shm-usage')
            # chrome_options.add_argument('--headless')
            #
            # self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            capture_exception(e)

    def zacks_dashboard(self):
        self.run_dashboard(
            '''https://shrimp-selected-dogfish.ngrok-free.app/projects/TAPREP/dashboards/3gdUKVN_TA%20Prep's%20default%20dashboard/view/TzDj7wW''')
            # 'http://localhost:11000/projects/TAPREP/dashboards/3gdUKVN_TA%20Prep\'s%20default%20dashboard/view/TzDj7wW')

    def run_dashboard(self, url):
        try:
            self.driver.delete_all_cookies()
            self.driver.get(url)

            login_elem = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "qa_login-page_input-login"))
            )

            login_elem.send_keys('admin')

            elem = self.driver.find_element(by=By.ID, value='qa_login-page_input-password')
            elem.send_keys(os.environ['DSS_PW'])

            elem = self.driver.find_element(by=By.XPATH, value='//button[text()="Log in"]')
            elem.click()

            print('logged in...')

            print('waiting for play...')
            run_btn = WebDriverWait(self.driver, 100).until(
                # EC.element_to_be_clickable((By.XPATH, 'div[ng-click="runNow()"]'))
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div > .icon-play"))
            )
            print('play found...')
            # action = ActionChains(driver)
            # action.move_to_element(run_btn).click().perform()

            run_btn.click()
            print('clicked run...')

            time.sleep(5)

        except Exception as e:
            capture_exception(e)

        finally:
            if self.driver:
                self.driver.close()

a = WebAutomation()
a.zacks_dashboard()