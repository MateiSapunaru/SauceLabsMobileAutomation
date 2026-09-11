from pages.login_page import LoginPage


def test_login_screen_loads(driver):
    login_page = LoginPage(driver)
    assert login_page.is_displayed()
