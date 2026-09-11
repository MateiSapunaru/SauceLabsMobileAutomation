import pytest

from pages.login_page import LoginPage
from pages.products_page import ProductsPage

VALID_PASSWORD = "secret_sauce"


def test_valid_login_shows_products(driver):
    login_page = LoginPage(driver)
    login_page.login("standard_user", VALID_PASSWORD)

    products_page = ProductsPage(driver)
    assert products_page.is_displayed()


@pytest.mark.parametrize(
    "username, password, expected_error",
    [
        (
            "locked_out_user",
            VALID_PASSWORD,
            "Sorry, this user has been locked out.",
        ),
        (
            "nonexistent_user",
            "wrong_password",
            "Username and password do not match any user in this service.",
        ),
    ],
    ids=["locked_out_user", "unrecognized_credentials"],
)
def test_invalid_login_shows_error(driver, username, password, expected_error):
    login_page = LoginPage(driver)
    login_page.login(username, password)

    assert login_page.error_message() == expected_error
