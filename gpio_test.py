#!/usr/bin/python3
import RPi.GPIO as GPIO
import threading
import time

import board
import busio
import adafruit_mcp230xx
from digitalio import Direction
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import time
import atexit
import trio

import time

obj = {'step': 300, 'solenoidvalve': 1, 'dose': 2}
CLK = 18
MISO = 23
MOSI = 24
CS = 25
mcp3008 = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)
i2c = busio.I2C(board.SCL, board.SDA)
mcp23017 = adafruit_mcp230xx.MCP23017(i2c)
# pin0 = mcp23017.get_pin(7)
# pin0.direction = Direction.OUTPUT
pin_dict = dict()
for pinnumber in range(0,12):
    pin_dict['pin' + str(pinnumber + 1)] = mcp23017.get_pin(pinnumber + 1)
    pin_dict['pin' + str(pinnumber + 1)].direction = Direction.OUTPUT
mh = Adafruit_MotorHAT(addr=0x60)
GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
st = threading.Thread()
start = True

def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)


myStepper = mh.getStepper(200, 1)

myStepper.setSpeed(100)

atexit.register(turnOffMotors)


def proximity_sensor():
    return mcp3008.read_adc(0)


def start_course():
    return not bool(GPIO.input(5))


def stepper_start_begin(stepper):
    while start_course() != True:
        if proximity_sensor() > 700:
            stepper.oneStep(Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.MICROSTEP)
            print('au dessus de 700')
        elif proximity_sensor() > 300:
            stepper.step(40, Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.DOUBLE)
            print('au dessus de 300')
        elif proximity_sensor() < 300:
            stepper.step(100, Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.DOUBLE)
            print('en dessous de 300')
        # time.sleep(0)
    turnOffMotors()



while start:
    if start_course() == True or start_course() == False:
        print('Cocktail start')
        time.sleep(0.2)
        myStepper.step(obj['step'], Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.DOUBLE)
        time.sleep(1)
        pin_dict['pin7'].value = False
        time.sleep(3)
        pin_dict['pin7'].value = True
        time.sleep(3)
        pin_dict['pin6'].value = False
        time.sleep(3)
        pin_dict['pin6'].value = True
        myStepper.step(obj['step'], Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.DOUBLE)
        start = False

    else:
        if not st.isAlive():
            st = threading.Thread(target=stepper_start_begin,
                                  args=(myStepper,))
            st.start()
