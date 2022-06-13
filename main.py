from tenacity import retry, wait_random_exponential, stop_after_attempt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import schedule
import subprocess
import time
import datetime
import logging

logging.basicConfig(filename="log.txt",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

# set up logging to console
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
# set a format which is simpler for console use
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

LOCAL_MOSQUE = "https://www.rabita.no/"
AZAN_FILE = r"./azan.wav"
PLAYER = r"aplay"

@retry(wait=wait_random_exponential(multiplier=1, min=4, max=60), stop=stop_after_attempt(15))
def get_page_html():
    chrome_options = Options()
    chrome_options.headless = True
    logging.info("starting download content")

    with webdriver.Chrome(options=chrome_options) as driver:
        driver.get(LOCAL_MOSQUE)
        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'responsiveExpander'))
        WebDriverWait(driver, 30).until(element_present)
        elem = driver.find_element(By.XPATH, "//*")
        source_code = elem.get_attribute("outerHTML")
        logging.info("content downloaded")
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
    logging.info("get content for azan times")
    namaz_times = html_to_json(content)
    namaz_time = namaz_times[0]
    namaz_time.pop('soloppgang', None)
    logging.info("azan times are ready")
    return namaz_time

def azan():
    logging.info("Playing azan")
    subprocess.call([PLAYER, AZAN_FILE], shell=True)

def schedule_azan():
    schedule.clear('azan')
    logging.info("scheduled clear all exting azans")
    contents = get_page_html()
    times = get_namaz_times(contents)
    for key, value in times.items():
        if(can_schedule(value)):
            schedule.every().day.at(value).do(azan).tag('azan')
            logging.info(key + " " + value)
        else:
            logging.info("Azan time passed for " + key + " Time "+ value)

    logging.info("azans are sheduled")

def can_schedule(azan_time):
    current_time = datetime.datetime.now()
    current_hour = int(current_time.strftime("%H"))
    current_minutes = int(current_time.strftime("%M"))

    hour_and_minutes = azan_time.split(":")
    azan_hour = int(hour_and_minutes[0])
    azan_minute = int(hour_and_minutes[1])

    if (current_hour > azan_hour):
        return False

    if(current_hour == azan_hour and current_minutes > azan_minute):
        return False

    return True

def schedule_refresh_azans():
    schedule.every().day.at("03:03").do(schedule_azan)
    logging.info("scheduled schedule_refresh_azans")

logging.info("@@@ Azan shedular get started @@@")
schedule_refresh_azans()
schedule_azan()

while True:
    schedule.run_pending()
    time.sleep(1)