import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

# setting pins 14 and 15 as input for AD8232
GPIO.setup(14, GPIO.IN)
GPIO.setup(15, GPIO.IN)

import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
import board
import busio
import adafruit_ads1x15.ads

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize ADC
ads = ADS1115(i2c)
ads.gain = 1  # You can adjust gain based on your signal range

# Choose channel 0
chan = AnalogIn(ads, adafruit_ads1x15.ads.P0)

# Set up plot
fig, ax = plt.subplots()
x_len = 200         # Number of points to display
y_range = 32768     # ADS1115 is a 16-bit ADC
xs = list(range(0, x_len))
ys = [0] * x_len
line, = ax.plot(xs, ys)
ax.set_ylim(-y_range, y_range)
ax.set_title('Real-Time ECG Signal')
ax.set_xlabel('Samples')
ax.set_ylabel('ADC Value')

# This function is called periodically from FuncAnimation
def animate(i, ys):
    # Read the ECG value
    ecg_value = chan.value

    # Add new reading and remove the oldest one
    ys.append(ecg_value)
    ys = ys[-x_len:]

    # Update the line
    line.set_ydata(ys)

    return line,

# Set up plot to call animate() function periodically
ani = animation.FuncAnimation(fig, animate, fargs=(ys,), interval=10, blit=True)

plt.show()


