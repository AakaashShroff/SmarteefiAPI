import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementClickInterceptedException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
from dotenv import load_dotenv

load_dotenv('environment_keys.env')

LOGIN_URL = "https://smarteefi.web.app/login"
EMAIL = os.getenv("SMARTEEFI_EMAIL")
PASSWORD = os.getenv("SMARTEEFI_PASSWORD")

if not EMAIL or not PASSWORD:
    print("Error: SMARTEEFI_EMAIL and SMARTEEFI_PASSWORD must be set in environment_keys.env")
    sys.exit(1)

def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def perform_login(driver):
    try:
        driver.get(LOGIN_URL)
        wait = WebDriverWait(driver, 60)
        email_input = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Enter your email']"))
        )
        email_input.clear()
        email_input.send_keys(EMAIL)
        print("Entered email.")
        login_button = driver.find_element(By.XPATH, "//ion-button[contains(., 'Login/Signup')]")
        login_button.click()
        print("Clicked Login/Signup button.")
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter your password']")))
        print("Password page loaded.")
        password_input = driver.find_element(By.XPATH, "//input[@placeholder='Enter your password']")
        password_input.clear()
        password_input.send_keys(PASSWORD)
        print("Entered password.")
        submit_button = driver.find_element(By.XPATH, "//ion-button[contains(., 'Login') and not(contains(., 'Signup'))]")
        submit_button.click()
        print("Clicked Login button.")
        wait.until(EC.presence_of_element_located((By.XPATH, "//ion-tab-bar")))
        print("Login successful.")
        time.sleep(10)
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
        dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//ion-select")))
        dropdown.click()
        print("Clicked Home dropdown.")
        alert_xpath = "//div[contains(@class, 'alert-wrapper') and contains(@class, 'ion-overlay-wrapper')]"
        wait.until(EC.visibility_of_element_located((By.XPATH, alert_xpath)))
        print("Alert popup appeared.")
        nikoo_button_xpath = "//div[contains(@class, 'alert-wrapper')]//div[@class='alert-radio-label sc-ion-alert-md' and text()='Nikoo ']/ancestor::button"
        nikoo_buttons = driver.find_elements(By.XPATH, nikoo_button_xpath)
        print(f"Number of 'Nikoo' buttons found: {len(nikoo_buttons)}")
        if not nikoo_buttons:
            print("No 'Nikoo' button found.")
            return
        nikoo_button = nikoo_buttons[0]
        nikoo_button.click()
        print("Selected 'Nikoo' option.")
        okay_button_xpath = "//div[contains(@class, 'alert-wrapper')]//button/span[text()='Okay']"
        okay_buttons = driver.find_elements(By.XPATH, okay_button_xpath)
        print(f"Number of 'Okay' buttons found: {len(okay_buttons)}")
        if not okay_buttons:
            print("No 'Okay' button found.")
            return
        okay_button = okay_buttons[0]
        okay_button.click()
        print("Clicked 'Okay' button.")
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

def toggle_switch(driver, switch_label, hidden_input_name):
    try:
        wait = WebDriverWait(driver, 60)
        ion_toggle_xpath = f"//ion-item[ion-label/h2[contains(text(), '{switch_label}')]]//ion-toggle"
        ion_toggle_elements = driver.find_elements(By.XPATH, ion_toggle_xpath)
        print(f"Number of ion-toggle elements found for '{switch_label}': {len(ion_toggle_elements)}")
        if not ion_toggle_elements:
            print(f"No ion-toggle element found for '{switch_label}'.")
            return
        ion_toggle = ion_toggle_elements[0]
        if ion_toggle.is_displayed() and ion_toggle.is_enabled():
            print("Toggle is visible and enabled.")
        else:
            print("Toggle is either not visible or not enabled.")
            return
        js = f"""
            var elem = document.querySelector('input[name="{hidden_input_name}"]');
            return elem ? elem.value : null;
        """
        current_value = driver.execute_script(js)
        is_on = current_value == "on"
        print(f"The {switch_label} is currently {'ON' if is_on else 'OFF'}.")
        while True:
            user_input = input(f"Do you want to turn the {switch_label} ON or OFF? (Enter 'on' or 'off'): ").strip().lower()
            if user_input in ["on", "off"]:
                break
            else:
                print("Invalid input. Please enter 'on' or 'off'.")
        desired_state = user_input == "on"
        if desired_state != is_on:
            try:
                driver.execute_script("arguments[0].click();", ion_toggle)
                print(f"Clicked the toggle to turn the {switch_label} {'ON' if desired_state else 'OFF'}.")
                time.sleep(2)
                new_value = driver.execute_script(js)
                new_state = new_value == "on"
                if new_state == desired_state:
                    print(f"Successfully set the {switch_label} to {'ON' if desired_state else 'OFF'}.")
                else:
                    print(f"Failed to set the {switch_label} to {'ON' if desired_state else 'OFF'}.")
            except ElementClickInterceptedException:
                print("Unable to click the toggle. It might be covered by another element.")
                time.sleep(5)
                try:
                    driver.execute_script("arguments[0].click();", ion_toggle)
                    print(f"Successfully clicked the toggle after waiting. {switch_label} has been turned {'ON' if desired_state else 'OFF'}.")
                    time.sleep(2)
                    new_value = driver.execute_script(js)
                    new_state = new_value == "on"
                    if new_state == desired_state:
                        print(f"Successfully set the {switch_label} to {'ON' if desired_state else 'OFF'}.")
                    else:
                        print(f"Failed to set the {switch_label} to {'ON' if desired_state else 'OFF'}.")
                except Exception as e:
                    print(f"Still unable to click the toggle: {e}")
            except Exception as e:
                print(f"An error occurred while toggling the {switch_label}: {e}")
        else:
            print(f"{switch_label.capitalize()} is already {'ON' if is_on else 'OFF'}.")
    except TimeoutException:
        print("The toggle element was not found within the given time.")
    except NoSuchElementException as e:
        print(f"Toggle element not found: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while toggling the {switch_label}: {e}")

def main():
    driver = init_driver()
    try:
        perform_login(driver)
        select_nikoo_home(driver)
        while True:
            switch = input("Which switch do you want to toggle? (Enter 'light', 'charger', or 'exit' to quit): ").strip().lower()
            if switch == 'light':
                toggle_switch(driver, 'Switch-1', 'ion-tg-5')
            elif switch == 'charger':
                toggle_switch(driver, 'Switch-2', 'ion-tg-6')
            elif switch == 'exit':
                print("Exiting the script.")
                break
            else:
                print("Invalid input. Please enter 'light', 'charger', or 'exit'.")
    finally:
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    main()
