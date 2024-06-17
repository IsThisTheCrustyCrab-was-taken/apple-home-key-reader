"""
Pins for the lock are hardcoded for now

    Function       |Pin (BCM GPIO - whatever that means)
    ---------------|-----------------
Inputs:            |
    Sense (Pull-up)| 16
    (relay)        | 21
    // Set Contact to 1 and pull the inputs to ground or other way around
Relays:            |
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
        # Motor pins
        top_relay_pin = 21
        bottom_relay_pin = 20

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
        self.top_relay = DigitalOutputDevice(top_relay_pin)
        self.top_relay.off()
        self.bottom_relay = DigitalOutputDevice(bottom_relay_pin)
        self.bottom_relay.off()

        self.sense.when_activated = self.on_closed
        self.sense.when_deactivated = self.on_opened
        self.opening = False

    def open(self):
        if self.opening:
            return
        self.opening = True
        self.top_relay.on()
        sleep(0.5)
        self.bottom_relay.on()
        self.update_target_state()
        sleep(5)
        self.top_relay.off()
        self.bottom_relay.off()
        self.update_target_state()
        self.opening = False

    def close(self):
        self.top_relay.off()
        self.bottom_relay.off()
        self.update_target_state()

    def on_opened(self):
        self.state_change_callback(0)

    def on_closed(self):
        self.state_change_callback(1)
        self.update_target_state()

    def update_target_state(self):
        target_state = 1 if self.closed and (not self.top_relay.is_active) else 0
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
        for p in [self.sense, self.top_relay, self.bottom_relay]:
            p.close()
