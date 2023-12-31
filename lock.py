"""
Pins for the lock are hardcoded for now

    Function       |Pin (BCM GPIO - whatever that means)
    ---------------|-----------------
Inputs:            |
    Door switch    |  6
    Top endstop    | 13
    Bottom endstop | 22
    (Contact)      | 26
    // Set Contact to 1 and pull the inputs to ground
Motor:             |
    Pwm            |  2
    Up             |  3
    Down           |  4
    // Set either up and down high to move in that direction, enable both to brake
"""

from gpiozero import Motor, DigitalInputDevice, DigitalOutputDevice, Button


class DoorLock:
    def __init__(self, on_open=None, on_close=None):
        # Input pins
        top_endstop_pin = 13
        bottom_endstop_pin = 19
        door_switch_pin = 6
        contact_pin = 26
        # Motor pins
        pwm_pin = 17
        up_pin = 22
        down_pin = 27

        self.on_open = on_open
        self.on_close = on_close

        self.motor_speed = 0.15
        # Setup Input pins
        self.motor = Motor(forward=up_pin, backward=down_pin, enable=pwm_pin)

        self.top_endstop = DigitalInputDevice(top_endstop_pin, pull_up=True)
        self.bottom_endstop = DigitalInputDevice(bottom_endstop_pin, pull_up=True)
        self.door_switch = Button(door_switch_pin)
        self.contact = DigitalOutputDevice(contact_pin, active_high=False)

        self.door_switch.hold_time = 2
        self.contact.off()
        self.top_endstop.when_activated = self.on_opened
        self.bottom_endstop.when_activated = self.on_closed
        self.door_switch.when_held = self.close

    def close(self):
        self.motor.forward(self.motor_speed)

    def open(self):
        self.motor.backward(self.motor_speed)

    def on_opened(self):
        self.motor.stop()
        self.on_open()

    def on_closed(self):
        self.motor.stop()
        self.on_close()

    @property
    def opened(self):
        return self.top_endstop.is_active

    @property
    def closed(self):
        return self.bottom_endstop.is_active
