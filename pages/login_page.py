from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage


class LoginPage(BasePage):
    USERNAME_FIELD = (AppiumBy.ACCESSIBILITY_ID, "test-Username")
    PASSWORD_FIELD = (AppiumBy.ACCESSIBILITY_ID, "test-Password")
    LOGIN_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "test-LOGIN")
    # The "test-Error message" container has no text of its own; the actual
    # message lives in an unlabeled child TextView.
    ERROR_MESSAGE = (
        AppiumBy.XPATH,
        '//*[@content-desc="test-Error message"]//android.widget.TextView',
    )

    def is_displayed(self) -> bool:
        return self.wait_for_visible(self.USERNAME_FIELD).is_displayed()

    def login(self, username: str, password: str) -> None:
        self.wait_for_visible(self.USERNAME_FIELD).send_keys(username)
        self.driver.find_element(*self.PASSWORD_FIELD).send_keys(password)
        self.driver.find_element(*self.LOGIN_BUTTON).click()

    def error_message(self) -> str:
        return self.wait_for_visible(self.ERROR_MESSAGE).text
