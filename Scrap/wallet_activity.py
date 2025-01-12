import os
import json
import time
import random
import pandas as pd
import csv
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC


def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox') 
    chrome_options.add_argument('--disable-dev-shm-usage') 
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    chrome_options.add_argument(
        "--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-automation"])

    username = os.getlogin()
    chrome_options.add_argument(f"user-data-dir=C:/Users/{username}/AppData/Local/Google/Chrome/User Data")
    # chrome_options.add_argument("profile-directory=Default")
    # service = Service(ChromeDriverManager().install())
    service = Service(r"C:\Users\Ali Mirash\.wdm\drivers\chromedriver\win64\131.0.6778.264\chromedriver-win64\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def human_like_delay():
    time.sleep(random.uniform(3, 7))


def get_xhr_responses(driver ,logs):
    xhr_responses = []
    for entry in logs:
        log = json.loads(entry["message"])["message"]
        if (
            "Network.responseReceived" == log["method"]
            and log["params"]["type"] == "XHR"
        ):
            request_id = log["params"]["requestId"]
            response = log["params"]["response"]
            # Get the response body
            try:
                body = driver.execute_cdp_cmd(
                    "Network.getResponseBody", {"requestId": request_id}
                )
                xhr_responses.append(
                    {
                        "url": response["url"],
                        "status": response["status"],
                        "headers": response["headers"],
                        "body": body["body"],
                        "base64Encoded": body["base64Encoded"],
                    }
                )
            except Exception as e:
                print(f"Could not get body for request {request_id}: {e}")
    return xhr_responses

def wallet_scrap(address):
    driver = init_driver()
    try:
        target_url = f"https://gmgn.ai/sol/address/{address}"

        driver.get(target_url)

        # got_button = "css-147wlxj"
        # button_1 = WebDriverWait(driver, 50).until(
        #     EC.element_to_be_clickable((By.CLASS_NAME, got_button)))
        # button_1.click()
        # human_like_delay()
        D30 = '//*[@id="__next"]/div/div/main/div[2]/div[1]/div[2]/div[1]/div/div[2]'
        button_2 = WebDriverWait(driver, 50).until(
            EC.element_to_be_clickable((By.XPATH, D30)))
        button_2.click()
        human_like_delay()

        logs = driver.get_log("performance")
        xhr_responses = get_xhr_responses(driver ,logs)

        # Save to CSV
        csv_file = f"results/{address}.csv"
        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["url", "status", "headers", "body", "base64Encoded"])
            writer.writeheader()
            for response in xhr_responses:
                writer.writerow(response)

        # for idx, response in enumerate(xhr_responses, start=1):
        #     print(f"XHR Response {idx}:")
        #     print(f"URL: {response['url']}")
        #     print(f"Status: {response['status']}")
        #     print(f"Headers: {response['headers']}")
        #     print(f"Body: {response['body']}\n")

    finally:
        human_like_delay()
        driver.quit()
