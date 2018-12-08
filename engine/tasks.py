import atexit
import time

import Adafruit_MCP3008
from RPi import GPIO
import adafruit_mcp230xx
import board
import busio
from Adafruit_MotorHAT import Adafruit_MotorHAT
from celery.utils.log import get_task_logger



logger = get_task_logger(__name__)

from celery import shared_task, current_task

CLK = 18
MISO = 23
MOSI = 24
CS = 25
mcp3008 = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)
i2c = busio.I2C(board.SCL, board.SDA)
mcp23017 = adafruit_mcp230xx.MCP23017(i2c)
mh = Adafruit_MotorHAT(addr=0x60)
GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)


def valve(valve_number):
    valve = mcp23017.get_pin(valve_number)
    valve.switch_to_output(value=True)
    return valve


def proximity_sensor():
    return mcp3008.read_adc(0)


def start_course():
    return not bool(GPIO.input(5))


def stepper_start_begin(stepper):
    near = False
    while start_course() != True:
        if proximity_sensor() > 900 or near == True:
            stepper.oneStep(Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.DOUBLE)

        else:
            stepper.oneStep(Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.DOUBLE)

    turnOffMotors()


def progress_percent(size_list):
    for i in range(size_list * 3):
        yield (90 / (size_list * 3)) * (i + 1)


myStepper = mh.getStepper(200, 1)
myStepper.setSpeed(200)
atexit.register(turnOffMotors)


@shared_task()
def make_cocktail(list):
    step_tray = 0
    start = True
    progress = progress_percent(len(list))
    while start:
        if start_course() == True:
            for loop, bottle in enumerate(list):
                logger.info(list)
                valve_one = valve(bottle['first_pin'])
                valve_two = valve(bottle['second_pin'])
                dose = 0
                print('Cocktail start')
                current_task.update_state(
                    state='PROGRESS_STATE',
                    meta={
                        'total': next(progress)
                    })
                if bottle['step'] > step_tray:
                    step = bottle['step'] - step_tray
                    myStepper.step(step, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.DOUBLE)
                    step_tray = bottle['step']
                else:
                    step = step_tray - bottle['step']
                    myStepper.step(step, Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.DOUBLE)
                current_task.update_state(
                    state='PROGRESS_STATE',
                    meta={
                        'total': next(progress)
                    })

                # send dose
                while dose != bottle['dose']:
                    valve_one.value = False
                    time.sleep(4)
                    valve_one.value = True
                    time.sleep(3)
                    time.sleep(6)
                    if dose == 0:
                        current_task.update_state(
                            state='PROGRESS_STATE',
                            meta={
                                'total': next(progress)
                            })
                    valve_two.value = False
                    time.sleep(5)
                    valve_two.value = True
                    dose += 1
            start = False
        else:
            stepper_start_begin(myStepper)

    turnOffMotors()
    current_task.update_state(
        state='PROGRESS_STATE',
        meta={
            'total': 100
        })
    stepper_start_begin(myStepper)
    turnOffMotors()
