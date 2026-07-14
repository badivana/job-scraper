import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = "https://github.com/badivana"
REFRESH_COUNT = 300
DELAY_SECONDS = 1

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)

try:
    driver.get(URL)
    for i in range(REFRESH_COUNT):
        time.sleep(DELAY_SECONDS)
        driver.refresh()
        print(f"Refreshed {i + 1}/{REFRESH_COUNT}")
finally:
    driver.quit()