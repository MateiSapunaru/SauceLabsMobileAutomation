# Sauce Labs Mobile Automation

[![CI](https://github.com/MateiSapunaru/SauceLabsMobileAutomation/actions/workflows/ci.yml/badge.svg)](https://github.com/MateiSapunaru/SauceLabsMobileAutomation/actions/workflows/ci.yml)

Appium and pytest test suite for Android, written against Sauce Labs' official sample mobile application. Covers login (valid and invalid credentials) and the product browsing and cart flow, with a Page Object Model structure and a GitHub Actions pipeline that runs the full suite on a hardware accelerated Android emulator on every push.

## Application under test

The suite runs against [saucelabs/sample-app-mobile](https://github.com/saucelabs/sample-app-mobile), Sauce Labs' own demo application, purpose built for Appium practice. Its UI elements carry explicit accessibility identifiers (`test-Username`, `test-LOGIN`, and so on) meant to make automation straightforward, and the login screen itself lists the accepted test users and shared password directly in the UI.

The repository is archived on GitHub. The last tagged release (2.7.1) is from November 2020, and the last non-documentation commit is from mid 2021. This is a deliberate choice rather than an oversight: the application is a fixed, stable target that will not change or break underneath the test suite for reasons outside of this project's control, which matters more for a demonstration suite than an actively maintained upstream would. The APK used for testing is downloaded directly from the project's GitHub Releases page rather than committed to this repository.

## Stack and reasoning

- **Python** with the official **Appium-Python-Client** and **pytest** as the test runner. pytest fixtures handle Appium server lifecycle and driver session setup/teardown cleanly, and `pytest.mark.parametrize` is used for the multiple invalid-login scenarios.
- **Page Object Model**, with a `BasePage` providing a shared explicit-wait helper (`WebDriverWait` plus `expected_conditions`) rather than relying on bare `find_element` calls or fixed sleeps.
- **GitHub Actions** with a Linux runner and a hardware accelerated Android emulator, instead of a hosted device farm. See the Continuous Integration section below for the reasoning.

## Project structure

```
.
├── .github/workflows/ci.yml     GitHub Actions pipeline
├── apps/                        downloaded APK, not committed (see .gitignore)
├── pages/
│   ├── base_page.py             shared explicit-wait helper
│   ├── login_page.py            login screen locators and actions
│   ├── products_page.py         product listing, add to cart, cart badge
│   └── cart_page.py             cart contents
├── tests/
│   ├── conftest.py              Appium server and driver fixtures
│   ├── test_login_smoke.py      sanity check that the app launches
│   ├── test_login.py            valid and invalid login
│   └── test_cart.py             product browsing and cart
├── pytest.ini
└── requirements.txt
```

## Local setup

### 1. Android SDK and emulator

Install [Android Studio](https://developer.android.com/studio). During setup, choose the Standard installation type, which installs the Android SDK, `adb`, the emulator, and a bundled JDK.

Open Android Studio, go to **Tools > Device Manager**, and create a virtual device:

- Device: Pixel 6
- System image: API 34, Google APIs, x86_64
- Accept the default AVD name (used below as `Pixel6_API34`, or adjust `AVD_NAME` in `tests/conftest.py` to match whatever name you choose)

Boot the emulator once from Device Manager and confirm it reaches the home screen before continuing.

Note that the CI pipeline runs against API 30 instead of API 34. This is intentional, not a mismatch: see BUG-005 in the Bugs section below for the reason.

### 2. Node.js and Appium

The Appium server itself runs on Node.js, independent of the Python client.

```bash
npm install -g appium
appium driver install uiautomator2
```

### 3. Python environment

```bash
python -m venv .venv
.venv\Scripts\activate      # on Windows
source .venv/bin/activate   # on macOS/Linux
pip install -r requirements.txt
```

### 4. The application APK

Download the Android build from the [sample-app-mobile releases page](https://github.com/saucelabs/sample-app-mobile/releases) and place it at `apps/Android.SauceLabs.Mobile.Sample.app.2.7.1.apk`. This path is what `tests/conftest.py` expects.

### 5. Running the tests

With the emulator booted:

```bash
pytest tests/ -v
```

`tests/conftest.py` starts and stops the Appium server itself through `AppiumService`, so there is no separate `appium` process to manage by hand.

## Test coverage

**Login** (`tests/test_login.py`)

- Valid login with `standard_user` reaches the products screen.
- Invalid login, parametrized over two distinct failure modes: `locked_out_user`, which the application specifically designates as a blocked account and returns a business rule error for, and a genuinely unrecognized username and password pair, which returns a different, generic error message.

**Product browsing and cart** (`tests/test_cart.py`)

- The products screen lists the expected product titles.
- Adding a specific named product to the cart (not simply "whichever button is first") updates the cart badge count and the product appears on the cart page.

**Smoke test** (`tests/test_login_smoke.py`)

- The application launches and the login screen renders. Kept separate from the behavioral login tests as a fast environment sanity check.

All credentials, error message text, and product names used in assertions were taken directly from the running application (via `uiautomator dump` and Appium's own `page_source`), not assumed or guessed from documentation.

## Bugs found during test development

Logged in the same format used to file a defect against an application or environment, since that is the actual output of this kind of work, not just the passing test at the end.

### BUG-001: Session creation fails with "SplashActivity never started"

**Component:** Appium session setup
**Environment:** Local Android 14 emulator (Pixel 6, API 34), Appium 3.7.0, appium-uiautomator2-driver 8.6.2

**Steps to reproduce:**
1. Start a new Appium session against the application using the default `app` capability, with no `appWaitActivity` override set.

**Expected result:** The session starts once the application has launched.

**Actual result:** Session creation fails with `Cannot start the 'com.swaglabsmobileapp' application ... 'com.swaglabsmobileapp.SplashActivity' never started`, even though the application launches normally when started manually through `adb shell am start`.

**Root cause:** The application's manifest declared launcher activity is `SplashActivity`, which redirects to `MainActivity` one to two seconds after launch. Appium's default session startup waits for the exact launcher activity to remain the resumed activity. By the time it polled, the application had already moved past `SplashActivity`.

**Resolution:** Set the `appWaitActivity` capability to a wildcard, `com.swaglabsmobileapp.*`, covering both activities. See `tests/conftest.py`.

### BUG-002: Element lookups fail intermittently right after session start

**Component:** Test implementation
**Environment:** Same as BUG-001, with that fix in place.

**Steps to reproduce:**
1. Start a session with the `appWaitActivity` fix from BUG-001 applied.
2. Immediately call `find_element` for an element on the login screen.

**Expected result:** The element is found once the login screen has rendered.

**Actual result:** `NoSuchElementException`. Appium considers the session ready as soon as the application process is on screen, which can be before the login screen itself has finished rendering.

**Root cause:** No explicit wait was used before interacting with the UI. `find_element` does not wait for an element to appear; it fails immediately if the element is not present at the moment of the call.

**Resolution:** Added a `wait_for_visible` helper to `BasePage`, built on `WebDriverWait` and `expected_conditions.visibility_of_element_located`, and used it in place of bare `find_element` calls throughout the page objects.

### BUG-003: Assertions against error and cart badge text return an empty string

**Component:** Application accessibility structure, test implementation
**Environment:** Same as BUG-001.

**Steps to reproduce:**
1. Trigger the login error state, for example by logging in as `locked_out_user`.
2. Locate the element with accessibility id `test-Error message` and read its `.text` property.

**Expected result:** The element's text matches the error message displayed on screen.

**Actual result:** `.text` returns an empty string. No exception is raised, so a direct assertion such as `error_message() == "Sorry, this user has been locked out."` fails with no indication of why. The same problem affects the cart item count badge on the element with accessibility id `test-Cart`.

**Root cause:** In both cases, the element carrying the accessibility identifier is a container view with no text content of its own. The actual text is rendered by an unlabeled child `TextView`.

**Resolution:** Used an XPath descendant selector to target the child `TextView` directly, for example `//*[@content-desc="test-Error message"]//android.widget.TextView`, instead of reading `.text` off the labeled container.

### BUG-004: All CI test runs fail at session setup with an adb timeout

**Component:** CI pipeline
**Environment:** GitHub Actions, `ubuntu-latest`, Android 14 emulator (API 34 at the time)

**Steps to reproduce:**
1. Push a commit that triggers the CI workflow.

**Expected result:** The test suite runs against the CI emulator the same way it runs locally.

**Actual result:** Every test fails during driver setup with `Error executing adbExec ... Command '...adb install ... appium-uiautomator2-server-v10.6.6.apk' timed out after 20000ms`.

**Root cause:** Appium installs its own uiautomator2-server companion APK on every new session. The default 20 second `adbExecTimeout` is not enough on the CI runner, which is measurably slower than local development hardware.

**Resolution:** Raised `adbExecTimeout` and `uiautomator2ServerInstallTimeout` to 60000ms each in `tests/conftest.py`. A subsequent run also hit the 90 second default `androidInstallTimeout` while installing the application itself, so that was raised to 300000ms as well.

### BUG-005: CI emulator fails a Settings app readiness check on Android 13/14

**Component:** CI pipeline
**Environment:** GitHub Actions, `ubuntu-latest`, headless Android 14 emulator (API 34), with BUG-004 fixed.

**Steps to reproduce:**
1. Push a commit with the increased timeouts from BUG-004 in place.

**Expected result:** The session starts successfully once the timeouts are no longer the limiting factor.

**Actual result:** Session creation fails with `Appium Settings app is not running after 30000ms`.

**Root cause:** Matches a known, unresolved upstream issue, [appium/appium#20074](https://github.com/appium/appium/issues/20074): headless Android 13 and 14 emulators fail an internal Appium readiness check for the `io.appium.settings` companion application. The local development AVD never hits this because it runs with an actual display, not headless.

**Resolution:** Targeted API 30 in the CI workflow instead of API 34. The application predates API 34 by several years and has no dependency on anything specific to it, and API 30 is not affected by the upstream issue.

### BUG-006: CI emulator system server crashes during boot

**Component:** CI pipeline
**Environment:** GitHub Actions, `ubuntu-latest`, API 30 emulator, with BUG-005 fixed.

**Steps to reproduce:**
1. Push a commit with the API level change from BUG-005 in place.

**Expected result:** The emulator boots in roughly the same time as it does locally, under two minutes, and stays stable through the action's post-boot setup.

**Actual result:** Boot took over six minutes, and shortly after "boot completed" was logged, the emulator's system server crashed with `android.os.DeadSystemException` while the action was still configuring the device, aborting the run.

**Root cause:** `reactivecircus/android-emulator-runner` requires a separate step granting the CI runner access to `/dev/kvm` on Linux. This is documented in the action's own README but was missed when the workflow was first written. Without it, QEMU silently falls back to fully software emulated CPU virtualization instead of hardware acceleration, which explains both the abnormally long boot time and the crash under the resulting sustained CPU load.

**Resolution:** Added the KVM group permissions step to `.github/workflows/ci.yml`. Workflow run time dropped from over twenty minutes to under four once this was in place.

## Continuous integration

The pipeline in `.github/workflows/ci.yml` runs on `ubuntu-latest`, boots a hardware accelerated Android emulator using `reactivecircus/android-emulator-runner`, and runs the full pytest suite against it on every push and pull request to `main`.

This intentionally does not use a cloud device farm, for a few concrete reasons:

- **Firebase Test Lab does not support Appium.** Its `gcloud firebase test android run` command only executes Espresso, UI Automator 2, Robo, and Game Loop tests, all of which run self-contained on the device. There is no way to point an external Appium WebDriver session at a Firebase Test Lab device.
- **AWS Device Farm and BrowserStack do support Appium**, but neither is free for ongoing use. AWS Device Farm gives a one-time 1,000 minute trial and then bills per device minute. BrowserStack's unlimited access requires applying to and being accepted into its Open Source Program, which is not something a CI pipeline can depend on with certainty.
- **A self-hosted, KVM-accelerated emulator in the CI runner itself has none of those dependencies.** It uses GitHub's own Actions minutes, requires no third party account, and cannot run out of a trial allowance partway through the project.

The trade-off is real device coverage and parallel execution across many devices at once, which a proper device farm provides and a single CI-hosted emulator does not. For a project of this scope, a deterministic, zero-cost pipeline was judged more valuable than that coverage.

## Screenshot

<img src="docs/screenshots/login_screen.png" alt="Sample app login screen running on the local emulator" width="360">

Sample application running on the local Pixel 6, API 34 emulator described above.

## Possible extensions

- A cross-device or cross-OS-version test to demonstrate parametrizing over multiple emulator configurations, deliberately left out of the initial scope to keep the suite focused.
- iOS coverage, using the same application's iOS build and the corresponding Appium XCUITest driver.
