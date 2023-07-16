
# Auto Azan For Norway

This script helps you to listen azan 5 times every day (alhamdulillah). This is a python script which can run at raspberry pi.



## License

It's open for all. I use [Rabita](https://www.rabita.no/) web site to get azan times. I ask them about permission, and they told me I can use it if I use it personally. So, you should ask for permission to them.
## Installation

1) Prepare your raspberry pi : https://www.raspberrypi.com/software/
2) Download Code at extract at ``` /home/{USER}/auto-azan ```
2) From Terminal ``` sudo apt install libsdl2-mixer-2.0-0 libsdl2-image-2.0-0 libsdl2-2.0-0 ```
3) From directory when you download : ``` pip install -r requirements.txt ```
4) From Terminal ``` sudo nano /etc/xdg/lxsession/LXDE-pi/autostart ```
5) Add this line : ``` @/usr/bin/python3 /home/pi/auto-azan/main.py ```
6) reboot your pi

## For Other Country or Mosque

It's basically make a api call to ``https://my-masjid.com/`` to get namaj times.
If you want to use this for other country you just need to change [MASJID](https://github.com/shuvo009/auto-azan/blob/52bbe234f7f8e3a9994520b574d100533b629409/main.py#L69)
and make it own.


## Donation

If you think this is help for you (alhamdulillah). Please pray for me and my family.

