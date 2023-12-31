"""
Pins for the lock are hardcoded for now

    Function       |Pin (BCM GPIO - whatever that means)
    ---------------|-----------------
Inputs:            |
    Door switch    |  6
    Top endstop    | 13
    Bottom endstop | 19
    (Contact)      | 26
    // Set Contact to 1 and pull the inputs to ground or other way around
Motor:             |
    Pwm            | 17
    Up             | 22
    Down           | 27
    // Set either up and down high to move in that direction, enable both to brake
"""

from gpiozero import Motor, DigitalInputDevice, DigitalOutputDevice, Button


class DoorLock:
    def doNothing(self):
        pass

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

        if on_open is None:
            on_open = self.doNothing
        if on_close is None:
            on_close = self.doNothing

        self.on_open = on_open
        self.on_close = on_close

        self.motor_speed = 0.45
        # Setup Input pins
        self.motor = Motor(forward=up_pin, backward=down_pin, enable=pwm_pin)

        self.top_endstop = Button(top_endstop_pin)
        self.bottom_endstop = Button(bottom_endstop_pin)
        self.door_switch = Button(door_switch_pin)
        self.contact = DigitalOutputDevice(contact_pin, active_high=False)

        self.bottom_endstop.hold_time = 4
        self.door_switch.hold_time = 2
        self.contact.on()
        self.top_endstop.when_activated = self.on_closed
        self.bottom_endstop.when_activated = self.on_opened
        self.bottom_endstop.when_held = self.close_if_door_closed
        self.door_switch.when_held = self.close

    def close_if_door_closed(self):
        if self.door_switch.is_active:
            self.close()

    def close(self):
        if self.top_endstop.is_active or self.motor.value != 01:
            return
        self.motor.forward(self.motor_speed+0.05)

    def open(self):
        if self.bottom_endstop.is_active or self.motor.value != 0:
            return
        self.motor.backward(self.motor_speed)

    def on_opened(self):
        if self.motor.value > 0.1:
            print(self.motor.value)
            return
        self.motor.stop()
        self.on_open()

    def on_closed(self):
        if self.motor.value < -0.1:
            print(self.motor.value)
            return
        self.motor.stop()
        self.on_close()

    @property
    def opened(self):
        return self.top_endstop.is_active

    @property
    def closed(self):
        return self.bottom_endstop.is_active

    def unload(self):
        for p in [self.motor, self.top_endstop, self.bottom_endstop, self.door_switch, self.contact]:
            p.close()
