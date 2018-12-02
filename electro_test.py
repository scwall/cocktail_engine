import time

import board
import busio
import adafruit_mcp230xx
from digitalio import Direction

i2c = busio.I2C(board.SCL, board.SDA)
mcp = adafruit_mcp230xx.MCP23017(i2c)
# pin0 = mcp.get_pin(7)
# pin0.direction = Direction.OUTPUT
pins = dict()
for pinnumber in range(0,12):
    pins['pin'+str(pinnumber +1)] = mcp.get_pin(pinnumber+1)
    pins['pin'+str(pinnumber +1)].direction = Direction.OUTPUT
print(pins)


print('test')
# Blink pin 0 on and then off.

time.sleep(5)
pins['pin7'].value = False
time.sleep(3)
pins['pin7'].value = True