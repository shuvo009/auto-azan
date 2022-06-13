# https://github.com/mozilla/geckodriver/releases

from tenacity import retry, wait_random_exponential, stop_after_attempt
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import schedule
import subprocess
import time
import datetime


LOCAL_MOSQUE = "https://www.rabita.no/"
GECKO_DRIVER = './geckodriver/geckodriver.exe'
AZAN_FILE = r"./azan.wav"
PLAYER = r"aplay"

@retry(wait=wait_random_exponential(multiplier=1, min=4, max=60), stop=stop_after_attempt(15))
def get_page_html():
    ser = Service(GECKO_DRIVER)
    firefox_options = Options()
    firefox_options.headless = True
    print("starting download content")

    with webdriver.Firefox(service=ser, options=firefox_options) as driver:
        driver.get(LOCAL_MOSQUE)
        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'responsiveExpander'))
        WebDriverWait(driver, 30).until(element_present)
        elem = driver.find_element(By.XPATH, "//*")
        source_code = elem.get_attribute("outerHTML")
        print("content downloaded")
        driver.quit()
        return source_code

def html_to_json(beautifulSoupContent):
    rows = beautifulSoupContent.find("tbody").find_all("tr")
    
    headers = {}
    thead = beautifulSoupContent.find("thead")
    if thead:
        thead = thead.find_all("th")
        for i in range(len(thead)):
            headers[i] = thead[i].text.strip().lower()
    data = []
    for row in rows:
        cells = row.find_all("td")
        if thead:
            items = {}
            for index in headers:
                items[headers[index]] = cells[index].text
        else:
            items = []
            for index in cells:
                items.append(index.text.strip())
        data.append(items)
    return data

def get_namaz_times(html):
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find(id="table_1")
    print("get content for azan times")
    namaz_times = html_to_json(content)
    namaz_time = namaz_times[0]
    namaz_time.pop('soloppgang', None)
    print("azan times are ready")
    return namaz_time

def azan():
    print("Playing azan")
    subprocess.call([PLAYER, AZAN_FILE], shell=True)

def schedule_azan():
    schedule.clear('azan')
    print("scheduled clear all exting azans")
    contents = get_page_html()
    times = get_namaz_times(contents)
    for key, value in times.items():
        if(can_schedule(value)):
            schedule.every().day.at(value).do(azan).tag('azan')
            print(key, value)
        else:
            print("Azan time passed for " + key + " Time "+ value)

    print("azans are sheduled")

def can_schedule(azan_time):
    current_time = datetime.datetime.now()
    current_hour = int(current_time.strftime("%H"))
    current_minutes = int(current_time.strftime("%M"))

    hour_and_minutes = azan_time.split(":")
    azan_hour = int(hour_and_minutes[0])
    azan_minute = int(hour_and_minutes[1])

    if (current_hour > azan_hour or current_minutes > azan_minute):
        return False
    return True

def schedule_refresh_azans():
    schedule.every().day.at("03:03").do(schedule_azan)
    print("scheduled schedule_refresh_azans")

print("@@@ Azan shedular get started @@@")
schedule_refresh_azans()
schedule_azan()

while True:
    schedule.run_pending()
    time.sleep(1)