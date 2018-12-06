
# they were native CircuitPython digital inputs/outputs.
# Author: Tony DiCola
import time

import board
import busio
import digitalio

import adafruit_mcp230xx

# Initialize the I2C bus:
i2c = busio.I2C(board.SCL, board.SDA)

# Create an instance of either the MCP23008 or MCP23017 class depending on
# which chip you're using:
mcp = adafruit_mcp230xx.MCP23017(i2c)  # MCP23017

# Optionally change the address of the device if you set any of the A0, A1, A2
# pins.  Specify the new address with a keyword parameter:
# mcp = adafruit_mcp230xx.MCP23017(i2c, address=0x21)  # MCP23017 w/ A0 set

# Now call the get_pin function to get an instance of a pin on the chip.
# This instance will act just like a digitalio.DigitalInOut class instance
# and has all the same properties and methods (except you can't set pull-down
# resistors, only pull-up!).  For the MCP23008 you specify a pin number from 0
# to 7 for the GP0...GP7 pins.  For the MCP23017 you specify a pin number from
# 0 to 15 for the GPIOA0...GPIOA7, GPIOB0...GPIOB7 pins (i.e. pin 12 is GPIOB4).
pin0 = mcp.get_pin(1)
pin1 = mcp.get_pin(2)

# Setup pin0 as an output that's at a high logic level.
pin0.switch_to_output(value=True)
pin1.switch_to_output(value=True)
# pin0.value = False
#
# time.sleep(0.5)
pin0.value = True
pin1.value = True
time.sleep(3)
pin0.value = False
time.sleep(2)
pin1.value = False
# while True:
#
#     # Blink pin 0 on and then off.
#
#     pin0.value = False
#     time.sleep(1)
#     pin0.value = True
#
#     time.sleep(0.5)
#     pin1.value = False
#     time.sleep(1)
#     pin1.value = True
#     print('ici')
# #     # Read pin 1 and print its state.
