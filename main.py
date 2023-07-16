from tenacity import retry, wait_random_exponential, stop_after_attempt
import schedule
import time
import datetime
import logging
import os
import requests
import pygame

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


@retry(wait=wait_random_exponential(multiplier=1, min=4, max=60), stop=stop_after_attempt(15))
def get_namaz_times():
    """Return No"""
    masjid_times = requests.get(API_BASE_URL.format(MASJID)).json()
    current_day = datetime.datetime.now().day
    current_month = datetime.datetime.now().month

    current_day_namaz_time = [x for x in masjid_times['model']['salahTimings']
                  if x["day"] == current_day and x["month"] == current_month][0]
    
    namaz_time = {
        "fajr": current_day_namaz_time['fajr'],
        "zuhr": current_day_namaz_time['zuhr'],
        "asr": current_day_namaz_time['asr'],
        "maghrib": current_day_namaz_time['maghrib'],
        "isha": current_day_namaz_time['isha'],
    }

    logging.info("azan times are ready")
    return namaz_time


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
    schedule.every().day.at("02:00").do(schedule_azan)
    logging.info("scheduled schedule_refresh_azans")


logging.info("@@@ Azan shedular get started @@@")
schedule_refresh_azans()
schedule_azan()
play_sound("/home/{0}/auto-azan/startup.wav")

while True:
    schedule.run_pending()
    time.sleep(1)
