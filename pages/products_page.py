from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage


class ProductsPage(BasePage):
    PRODUCTS_TITLE = (AppiumBy.ACCESSIBILITY_ID, "test-PRODUCTS")

    def is_displayed(self) -> bool:
        return self.wait_for_visible(self.PRODUCTS_TITLE).is_displayed()
