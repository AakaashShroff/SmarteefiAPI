import os
import sys
import time
import threading
from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementClickInterceptedException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# Load environment variables from environment_keys.env
load_dotenv('environment_keys.env')

LOGIN_URL = "https://smarteefi.web.app/login"
EMAIL = os.getenv("SMARTEEFI_EMAIL")
PASSWORD = os.getenv("SMARTEEFI_PASSWORD")

if not EMAIL or not PASSWORD:
    print("Error: SMARTEEFI_EMAIL and SMARTEEFI_PASSWORD must be set in environment_keys.env")
    sys.exit(1)

app = Flask(__name__)

# Initialize a threading lock to manage WebDriver access
driver_lock = threading.Lock()
driver = None  # Will hold the WebDriver instance

def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    # Uncomment the next line to run Chrome in headless mode
    # chrome_options.add_argument("--headless")
    driver_instance = webdriver.Chrome(options=chrome_options)
    return driver_instance

def perform_login(driver):
    try:
        driver.get(LOGIN_URL)
        wait = WebDriverWait(driver, 60)

        # Enter email
        email_input = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Enter your email']"))
        )
        email_input.clear()
        email_input.send_keys(EMAIL)
        print("Entered email.")

        # Click Login/Signup button
        login_button = driver.find_element(By.XPATH, "//ion-button[contains(., 'Login/Signup')]")
        login_button.click()
        print("Clicked Login/Signup button.")

        # Wait for password page to load
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter your password']")))
        print("Password page loaded.")

        # Enter password
        password_input = driver.find_element(By.XPATH, "//input[@placeholder='Enter your password']")
        password_input.clear()
        password_input.send_keys(PASSWORD)
        print("Entered password.")

        # Click Login button
        submit_button = driver.find_element(By.XPATH, "//ion-button[contains(., 'Login') and not(contains(., 'Signup'))]")
        submit_button.click()
        print("Clicked Login button.")

        # Wait for dashboard to load
        wait.until(EC.presence_of_element_located((By.XPATH, "//ion-tab-bar")))
        print("Login successful.")
        time.sleep(5)  # Reduced sleep time for efficiency
    except TimeoutException:
        print("Login failed: Timeout while trying to log in.")
        driver.quit()
        sys.exit()
    except NoSuchElementException as e:
        print(f"Login failed: Element not found. {e}")
        driver.quit()
        sys.exit()
    except Exception as e:
        print(f"An unexpected error occurred during login: {e}")
        driver.quit()
        sys.exit()

def select_nikoo_home(driver):
    try:
        wait = WebDriverWait(driver, 60)

        # Wait until no overlays are present
        try:
            wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "ion-backdrop")))
            print("No overlays present.")
        except TimeoutException:
            print("Overlay is still present. Waiting for it to disappear.")
            wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "ion-backdrop")))
            print("Overlay has disappeared.")

        # Click Home dropdown
        dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//ion-select")))
        dropdown.click()
        print("Clicked Home dropdown.")

        # Wait for alert popup
        alert_xpath = "//div[contains(@class, 'alert-wrapper') and contains(@class, 'ion-overlay-wrapper')]"
        wait.until(EC.visibility_of_element_located((By.XPATH, alert_xpath)))
        print("Alert popup appeared.")

        # Select 'Nikoo' option
        nikoo_button_xpath = "//div[contains(@class, 'alert-wrapper')]//div[@class='alert-radio-label sc-ion-alert-md' and contains(text(), 'Nikoo')]/ancestor::button"
        nikoo_buttons = driver.find_elements(By.XPATH, nikoo_button_xpath)
        print(f"Number of 'Nikoo' buttons found: {len(nikoo_buttons)}")
        if not nikoo_buttons:
            print("No 'Nikoo' button found.")
            return
        nikoo_button = nikoo_buttons[0]
        nikoo_button.click()
        print("Selected 'Nikoo' option.")

        # Click 'Okay' button to confirm
        okay_button_xpath = "//div[contains(@class, 'alert-wrapper')]//button/span[text()='Okay']"
        okay_buttons = driver.find_elements(By.XPATH, okay_button_xpath)
        print(f"Number of 'Okay' buttons found: {len(okay_buttons)}")
        if not okay_buttons:
            print("No 'Okay' button found.")
            return
        okay_button = okay_buttons[0]
        okay_button.click()
        print("Clicked 'Okay' button.")

        # Wait for alert popup to disappear
        wait.until(EC.invisibility_of_element_located((By.XPATH, alert_xpath)))
        print("'Nikoo' selection confirmed.")
    except TimeoutException:
        print("Failed to select 'Nikoo': Timeout while waiting for elements.")
        driver.quit()
        sys.exit()
    except NoSuchElementException as e:
        print(f"Failed to select 'Nikoo': Element not found. {e}")
        driver.quit()
        sys.exit()
    except Exception as e:
        print(f"An unexpected error occurred while selecting 'Nikoo': {e}")
        driver.quit()
        sys.exit()

