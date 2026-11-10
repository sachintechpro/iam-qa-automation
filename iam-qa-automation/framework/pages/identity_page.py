"""Employer showcase: Selenium Page Object Model (POM).

Locators and waits are centralized here. Tests express *what* a user does,
not brittle low-level Selenium steps. Explicit waits avoid arbitrary sleeps.
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class IdentityPage:
    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 15)

    def open(self):
        self.driver.get(self.base_url)
        self.wait.until(EC.visibility_of_element_located((By.ID, 'username')))
        return self

    def login(self, username, password):
        Select(self.driver.find_element(By.ID, 'username')).select_by_visible_text(username)
        field = self.driver.find_element(By.ID, 'password')
        field.clear()
        field.send_keys(password)
        self.driver.find_element(By.ID, 'login').click()
        self.wait.until(lambda d: 'HTTP ' in d.find_element(By.ID, 'session').text or 'MFA is required' in d.find_element(By.ID, 'session').text)
        return self

    def session_text(self):
        return self.driver.find_element(By.ID, 'session').text

    def create_project(self, name):
        field = self.driver.find_element(By.ID, 'projectName')
        field.clear()
        field.send_keys(name)
        self.driver.find_element(By.ID, 'create').click()
        self.wait.until(lambda d: 'HTTP ' in d.find_element(By.ID, 'response').text)
        return self.driver.find_element(By.ID, 'response').text

    def logout(self):
        self.driver.find_element(By.ID, 'logout').click()
        self.wait.until(lambda d: 'HTTP 200' in d.find_element(By.ID, 'session').text)
        return self
