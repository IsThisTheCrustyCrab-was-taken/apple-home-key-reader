"""
Pins for the lock are hardcoded for now

    Function       |Pin (BCM GPIO - whatever that means)
    ---------------|-----------------
Inputs:            |
    Sense (Pull-up)| 16
MOSFETs (active HIGH):
    Top            | 21
    Bottom         | 20
"""
from time import sleep

from gpiozero import Motor, DigitalInputDevice, DigitalOutputDevice, Button


class DoorLock:
    def doNothing(self):
        return

    def __init__(self, on_open=None, on_close=None, closing_function=None, state_change_callback=None,
                 target_state_callback=None):
        # Input pins
        sense_pin = 16
        # MOSFET pins
        top_mosfet_pin = 21
        bottom_mosfet_pin = 20

        if on_open is None:
            on_open = self.doNothing
        if on_close is None:
            on_close = self.doNothing
        if closing_function is None:
            self.closing_function = self.doNothing
        else:
            self.closing_function = closing_function

        if state_change_callback is None:
            self.state_change_callback = self.doNothing
        else:
            self.state_change_callback = state_change_callback
        if target_state_callback is None:
            self.target_state_callback = self.doNothing
        else:
            self.target_state_callback = target_state_callback

        self.on_open = on_open
        self.on_close = on_close

        # Setup Input pins
        self.sense = DigitalInputDevice(sense_pin, pull_up=True)
        # Setup MOSFET pins with active_high=True (activates when pin is HIGH)
        self.top_mosfet = DigitalOutputDevice(top_mosfet_pin, active_high=True, initial_value=False)
        self.bottom_mosfet = DigitalOutputDevice(bottom_mosfet_pin, active_high=True, initial_value=False)

        self.sense.when_activated = self.on_closed
        self.sense.when_deactivated = self.on_opened
        self.opening = False

    def open(self):
        if self.opening:
            return
        self.opening = True
        self.top_mosfet.on()  # Sets pin LOW to activate MOSFET
        sleep(0.5)
        self.bottom_mosfet.on()  # Sets pin LOW to activate MOSFET
        self.update_target_state()
        sleep(5)
        self.top_mosfet.off()  # Sets pin HIGH to deactivate MOSFET
        self.bottom_mosfet.off()  # Sets pin HIGH to deactivate MOSFET
        self.update_target_state()
        self.opening = False

    def close(self):
        self.top_mosfet.off()  # Sets pin HIGH to deactivate MOSFET
        self.bottom_mosfet.off()  # Sets pin HIGH to deactivate MOSFET
        self.update_target_state()

    def on_opened(self):
        self.state_change_callback(0)

    def on_closed(self):
        self.state_change_callback(1)
        self.update_target_state()

    def update_target_state(self):
        target_state = 1 if self.closed and (not self.top_mosfet.is_active) else 0
        self.target_state_callback(target_state)

    def update_current_state(self):
        current_state = 1 if self.closed else 0
        self.state_change_callback(current_state)

    @property
    def opened(self):
        return not self.sense.is_active

    @property
    def closed(self):
        return self.sense.is_active

    def unload(self):
        for p in [self.sense, self.top_mosfet, self.bottom_mosfet]:
            p.close()
