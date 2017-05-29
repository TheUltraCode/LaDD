"""
Copyright 2017 Kyle Nied (nied.kyle@gmail.com)

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

import obd

"""
"OBD" Module:

Packages Imported:
 * obd.

Classes:
 * OBD -> An "interface" for LaDD's OBD connection to a vehicle.
"""

class OBD:
    """
    Instance Variables:
     * shared_dict [multiprocessing.Manager.dict()] -> A special dictionary returned by the Manager object "manager_obj" located in LaDD's main.py, this is a dictionary shared across the different processes that constitute LaDD.
     * OBD_connected [bool] -> The result of running this class's "test_OBD_connection" in LaDD's main.py.
     * OBD_connection [obd.OBD] -> The obd.OBD object that collects OBD data, being the core of this class.
     * speed [int] -> The current speed of the vehicle.
     * previously_below_48kph [bool] -> The last value of "shared_dict's" "below_48kph," it is used to determine whether to warn the user a change in their vehicle's speed from below 48 kph to equal or above 48 kph, or vice-versa.
    
    Methods:
     * __init__ -> Instantiates the class, and prepares an OBD connection if "OBD_connected" holds True.
     * begin -> Begins the main loop of this class, which constantly collects the current speed of the car and determines based on that value whether "shared_dict's" "below_48kph" key's value is set to True or False. Also ends the multiprocessing.Process in LaDD's main.py using an object of this class when "shared_dict's" "turn_off_LaDD" is True.
     * test_OBD_connection [static] -> Tests whether or not an OBD connection can be established with a given baud rate.
    """    
    
    def __init__(self, shared_dict, OBD_connected):
        """
        Instantiates the class and assign an obd.Async object to the instance variable "OBD_connection."
        
        Arguments:
         * shared_dict [multiprocessing.Manager.dict()] -> A special dictionary returned by the Manager object "manager_obj" located in LaDD's main.py, this is a dictionary shared across the different processes that constitute LaDD.
         * OBD_connected [bool] -> The result of running this class's "test_OBD_connection" in LaDD's main.py.
        """
        self.shared_dict = shared_dict
        self.OBD_connected = OBD_connected
        self.speed = 0
        self.previously_below_48kph = self.shared_dict['below_48kph']
        if self.OBD_connected:
            self.OBD_connection = obd.OBD(portstr='/dev/ttyUSB0',baudrate=self.shared_dict['baud_rate'])
            
        
    def begin(self):
        """
        Begins the main loop of this class, which constantly collects the current speed of the vehicle and determines based on that value whether "shared_dict's" "below_48kph" key's value is set to True or False. Also ends the multiprocessing.Process in LaDD's main.py using an object of this class when "shared_dict's" "turn_off_LaDD" is True.
        """
        while self.OBD_connected and not self.shared_dict['turn_off_LaDD']:
            self.previously_below_48kph = self.shared_dict['below_48kph']
            self.speed = self.OBD_connection.query(obd.commands.SPEED)
            if (self.speed.value.magnitude >= 48):
                self.shared_dict['below_48kph'] = False
            else:
                self.shared_dict['below_48kph'] = True
            
            if self.previously_below_48kph != self.shared_dict['below_48kph']:
                self.shared_dict['crossed_48kph_threshold'] = True
        else:
            self.OBD_connection.close()
    
    @staticmethod
    def test_OBD_connection(baud_rate):
        """
        Tests whether or not an OBD connection can be established with a given baud rate.
        
        Return Argument:
         * result [bool]-> Represents whether an OBD connection has been successfully established.
        """
        
        test_con = obd.OBD(portstr='/dev/ttyUSB0',baudrate=baud_rate)
        result = test_con.is_connected()
        test_con.close()
        del test_con
        return result
