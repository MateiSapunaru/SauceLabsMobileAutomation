from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.webdriver import WebDriver

DEFAULT_TIMEOUT = 15


class BasePage:
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def wait_for_visible(self, locator, timeout: int = DEFAULT_TIMEOUT):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
