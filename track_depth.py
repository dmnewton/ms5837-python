#!/usr/bin/python
import ms5837
import time

import requests

url_string = 'http://piserver.local:8086/write?db=home'

def sleep_gen(period):
    """use generator to create an accurate time intervals to send frames"""
    num = 0
    start_time = time.time()
    while True:
       sleeplength =  start_time + ( period * num ) - time.time()
       sleeplength = max(sleeplength,0)
       yield sleeplength
       num += 1


sensor = ms5837.MS5837_30BA() 

# We must initialize the sensor before reading it
if not sensor.init():
        print("Sensor could not be initialized")
        exit(1)

# We have to read values from sensor to update pressure and temperature
if not sensor.read():
    print("Sensor read failed!")
    exit(1)

print("Pressure: {:.3f} atm  {:.3f} Torr  {:.3f} psi".format(
sensor.pressure(ms5837.UNITS_atm),
sensor.pressure(ms5837.UNITS_Torr),
sensor.pressure(ms5837.UNITS_psi)))

print("Temperature: {:.3f} C  {:.3f} F  {:.3f} K".format(
sensor.temperature(ms5837.UNITS_Centigrade),
sensor.temperature(ms5837.UNITS_Farenheit),
sensor.temperature(ms5837.UNITS_Kelvin)))

sensor.setFluidDensity(1000) # kg/m^3
print("Depth: {:.3f} cm (freshwater)".format(sensor.depth() *100))

# fluidDensity doesn't matter for altitude() (always MSL air density)
print("MSL Relative Altitude: {:.3f} m".format(sensor.altitude())) # relative to Mean Sea Level pressure in air

time.sleep(2)

# Spew readings
sleeplength = sleep_gen(20)
        
while True:
        time.sleep(next(sleeplength))
        ts =time.time_ns()
        if sensor.read():
                print("Time: {} ns P: {:.3f} mbar  T: {:.3f} C  Depth: {:.3f} cm (freshwater)".format(
                ts,
                sensor.pressure(), # Default is mbar (no arguments)
                sensor.temperature(), # Default is degrees C (no arguments)
                sensor.depth()*100
                )) # Request Farenheit
                data_string = 'pressure,host=frontwindows depth={},temp={} {}'.format(sensor.depth()*100,sensor.temperature(),ts)

                r = requests.post(url_string, data=data_string)
        else:
                print("Sensor read failed!")