import requests
from datetime import datetime

#res = requests.get("https://time.my-masjid.com/api/TimingsInfoScreen/GetMasjidTimings?GuidId=46c50796-75af-4b82-a501-224506680f66").json()

res = requests.get("https://time.my-masjid.com/api/TimingsInfoScreen/GetMasjidTimings?GuidId=4f14a4b0-4151-40d0-953f-d3f317a8d51c").json()

currentDay = datetime.now().day
currentMonth = datetime.now().month

result = [x for x in res['model']['salahTimings'] if x["day"]== currentDay and x["month"]==currentMonth]
print(result[0])