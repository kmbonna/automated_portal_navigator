import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

import time
import sys
import os

# Configurable paths

# Determine if running as a bundled executable or as a script
if getattr(sys, 'frozen', False):
    # If running as a bundled executable, use the executable path
    base_path = sys._MEIPASS
else:
    # If running as a script, use the script path
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Chromedriver path
CHROMEDRIVER_PATH = os.path.join(base_path, 'chromedriver.exe')


EXCEL_FILE_PATH = 'modified_published_jobs.xlsx'

def find_toggle_and_save(driver):
    temp_state = "Not decided"
    try:
        job_board_button = WebDriverWait(driver, 50).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#job_boards > div.inline-block-card > div"))
        )
        time.sleep(1)
        job_board_button.click()
        time.sleep(1)
        
        toggle_all_button = WebDriverWait(driver, 50).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "toggle-btn"))
        )
        time.sleep(1)
        toggle_all_button[0].click()
        time.sleep(1)
        
        save_button = WebDriverWait(driver, 50).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[5]/div[1]/div/div/form/button[2]"))
        )
        time.sleep(1)
        save_button.click()
        time.sleep(3)

        # Check if the current URL is a 404 error page
        if "kalam.freshteam.com/404" in driver.current_url:
            driver.back()  # Navigate back
    except WebDriverException as e:
        print("Error in find_toggle_and_save:", str(e))
    else:
        temp_state = "Success"  # Change state only if no exception occurs
    
    return temp_state

def check_login(driver):
    try:
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, 'ember679'))
        )
        return True
    except:
        return False

def login_to_site(driver, urls):
    while True:
        user_input = input("Please log in through the browser and press any key to continue, type x at any time to exit: ").strip().lower()
        if user_input == 'x':
            sys.exit("User requested exit.")
        
        if check_login(driver):
            print("Login successful, continuing script...")
            return
        else:
            print("Login not completed. Please try again.")

def refresh_jobs(driver, df, urls):
    step = len(urls) // 10
    start_index = df[df['Refreshed?'] == "No"].index[0]
    print(f"Starting the automated refreshing process at row number {start_index + 2} at URL {urls[start_index]}")

    for i in range(start_index, len(urls)):
        state = "Offline"
        if i % step == 0:
            print(f"Progress: {round(i / len(urls) * 100)}% complete")
        
        try:
            driver.get(urls[i])
            status = find_toggle_and_save(driver)
            if status == "Success":
                state = "Offline"

            status = find_toggle_and_save(driver)
            if status == "Success":
                state = "Online"


            if state == "Online":
                df.at[i, 'Refreshed?'] = "Yes"

            df.to_excel(EXCEL_FILE_PATH, index=False)

        except WebDriverException as e:
            print(f"An error occurred when the state was '{state}' at URL: {urls[i]} with row number {i + 2}")
            print("Error details:", str(e))
    
    print("100% Completed, Done!")

def main():
    df = pd.read_excel(EXCEL_FILE_PATH, engine='openpyxl')
    urls = df['Jobs URL']

    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)

    driver.get(urls[0])
    login_to_site(driver, urls)
    refresh_jobs(driver, df, urls)

if __name__ == "__main__":
    main()
