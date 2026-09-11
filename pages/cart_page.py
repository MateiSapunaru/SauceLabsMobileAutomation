from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException

from pages.base_page import BasePage


class CartPage(BasePage):
    CART_CONTENT = (AppiumBy.ACCESSIBILITY_ID, "test-Cart Content")

    def is_displayed(self) -> bool:
        return self.wait_for_visible(self.CART_CONTENT).is_displayed()

    def contains_product(self, product_name: str) -> bool:
        locator = (
            AppiumBy.XPATH,
            f'//*[@content-desc="test-Cart Content"]//*[@text="{product_name}"]',
        )
        try:
            return self.driver.find_element(*locator).is_displayed()
        except NoSuchElementException:
            return False
