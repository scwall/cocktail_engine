#!/usr/bin/python3
import atexit
import time

import Adafruit_MCP3008
import adafruit_mcp230xx
import board
import busio
from Adafruit_MotorHAT import Adafruit_MotorHAT
from RPi import GPIO
from celery import shared_task, current_task
from celery.utils.log import get_task_logger

LOGGER = get_task_logger(__name__)

CLK = 18
MISO = 23
MOSI = 24
CS = 25
MCP3008 = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)
I2C = busio.I2C(board.SCL, board.SDA)
MCP23017 = adafruit_mcp230xx.MCP23017(I2C)
MOTOR_HAT = Adafruit_MotorHAT(addr=0x60)
GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def turn_off_motors():
    """
    Stop the 4 motor pulses
    """
    MOTOR_HAT.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    MOTOR_HAT.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    MOTOR_HAT.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    MOTOR_HAT.getMotor(4).run(Adafruit_MotorHAT.RELEASE)


def valve(valve_number):
    """

    :param valve_number: Relay connection number on the map
    :return: Return an object to use the specified relay
    """
    valve_choice = MCP23017.get_pin(valve_number)
    valve_choice.switch_to_output(value=True)
    return valve_choice


def proximity_sensor():
    """
    To know the distance of the plateau
    :return: Returns the data of the distance probe
    """
    return MCP3008.read_adc(0)


def start_course():
    """
    To know if the plateau is revennu at the beginning
    :return: Returns if the switch button is enabled
    """
    return not bool(GPIO.input(5))


def stepper_start_begin(stepper):
    """
    Allows you to return the tray to the beginning
    :param stepper: Takes into parameter the engine
    """
    small_distance = False
    while not start_course():
        if proximity_sensor() > 900 and small_distance is False:
            small_distance = True
        if small_distance:
            stepper.oneStep(Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.INTERLEAVE)

        else:
            stepper.oneStep(Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.DOUBLE)

    turn_off_motors()


def progress_percent(size_list):
    """
    Creates a builder to calculate percentages of the progress of the cocktail creation
    :param size_list: Takes as parameter the length of the list
    """
    for i in range(size_list * 3):
        yield (90 / (size_list * 3)) * (i + 1)


MY_STEPPER = MOTOR_HAT.getStepper(200, 1)
MY_STEPPER.setSpeed(200)
atexit.register(turn_off_motors)


@shared_task()
def make_cocktail(bottles_list):
    """
    Function for the creation of the cocktail:
    the displacement and the emptying of the solenoid valves
    :param bottles_list:
    Takes in parameter the list with the different
    elements necessary for the creation of the cocktail
    """
    step_tray = 0
    start = True
    progress = progress_percent(len(bottles_list))
    while start:

        if start_course():
            for bottle in bottles_list:
                LOGGER.info(bottles_list)
                valve_one = valve(bottle['first_pin'])
                valve_two = valve(bottle['second_pin'])
                dose = 0
                current_task.update_state(
                    state='PROGRESS_STATE',
                    meta={
                        'total': next(progress)
                    })
                if bottle['step'] > step_tray:
                    step = bottle['step'] - step_tray
                    MY_STEPPER.step(step, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.DOUBLE)
                    step_tray = bottle['step']
                else:
                    step = step_tray - bottle['step']
                    MY_STEPPER.step(step, Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.DOUBLE)
                current_task.update_state(
                    state='PROGRESS_STATE',
                    meta={
                        'total': next(progress)
                    })

                # send dose
                while dose != bottle['dose']:
                    valve_one.value = False
                    time.sleep(3)
                    valve_one.value = True
                    time.sleep(1)
                    if dose == 0:
                        current_task.update_state(
                            state='PROGRESS_STATE',
                            meta={
                                'total': next(progress)
                            })
                    valve_two.value = False
                    time.sleep(2)
                    valve_two.value = True
                    dose += 1
            start = False
        else:
            stepper_start_begin(MY_STEPPER)

    turn_off_motors()
    current_task.update_state(
        state='PROGRESS_STATE',
        meta={
            'total': 100
        })
    stepper_start_begin(MY_STEPPER)
    turn_off_motors()