def toggle_switch(driver, switch_label, hidden_input_name, desired_state):
    try:
        wait = WebDriverWait(driver, 60)

        # Locate the toggle element
        ion_toggle_xpath = f"//ion-item[ion-label/h2[contains(text(), '{switch_label}')]]//ion-toggle"
        ion_toggle_elements = driver.find_elements(By.XPATH, ion_toggle_xpath)
        print(f"Number of ion-toggle elements found for '{switch_label}': {len(ion_toggle_elements)}")
        if not ion_toggle_elements:
            print(f"No ion-toggle element found for '{switch_label}'.")
            return False, f"No ion-toggle element found for '{switch_label}'."
        ion_toggle = ion_toggle_elements[0]

        # Scroll the toggle into view using scrollIntoView
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", ion_toggle)
        print("Scrolled the toggle into view.")
        time.sleep(1)  # Allow time for scrolling

        # Use ActionChains to move to the toggle element
        actions = ActionChains(driver)
        actions.move_to_element(ion_toggle).perform()
        print("Moved to the toggle element using ActionChains.")
        time.sleep(1)  # Allow time for movement

        # Wait until no overlays are present
        try:
            wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "ion-backdrop")))
            print("No overlays present.")
        except TimeoutException:
            print("Overlay is still present. Waiting for it to disappear.")
            wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "ion-backdrop")))
            print("Overlay has disappeared.")

        if ion_toggle.is_displayed() and ion_toggle.is_enabled():
            print("Toggle is visible and enabled.")
        else:
            print("Toggle is either not visible or not enabled.")
            return False, "Toggle is either not visible or not enabled."

        # JavaScript to get the hidden input's value within the toggle element
        js = f"""
            var elem = arguments[0].querySelector('input[name="{hidden_input_name}"]');
            return elem ? elem.value : null;
        """
        current_value = driver.execute_script(js, ion_toggle)
        is_on = current_value == "on"
        print(f"The {switch_label} is currently {'ON' if is_on else 'OFF'}.")

        desired_state_bool = desired_state.lower() == "on"

        if desired_state_bool != is_on:
            try:
                # Click the toggle via JavaScript
                driver.execute_script("arguments[0].click();", ion_toggle)
                print(f"Clicked the toggle to turn the {switch_label} {'ON' if desired_state_bool else 'OFF'}.")

                # Wait until the hidden input's value reflects the desired state
                wait.until(lambda d: d.execute_script(js, ion_toggle) == ("on" if desired_state_bool else ""))
                print(f"Successfully set the {switch_label} to {'ON' if desired_state_bool else 'OFF'}.")
                return True, f"Successfully set the {switch_label} to {'ON' if desired_state_bool else 'OFF'}."
            except TimeoutException:
                print(f"Failed to set the {switch_label} to {'ON' if desired_state_bool else 'OFF'}. The state did not change in time.")
                return False, f"Failed to set the {switch_label} to {'ON' if desired_state_bool else 'OFF'}."
            except ElementClickInterceptedException:
                print("Unable to click the toggle. It might be covered by another element.")
                time.sleep(5)
                try:
                    driver.execute_script("arguments[0].click();", ion_toggle)
                    print(f"Successfully clicked the toggle after waiting. {switch_label} has been turned {'ON' if desired_state_bool else 'OFF'}.")

                    # Wait again for the state
                    wait.until(lambda d: d.execute_script(js, ion_toggle) == ("on" if desired_state_bool else ""))
                    print(f"Successfully set the {switch_label} to {'ON' if desired_state_bool else 'OFF'}.")
                    return True, f"Successfully set the {switch_label} to {'ON' if desired_state_bool else 'OFF'}."
                except Exception as e:
                    print(f"Still unable to click the toggle: {e}")
                    return False, f"Still unable to click the toggle: {e}"
            except Exception as e:
                print(f"An error occurred while toggling the {switch_label}: {e}")
                return False, f"An error occurred while toggling the {switch_label}: {e}"
        else:
            print(f"{switch_label.capitalize()} is already {'ON' if is_on else 'OFF'}.")
            return True, f"{switch_label.capitalize()} is already {'ON' if is_on else 'OFF'}."
    except TimeoutException:
        print("The toggle element was not found within the given time.")
        return False, "The toggle element was not found within the given time."
    except NoSuchElementException as e:
        print(f"Toggle element not found: {e}")
        return False, f"Toggle element not found: {e}"
    except Exception as e:
        print(f"An unexpected error occurred while toggling the {switch_label}: {e}")
        return False, f"An unexpected error occurred while toggling the {switch_label}: {e}"

