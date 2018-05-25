"""
Copyright 2017-2018 Kyle Nied (nied.kyle@gmail.com)

<------------------------------------------------------------------>

This file is part of LaDD.

LaDD is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

LaDD is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with LaDD.  If not, see <http://www.gnu.org/licenses/>.
"""

import RPi.GPIO as gpio
import time

"""
"audio" Module:

Packages Imported:
 * RPi.GPIO (as gpio),
 * time.

Classes:
 * Audiovisual -> An "interface" for LaDD's Piezo buzzer.
"""

class Audio:
    """
    Instance Variables:
     * shared_dict [multiprocessing.Manager.dict()] -> A special dictionary returned by the Manager object "manager_obj" located in LaDD's main.py, this is a dictionary shared across the different processes that constitute LaDD.
     * Piezo_GPIO_pin [int] -> The GPIO pin number of a pulse width modulation GPIO pin on the Raspberry Pi 3 that LaDD uses to control the Piezo buzzer.
     * piezo [gpio.PWM] -> The gpio.PWM object that controls LaDD's Piezo buzzer, being the core of this class.
    
    Methods:
     * __init__ -> Instantiates the class, and gives LaDD the control of its Piezo buzzer.
     * begin -> Begins the main loop of this class, which constantly runs "Piezo_controller". Also ends the multiprocessing.Process object in LaDD's main.py using an object of this class when "shared_dict's" "turn_off_LaDD" is True.
     * Piezo_controller -> Checks constantly "shared_dict's" "crossed_lane", "crossed_divider", and ">=48kph" keys' values, and warns the driver according to the values.
    """
    
    def __init__(self, shared_dict):
        """
        Instantiates the class, and gives LaDD the control of its Piezo buzzer.
        
        Arguments:
         * shared_dict [multiprocessing.Manager.dict()] -> A special dictionary returned by the Manager object "manager_obj" located in LaDD's main.py, this is a dictionary shared across the different processes that constitute LaDD.
        """
        
        self.shared_dict = shared_dict
        
        self.Piezo_GPIO_pin = 18
        gpio.setmode(gpio.BCM)
        gpio.setup(self.Piezo_GPIO_pin, gpio.OUT)
        self.piezo = gpio.PWM(self.Piezo_GPIO_pin,1700)
        
    def begin(self):
        """
        Begins the main loop of this class, which constantly runs "Piezo_controller". Also ends the multiprocessing.Process object in LaDD's main.py using an object of this class when "shared_dict's" "turn_off_LaDD" is True.
        """
        while not self.shared_dict['turn_off_LaDD']:
            self.Piezo_controller()
        else:
            gpio.cleanup()
    
    def Piezo_controller(self):
        """
        Checks constantly "shared_dict's" "crossed_lane", "crossed_divider", and ">=48kph" keys' values, and warns the driver according to the values.
        """
        
        conditions = [self.shared_dict['crossed_48kph_threshold'],(self.shared_dict['crossed_lane'] or self.shared_dict['crossed_divider'])]
        for c in enumerate(conditions,1):
            if c[0] == 1:
                if c[1]:
                    self.shared_dict['crossed_48kph_threshold'] = False
                    self.piezo.start(85)
                    time.sleep(1)
                    self.piezo.stop()
                    self.piezo.ChangeFrequency(1700)
                    time.sleep(1)
            else:
                if c[1]:
                    for x in range(3):
                        self.piezo.start(85)
                        time.sleep(0.25)
                        self.piezo.stop()
                        time.sleep(0.75)
                        self.piezo.ChangeFrequency(1700)
                    time.sleep(2)
