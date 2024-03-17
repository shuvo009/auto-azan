from tenacity import retry, wait_random_exponential, stop_after_attempt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import schedule
import time
import datetime
import logging
import os
import requests
import pygame
from distutils.util import strtobool

logging.basicConfig(filename="log.txt",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

# set up logging to console
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
# set a format which is simpler for console use
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

API_BASE_URL = 'https://time.my-masjid.com/api/TimingsInfoScreen/GetMasjidTimings?GuidId={0}'
MASJID = '4f14a4b0-4151-40d0-953f-d3f317a8d51c'
OS_USER = os.getlogin()
LOCAL_MOSQUE = "https://www.rabita.no/"

def handle_dst(azan_time):
    """Return string"""
    minues = 60 if 3 < datetime.datetime.now().month < 11 else 0
    azan_h = int(azan_time.split(":")[0])
    azan_m = int(azan_time.split(":")[1])
    azan_dt = datetime.datetime.combine(datetime.date.today(), datetime.time(azan_h, azan_m)) + datetime.timedelta(minutes=minues)
    return azan_dt.strftime('%H:%M')

#Download Times Begin
@retry(wait=wait_random_exponential(multiplier=1, min=4, max=60), stop=stop_after_attempt(15))
def get_namaz_times_from_api():
    """Return No"""
    masjid_times = requests.get(API_BASE_URL.format(MASJID)).json()
    current_day = datetime.datetime.now().day
    current_month = datetime.datetime.now().month
    has_dst = masjid_times['model']['masjidSettings']['isDstOn']
    current_day_namaz_time = [x for x in masjid_times['model']['salahTimings']
                  if x["day"] == current_day and x["month"] == current_month][0]
    
    namaz_time = {
        "fajr": handle_dst(current_day_namaz_time['fajr']) if has_dst else current_day_namaz_time['fajr'],
        "zuhr": handle_dst(current_day_namaz_time['zuhr']) if has_dst else current_day_namaz_time['zuhr'],
        "asr":  handle_dst(current_day_namaz_time['asr']) if has_dst else current_day_namaz_time['asr'],
        "maghrib": handle_dst(current_day_namaz_time['maghrib']) if has_dst else current_day_namaz_time['maghrib'],
        "isha":  handle_dst(current_day_namaz_time['isha']) if has_dst else current_day_namaz_time['isha'],
    }

    logging.info("azan times are ready")
    return namaz_time

@retry(wait=wait_random_exponential(multiplier=1, min=4, max=60), stop=stop_after_attempt(15))
def get_page_html():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox");
    chrome_options.add_argument("--disable-dev-shm-usage");
    chrome_options.add_argument("--headless");
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

def get_namaz_times_from_html():
    html = get_page_html()
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find(id="table_1")
    logging.info("get content for azan times")
    namaz_times = html_to_json(content)
    namaz_time = namaz_times[0]
    namaz_time.pop('soloppgang', None)
    logging.info("azan times are ready")
    return namaz_time

def get_namaz_times():
    try:
        namz_time_html = get_namaz_times_from_html()
        logging.info("Times downloaded from HTML")
        return namz_time_html
    except:
        namaz_time_api = get_namaz_times_from_api()
        logging.info("Times downloaded from API")
        return namz_time_html

#Download Times Ends

def play_sound(sound_file):
    """Return No"""
    file_path = sound_file.format(OS_USER)
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue

def azan():
    """Return No"""
    logging.info("Playing azan")
    play_sound("/home/{0}/auto-azan/azan.wav")

def schedule_azan():
    """Return No"""
    schedule.clear('azan')
    logging.info("scheduled clear all exting azans")
    times = get_namaz_times()
    for key, value in times.items():
        if (can_schedule(value)):
            schedule.every().day.at(value).do(azan).tag('azan')
            logging.info(key + " " + value)
        else:
            logging.info("Azan time passed for " + key + " Time " + value)

    logging.info("azans are sheduled")

def can_schedule(azan_time):
    """Return No"""
    current_time = datetime.datetime.now()
    current_hour = int(current_time.strftime("%H"))
    current_minutes = int(current_time.strftime("%M"))

    hour_and_minutes = azan_time.split(":")
    azan_hour = int(hour_and_minutes[0])
    azan_minute = int(hour_and_minutes[1])

    if (current_hour > azan_hour):
        return False

    if (current_hour == azan_hour and current_minutes > azan_minute):
        return False

    return True

def reboot_system():
    """Return No"""
    os.system("sudo reboot")

def schedule_refresh_azans():
    """Return No"""
    schedule.every().day.at("03:00").do(reboot_system)
    logging.info("scheduled schedule_refresh_azans")

logging.info("@@@ Azan shedular get started @@@")
schedule_refresh_azans()
schedule_azan()

try:
    schedule_azan()
    play_sound("/home/{0}/auto-azan/startup.wav")
    logging.error("(*_*) Namaz time schedule successfully (*_*)")
except:
    logging.error("(-_-) Download namaz time failed (-_-)")

while True:
    schedule.run_pending()
    time.sleep(1)
