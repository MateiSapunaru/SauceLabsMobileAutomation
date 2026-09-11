from pathlib import Path

import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.appium_service import AppiumService

PROJECT_ROOT = Path(__file__).parent.parent
APP_PATH = PROJECT_ROOT / "apps" / "Android.SauceLabs.Mobile.Sample.app.2.7.1.apk"
AVD_NAME = "Pixel6_API34"
APPIUM_URL = "http://127.0.0.1:4723"


@pytest.fixture(scope="session")
def appium_server():
    service = AppiumService()
    service.start(args=["--address", "127.0.0.1", "--port", "4723"])
    yield service
    service.stop()


@pytest.fixture
def driver(appium_server):
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = AVD_NAME
    options.app = str(APP_PATH)
    options.new_command_timeout = 120
    # The app's launcher activity is a SplashActivity that redirects to MainActivity
    # after ~1-2s; without this, Appium's exact-activity-match wait fails because
    # by the time it polls, the app has already moved past SplashActivity.
    options.app_wait_activity = "com.swaglabsmobileapp.*"
    # CI runners are slower than a local dev machine; Appium's 20s defaults
    # for adb operations and installing its own uiautomator2-server APK are
    # too tight there and cause spurious session-setup timeouts.
    options.adb_exec_timeout = 60000
    options.uiautomator2_server_install_timeout = 60000

    driver = webdriver.Remote(APPIUM_URL, options=options)
    yield driver
    driver.quit()
