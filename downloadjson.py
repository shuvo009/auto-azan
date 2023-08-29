import requests
from datetime import datetime

#res = requests.get("https://time.my-masjid.com/api/TimingsInfoScreen/GetMasjidTimings?GuidId=46c50796-75af-4b82-a501-224506680f66").json()

#res = requests.get("https://time.my-masjid.com/api/TimingsInfoScreen/GetMasjidTimings?GuidId=4f14a4b0-4151-40d0-953f-d3f317a8d51c").json()

#currentDay = datetime.now().day
#currentMonth = datetime.now().month

#result = [x for x in res['model']['salahTimings'] if x["day"]== currentDay and x["month"]==currentMonth]
#print(result[0])
mytime = "03:21"

h = int(mytime.split(":")[0]);
m = int(mytime.split(":")[1]);
print(h)
print(m)
import datetime
from distutils.util import strtobool
#from datetime import date, datetime, time, timedelta
dt = datetime.datetime.combine(datetime.date.today(), datetime.time(h, m)) + datetime.timedelta(minutes=60)
print (dt.strftime('%H:%M'))

minues = 60 if 3 < datetime.datetime.now().month < 11 else 0

print( minues   )
#13:10:00

