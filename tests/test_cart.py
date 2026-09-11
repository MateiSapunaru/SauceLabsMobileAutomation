from pages.login_page import LoginPage
from pages.products_page import ProductsPage

PRODUCT_NAME = "Sauce Labs Bike Light"


def _login_as_standard_user(driver):
    LoginPage(driver).login("standard_user", "secret_sauce")


def test_products_page_lists_known_items(driver):
    _login_as_standard_user(driver)
    products_page = ProductsPage(driver)

    assert products_page.is_displayed()
    assert PRODUCT_NAME in products_page.product_titles()


def test_add_product_to_cart_updates_badge_and_cart(driver):
    _login_as_standard_user(driver)
    products_page = ProductsPage(driver)

    products_page.add_to_cart(PRODUCT_NAME)
    assert products_page.cart_badge_count() == "1"

    cart_page = products_page.open_cart()
    assert cart_page.is_displayed()
    assert cart_page.contains_product(PRODUCT_NAME)
