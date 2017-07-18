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

import multiprocessing as mp
import os.path
from interfaces import *

"""
"main" Module:

Packages Imported:
 * multiprocessing (as mp),
 * interfaces.

Functions:
 * begin_process -> Initiates a separate process using what was passed as arguments to a mp.Process when the "start" method of that mp.Process is called.
"""

Piezo_pin = 18
#The GPIO pin number of a pulse width modulation GPIO pin on the Raspberry Pi 3 that LaDD uses to control the Piezo buzzer
camera_resolution = [640,480]
#The resolution of the Raspberry Pi Camera Module V2 [width,height].

def begin_process(obj):
    """
    "begin_process" Function:
    
    Actions:
     * Initiates a separate process using what was passed as arguments to a mp.Process when the "start" method of that mp.Process is called.
    
    Arguments:
     * obj [multiple types] -> An object of interfaces.user_interface.User_interface, interfaces.camera.Camera, interfaces.audio.Audio, or interfaces.OBD.OBD.
    """
    
    obj.begin()

if __name__ == '__main__':
    if not os.path.isfile('configure.csv'):
        with open('configure.csv','x',newline='') as csvfile:
            pass
            
    if not os.path.isfile('data.csv'):
        with open('data.csv','x',newline='') as csvfile:
            pass

    manager_obj = mp.Manager()
    shared_dict = manager_obj.dict({'vehicle_width':0,'baud_rate':0,'first_row_for_warping':0,'binary_threshold_value_lower_end':0,'turn_off_LaDD':False, 'below_48kph':False, 'crossed_48kph_threshold':False,'result':'',
    'crossed_lane':False,'crossed_divider':False,'nothing_detected':False,'full_frame':[],'ROI_frame':[],'warped_ROI_frame':[],'show_both_rows_for_warping':False,'processed_ROI_frame':[],'result':''})
    
    config_vars = user_interface.User_Interface.get_config_vars()
    shared_dict['vehicle_width'] = config_vars[1]['vehicle_width']
    shared_dict['baud_rate'] = config_vars[1]['baud_rate']
    
    data_vars = user_interface.User_Interface.get_data_vars()
    shared_dict['binary_threshold_value_lower_end'] = data_vars[1]['binary_threshold_value_lower_end']
    shared_dict['first_row_for_warping'] = data_vars[1]['first_row_for_warping']
    
    print(data_vars)
    print(config_vars)
    '''
    if not config_vars[0]:
        shared_dict['turn_off_LaDD'] = True
    
    OBD_connected = OBD.OBD.test_OBD_connection(shared_dict['baud_rate'])
    camera_connected = camera.Camera.test_camera_connection()
    #The two lines below are for testing purposes.
    #OBD_connected = True
    #camera_connected = True
    if not OBD_connected or not camera_connected:
        shared_dict['turn_off_LaDD'] = True
            
    #For the purpose of testing individual "interfaces," you can comment out each line of code pertaining to the creation of one of the "X_obj" objects, their passing through their respective "X_process" mp.Process, etc.
    
    user_interface_obj = user_interface.User_Interface(shared_dict,not data_vars[0],not config_vars[0],OBD_connected,camera_connected)
    camera_obj = camera.Camera(shared_dict,camera_resolution)
    audio_obj = audio.Audio(shared_dict)
    OBD_obj = OBD.OBD(shared_dict,OBD_connected)
    
    user_interface_process = mp.Process(target=begin_process, args=(user_interface_obj,))
    camera_process = mp.Process(target=begin_process, args=(camera_obj,))
    audio_process = mp.Process(target=begin_process, args=(audio_obj,))
    OBD_process = mp.Process(target=begin_process, args=(OBD_obj,))
    
    user_interface_process.start()
    camera_process.start()
    audio_process.start()
    OBD_process.start()
    
    user_interface_process.join()
    camera_process.join()
    audio_process.join()
    OBD_process.join()'''
    
