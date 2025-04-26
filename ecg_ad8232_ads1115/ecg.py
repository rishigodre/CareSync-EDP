import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
from gpiozero import DigitalInputDevice

# Setup gpiozero for LO+ and LO- pins
lo_plus = DigitalInputDevice(14)  # GPIO14 (Pin 8)
lo_minus = DigitalInputDevice(15)  # GPIO15 (Pin 10)

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize ADS1115 ADC
ads = ADS1115(i2c)
ads.gain = 1  # Gain of 1x (±4.096V range)

# Setup channel (direct integer 0 means A0 pin)
chan = AnalogIn(ads, 0)

# Set up plot
fig, ax = plt.subplots()
x_len = 200         # Number of points to display
y_range = 32768     # 16-bit ADC range
xs = list(range(0, x_len))
ys = [0] * x_len
line, = ax.plot(xs, ys)
ax.set_ylim(-y_range, y_range)
ax.set_title('Real-Time ECG Signal')
ax.set_xlabel('Samples')
ax.set_ylabel('ADC Value')

# Animate function
def animate(i, ys):
    if lo_plus.value == 1 or lo_minus.value == 1:
        ecg_value = 0
        print("Lead off detected!")
    else:
        ecg_value = chan.value  # RAW ADC counts (-32768 to +32767)

    ys.append(ecg_value)
    ys = ys[-x_len:]

    line.set_ydata(ys)

    return line,

# Set up live animation
ani = animation.FuncAnimation(fig, animate, fargs=(ys,), interval=10, blit=True)

# Show plot
plt.show()