@app.route('/lighton', methods=['POST'])
def light_on():
    with driver_lock:
        success, message = toggle_switch(driver, 'Switch-1', 'ion-tg-5', 'on')
    status_code = 200 if success else 400
    return jsonify({"success": success, "message": message}), status_code

@app.route('/lightoff', methods=['POST'])
def light_off():
    with driver_lock:
        success, message = toggle_switch(driver, 'Switch-1', 'ion-tg-5', 'off')
    status_code = 200 if success else 400
    return jsonify({"success": success, "message": message}), status_code

@app.route('/fanon', methods=['POST'])
def fan_on():
    with driver_lock:
        success, message = toggle_switch(driver, 'Fan-1', 'ion-tg-9', 'on')
    status_code = 200 if success else 400
    return jsonify({"success": success, "message": message}), status_code

@app.route('/fanoff', methods=['POST'])
def fan_off():
    with driver_lock:
        success, message = toggle_switch(driver, 'Fan-1', 'ion-tg-9', 'off')
    status_code = 200 if success else 400
    return jsonify({"success": success, "message": message}), status_code

@app.route('/chargeron', methods=['POST'])
def charger_on():
    with driver_lock:
        success, message = toggle_switch(driver, 'Switch-2', 'ion-tg-6', 'on')
    status_code = 200 if success else 400
    return jsonify({"success": success, "message": message}), status_code

@app.route('/chargeroff', methods=['POST'])
def charger_off():
    with driver_lock:
        success, message = toggle_switch(driver, 'Switch-2', 'ion-tg-6', 'off')
    status_code = 200 if success else 400
    return jsonify({"success": success, "message": message}), status_code

@app.route('/')
def index():
    return jsonify({"message": "Smarteefi Control API is running."})

def setup_driver():
    global driver
    driver = init_driver()
    perform_login(driver)
    select_nikoo_home(driver)
    print("Driver setup complete and ready to handle requests.")

if __name__ == "__main__":
    # Initialize the WebDriver only once before starting the app
    setup_driver()
    # Run the Flask app
    app.run(host='0.0.0.0', port=9000)
