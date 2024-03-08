import network
import secrets
from machine import Pin
from utime import sleep
import requests

import gc
gc.collect()

statusLeds = {
    "wlanActive": 18,
    "wlanConnected": 19,
    "requestSuccess": 20,
    "requestMade": 21
    }

def writeLed(address, state):
    led = Pin(address, Pin.OUT)
    if int(state):
        led.high()
    else:
        led.low()
        
def resetLeds():
    for led in statusLeds:
        writeLed(statusLeds[led], 0)
    
def indicateRequestStart():
    writeLed(statusLeds["requestMade"],1)
def indicateRequestStop():
    writeLed(statusLeds["requestMade"],0)


def initWifi():
    try:
        print('Connecting to WiFi Network Name:', secrets.SSID)
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True) # power up the WiFi chip
        writeLed(statusLeds["wlanActive"], 1)
    except:
        print("Failed to init")
        
    print('Waiting for wifi chip to power up...')
    sleep(3) # wait three seconds for the chip to power up and initialize
    wlan.connect(secrets.SSID, secrets.PASSWORD)
    print('Waiting for access point to log us in.')
    sleep(2)
    if wlan.isconnected():
      print('Success! We have connected to your access point!')
      print('Try to ping the device at', wlan.ifconfig()[0])
      writeLed(statusLeds["wlanConnected"], 1)
      if checkRequest():
          return True
      else:
          return False
    else:
      print('Failure! We have not connected to your access point!  Check your secrets.py file for errors.')
      writeLed(statusLeds["wlanActive"],0)
      writeLed(statusLeds["wlanConnected"], 0)
      writeLed(statusLeds["requestSuccess"],0)
      return False
      

def checkRequest():
    indicateRequestStart()
    try:
        r = requests.get('https://httpbin.org/basic-auth/user/pass', auth=('user', 'pass'), timeout=10)
        indicateRequestStop()
        if r.status_code == 200:
            r.close()
            print("Request check succeded")
            writeLed(statusLeds["requestSuccess"],1)
            return True
        else:
            r.close()
            print("Request check failed")
            writeLed(statusLeds["requestSuccess"],0)
            return False
    except:
        return False


def main():
    while True:
        resetLeds()
        met = True
        while met:
            if initWifi():
                break
        
        while True:
            sleep(10)
            checkRequest()
    
main()