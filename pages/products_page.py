from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage
from pages.cart_page import CartPage


class ProductsPage(BasePage):
    PRODUCTS_TITLE = (AppiumBy.ACCESSIBILITY_ID, "test-PRODUCTS")
    ITEM_TITLES = (AppiumBy.ACCESSIBILITY_ID, "test-Item title")
    CART_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "test-Cart")
    # The cart icon's own container carries no text; the item-count badge is
    # an unlabeled child TextView, same pattern as the login error message.
    CART_BADGE = (
        AppiumBy.XPATH,
        '//*[@content-desc="test-Cart"]//android.widget.TextView',
    )

    def is_displayed(self) -> bool:
        return self.wait_for_visible(self.PRODUCTS_TITLE).is_displayed()

    def product_titles(self) -> list[str]:
        self.wait_for_visible(self.PRODUCTS_TITLE)
        return [el.text for el in self.driver.find_elements(*self.ITEM_TITLES)]

    def add_to_cart(self, product_name: str) -> None:
        locator = (
            AppiumBy.XPATH,
            f'//*[@content-desc="test-Item"][.//*[@text="{product_name}"]]'
            '//*[@content-desc="test-ADD TO CART"]',
        )
        self.wait_for_visible(locator).click()

    def cart_badge_count(self) -> str:
        return self.wait_for_visible(self.CART_BADGE).text

    def open_cart(self) -> CartPage:
        self.driver.find_element(*self.CART_BUTTON).click()
        return CartPage(self.driver)
