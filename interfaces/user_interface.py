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

import csv, PIL
import PIL.Image, PIL.ImageTk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

"""
"user_interface" Module:
Packages Imported:
 * csv,
 * PIL.
 * tkinter.

Classes:
 * Shutdown_Dialog_Window -> A class that creates a custom shutdown dialog window used by the "User_Interface" class, with a built in timer to automatically close the dialog window without shutting down LaDD.
 * User_Interface -> An "interface" for LaDD's user interface displayed through its touchscreen.
"""

class Shutdown_Dialog_Window:
    """
    Instance Variables:
     * shutdown_method [User_Interface.shutdown (method)] -> Literally the "shutdown" method of the "User_Interface" class.
     * counter [int] -> Used to "count" how many seconds have gone by.
     * decision_made [bool] -> Per its name, its value represents the reality; in other words, if the user has pressed either the "yes_button" or "no_button", then it equals True, else in the meantime, it is False. After five seconds pass and the shutdown dialog window is automatically closed, it is set to True, stopping the "timer" method for good.
     * root [tkinter.Tk] -> The "root" window instance variable of the "User_Interface" class.
     * Toplevel_Window [tkinter.TopLevel] -> The TopLevel window that is the shutdown dialog window.
     * Toplevel_Window_width [int] -> Self-explanatory.
     * shutdown_question_label [tkinter.tkk.Label] -> The label containing the question of shutting down LaDD.
     * shutdown_detail_label [tkinter.ttk.Label] -> The label containing "detail" text that is below the "shutdown_question_label", whose text is updated (see "shutdown_detail_label_text" below for explanation).
     * shutdown_detail_label_text [tkinter.StringVar] -> The "textvariable" used by the "shutdown_detail_label", which is updated in real time by this class's "timer" method to show how much time is left until the shutdown dialog window closes.
     * yes_button [tkinter.ttk.Button] -> The "Yes" button, which if pressed shuts down LaDD.
     * no_button [tkinter.ttk.Button] -> The "No" button, which if pressed closes the shutdown dialog window.
    
    Methods:
     * __init__ -> Instantiates the class, creates the shutdown dialog window, and starts the count-down timer for automatic closure of the window.
     * timer -> Keeps track of how many seconds are left until the shutdown dialog window is automatically closed, while updating "shutdown_detail_label_text" to convey that amount of time left to the user.
     * closing_action -> Closes the shutdown dialog window, and if the user pressed the "no_button", then also calls the "shutdown_method" to shutdown LaDD.
    """
    
    def __init__(self, root, shutdown_method):
        """
        Instantiates the class, creates the shutdown dialog window, and starts the count-down timer for automatic closure of the window.
        
        Arguments:
         * root [tkinter.Tk] -> The "root" window instance variable of the "User_Interface" class.
         * shutdown_method [User_Interface.shutdown (method)] -> Literally the "shutdown" method of the "User_Interface" class.
        """
        self.shutdown_method = shutdown_method
        
        self.shutdown_detail_label_text = StringVar(value='This message will automatically close\nin 5 seconds without shutting down.')
        self.counter = 0
        self.decision_made = False
        self.Toplevel_Window_width = 0
        #Toplevel_Windos_dimensions = expressed [width,height]
        
        #############################
        # tkinter window definition #
        #############################
        self.root = root
        self.Toplevel_Window = Toplevel(self.root)
        self.Toplevel_Window.geometry('+' + str(self.root.winfo_x()) + '+' + str(self.root.winfo_y()))
        self.shutdown_question_label = ttk.Label(self.Toplevel_Window, text='Are you sure you want to shutdown LaDD?', font='TkCaptionFont',anchor='center')
        self.shutdown_detail_label = ttk.Label(self.Toplevel_Window, textvariable=self.shutdown_detail_label_text,anchor='center',justify='center')
        self.yes_button = ttk.Button(self.Toplevel_Window, text='Yes', command=lambda:self.closing_action(True))
        self.no_button = ttk.Button(self.Toplevel_Window, text='No', command=lambda:self.closing_action(False))
        #########################
        # tkinter window setup #
        #########################
        self.shutdown_question_label.grid(row=0,column=0,columnspan=5,sticky='nwes')
        self.shutdown_detail_label.grid(row=1,column=0,columnspan=5,sticky='nwes')
        self.yes_button.grid(row=2,column=1,sticky='nwes')
        self.no_button.grid(row=2,column=3,sticky='nwes')
        
        for child in self.Toplevel_Window.winfo_children():
            child.grid_configure(padx=5, pady=5)
        
        self.Toplevel_Window.update_idletasks()
        self.Toplevel_Window_width = int(self.Toplevel_Window.geometry().split('x')[0])
        self.Toplevel_Window.geometry('+' + str(self.root.winfo_x()+int((self.root.winfo_width()-self.Toplevel_Window_width)/2)) + '+' + str(self.root.winfo_y()))
        self.root.after(1000,self.timer)
    
    def timer(self):
        """
        Keeps track of how many seconds are left until the shutdown dialog window is automatically closed, while updating "shutdown_detail_label_text" to convey that amount of time left to the user.
        """
        if not self.decision_made:
            self.counter += 1
            if self.counter < 5:
                self.shutdown_detail_label_text.set('This message will automatically close\nin ' + str(5-self.counter) + ' seconds without shutting down.')
                self.root.after(1000,self.timer)
            else:
                self.closing_action(False)
            
    
    def closing_action(self, result):
        """
        Closes the shutdown dialog window, and if the user pressed the "no_button", then also calls the "shutdown_method" to shutdown LaDD.
        
        Arguments:
         * result -> The decision made by the user or automatically by the "timer" method: if True, then the user had pressed the "yes_button", and LaDD will be shutdown; if False, then either the user had pressed the "no_button", or the "timer" method determined five seconds have passed without user input, and LaDD is left on.
        """
        self.decision_made = True
        self.Toplevel_Window.destroy()
        if result:
            self.shutdown_method()


class User_Interface:
    """
    Instance Variables:
     * shared_dict [multiprocessing.Manager.dict()] -> A special dictionary returned by the Manager object "manager_obj" located in LaDD's main.py, this is a dictionary shared across the different processes that constitute LaDD.
     * need_to_set_config_vars [bool] -> Determined in main.py, if False, then all of the configuration variables have been successfully pulled from the "configure.csv file", but if True, then that was not the case.
     * OBD_connected [bool] -> The result of running "interfaces.OBD.OBD.test_OBD_connection" in LaDD's main.py.
     * camera_connected [bool] -> The result of running "interfaces.camera.Camera.test_camera_connection" in LaDD's main.py.
     * root [tkinter.Tk] -> The "root" window of the entire user interface of LaDD.
     * main_frame [tkinter.ttk.Frame] -> Literally the "main frame" and also the only frame slaved to "root".
     * notebook [tkinter.ttk.Notebook] -> The "Notebook" that is the only slave to "main_frame".
     * main_page [tkinter.ttk.Frame] -> The "Main" tab in the "Notebook" of LaDD's user interface, it is where help in using LaDD, an "About" statement, and the shutdown option for LaDD can be found. It is slave to "notebook."
     * camera_page [tkinter.ttk.Frame] -> The "Camera" tab in the "Notebook" of LaDD's user interface, it is where raw, partially processed, or completely processed footage from LaDD's camera can be seen. It is slave to "notebook."
     * set_config_vars_page [tkinter.ttk.Frame] -> The "Set Config. Vars." tab in the "Notebook" of LaDD's user interface, it is where the configuration variables from LaDD's "configure.csv" file can be seen and edited. It is slave to "notebook".
     
     {"mp" = "main_page"; "cp" = "camera_page"; "scvp" = "set_config_vars_page"; "verti" = "vertical"; "horiz" = "horizontal"}
     
     * mp_verti_separator [tkinter.ttk.Separator] -> A vertical separator used between "mp_about_button" plus "mp_shutdown_button" and "mp_help_label_frame". It is slave to "main_page."
     * mp_horiz_separator [tkinter.ttk.Separator] -> A horizontal separator used between "mp_about_button" and "mp_shutdown_button". It is slave to "main_page".
     * mp_about_button [tkinter.ttk.Button] -> A button that when pressed displays an "About" statement in a generic tkinter information dialog window. It is slave to "main_page."
     * mp_disclaimer_button [tkinter.ttk.Button] -> A button that when pressed displays the disclaimer statement in a generic tkinter information dialog window. It is a slave to "main_page."
     * mp_shutdown_button [tkinter.ttk.Button] -> A button that when pressed creates a "Shutdown_Dialog_Window" instance.
     * mp_help_label_frame [tkinter.ttk.Labelframe] -> A "Labelframe" containing buttons that provide "Help" statements on the "camera_page" and the "set_config_vars_page". It is slave to "main_page."
     * mp_cp_help_button [tkinter.ttk.Button] -> A button that when pressed displays an "Help" statement regarding the function and use of the "camera_page" in a generic tkinter information dialog window. It is slave to "mp_help_label_frame."
     * mp_scvp_help_button [tkinter.ttk.Button] -> A button that when pressed displays an "Help" statement regarding the function and use of the "set_config_vars_page" in a generic tkinter information dialog window. It is slave to "mp_help_label_frame."
     
     * feed_name [tkinter.StringVar] -> The video feed stage that was selected in "cp_frame_combobox" by the user; it is based on this value that what stage of the video feed in being processed is displayed in "cp_feed_label" to the user.
     * cp_threshold_spinbox_value [tkinter.StringVar] -> The current value of the lower value of the binary threshold stored in "shared_dict's" "binary_threshold_value_lower_end" that is applied on "Camera's" "ROI," set in "cp_threshold_spinbox."
     * cp_warping_spinbox_value [tkinter.StringVar] -> The current value of the "lower" row of "Camera's" "ROI" stored in "shared_dict's" "first_row_for_warping" that is used, along with the row after it, to warp "ROI" into "Camera's" "WarpedROI."
     * cp_warping_checkbutton_value [tkinter.StringVar] -> Used to determine whether to show or hide red lines that denote "shared_dict's" "first_row_for_warping," as well as the row after it, in "shared_dict's" "ROI_frame."
     * Image_obj [PIL.Image] -> The converted image of either "shared_dict's" "full frame", "ROI_frame", "warped_ROI_frame", or "processed_ROI_frame" into a form that can then be converted into an PIL.ImageTk.PhotoImage image object that can then be displayed in "cp_feed_label."
     * ImageTk_obj [PIL.ImageTk.PhotoImage] -> The converted "Image_obj" image object that can be displayed in "cp_feed_label."
     * cp_frame_combobox_label [tkinter.ttk.Label] -> The "Label" displaying the string "Frame type from camera feed:" above "cp_frame_combobox", indicating to the user that a specific stage of the video feed in the process of being processed can be selected in the "cp_frame_combobox." It is a slave of "camera_page."
     * cp_frame_combobox [tkinter.ttk.Combobox] -> The "Combobox" where the user can select a specific stage of the video feed in the process of being processed that will be displayed in "cp_feed_label." It is a slave to "camera_page."
     * cp_feed_label [tkinter.ttk.Label] -> Where "ImageTk_obj" that is derived from either "shared_dict's" "full_frame", "ROI_frame", 'warped_ROI_frame', or "processed_ROI_frame", according to what the user chooses in "cp_frame_combobox", is displayed. It is a slave to "camera_page."
     * cp_horiz_separator [tkinter.ttk.Separator] -> A horizonal separator used between "cp_frame_combobox" and "cp_threshold_spinbox_label." It is a slave to "camear_page."
     * cp_threshold_spinbox_label [tkinter.ttk.Label] -> The "Label" displaying the string "Binary Threshold Value (Lower End)" above "cp_threshold_spinbox." It is a slave to "camera_page."
     * cp_threshold_spinbox [tkinter.ttk.Spinbox] -> The "Spinbox" where the user can change the value of "shared_dicts'" "binary_threshold_value_lower_end," which is used for applying a binary threshold on "Camera's" "ROI." It is a slave to "camera_page."
     * cp_warping_spinbox_label [tkinter.Label] -> The "Label" displaYING the string "First Row for Warping" above "cp_warping_spinbox." It is a slave to "camera_page."
     * cp_warping_spinbox [tkinter.Spinbox] -> The "Spinbox" where the user can change the value of the "lower" row of "Camera's" "ROI" stored in "shared_dict's" "first_row_for_warping" that is used, along with the row after it, to warp "ROI" into "Camera's" "WarpedROI." It is a slave to "camera_page."
     * cp_warping_checkbutton [tkinter.ttk.Checkbutton] -> Can show or hide red lines that denote "shared_dict's" "first_row_for_warping," as well as the row after it, in "shared_dict's" "ROI_frame." It is a slave to "camera_page."
     
     * accepted_characters [list] -> A list of the characters that are "available" and acceptable for the user to enter a new value for a configuration variable in the "set_cofig_vars_page."
     * outcome [tkinter.StringVar] -> The result of pressing the "scvp_enter_button" with whatever characters are or the lack thereof in "scvp_entry"; the value of this variable will either provide the current value of a configuration variable, tell the user that they have succesfully changed the value of a configuration variable, or display an error regarding what value "new_config_var_value" holds.
     * config_var_name [tkinter.StringVar] -> The configuration variable selected in "scvp_var_combobox" by the user; it is based on this value that what configuration variable is viewed and/or edited in the "set_config_vars_page."
     * new_config_var_value [tkinter.StringVar] -> The value of what "scvp_entry" contains; it is this value that if it is deemed acceptable replaces the current value of a configuration variable, albeit with LaDD continuing to run with the old value until LaDD is restarted.
     * scvp_horiz_separator [tkinter.ttk.Separator] -> A vertical separator used between "scvp_entry" plus "scvp_var_combobox" and buttons "scvp_1_button" through "scvp_5_button", "scvp_0_button", and "scvp_enter_button." It is slave to "set_config_vars_page."
     * scvp_entry [tkinter.ttk.Entry] -> Where the new value for a configuration variable is "typed" into and displayed. It is a slave to "set_config_vars_page."
     * scvp_entry_result [tkinter.ttk.Label] -> The result of pressing the "scvp_enter_button" with whatever characters are or the lack thereof in "scvp_entry"; the text it holds is in "outcome" (see above). It is a slave to "set_config_vars_page."
     * scvp_var_combobox_label [tkinter.ttk.Label] -> The "Label" displaying the string "Variable:" above "scvp_var_combobox," indicating to the user that a configuration variable can be selected in the "scvp_var_combobox." It is a slave to "set_config_var_page."
     * scvp_var_combobox [tkinter.ttk.Label] -> The "Combobox" where the user can select what configuration variable to view/edit its value. It is a slave to "set_config_vars_page."
     * scvp_0_button {through} scvp_9_button {and} scvp_point_button [tkinter.ttk.Button] -> Buttons that append their "face value" to "new_config_var_value." It is a slave to "set_config_var_page."
     * scvp_backspace_button [tkinter.ttk.Button] -> A button that removes the last character from "new_config_var_value." It is a slave to "set_config_var_value." It is a slave to "set_config_var_page."
     * scvp_enter_button [tkinter.tkk.Button] -> A button that calls "set_config_vars," which checks "new_config_var_value" to make sure it is "acceptable," then sets the choosen "config_var_name's" value to "new_config_var_value." It is a slave to "set_config_var_page."
    
     * warning_label_value [tkinter.StringVar] -> The warning text presented in "warning_label", which can be "Crossed a lane!", "Crossed the divider!", "Nothing detected.", or "Below 30 mph.".
     * red_frame_style {and} blue_frame_style {and} yellow_frame_style [tkinter.ttk.Style] -> "Styles" that change the "background" color of "warning_frame" to their namesakes (red, blue, or yellow).
     * warning_label [tkinter.ttk.Label] -> A "Label" that displays a warning message when the user either crosses a lane, the divider, the camera detects nothing, or they are going below 48 kph (30 mph). It is a slave to "root."
     * warning_frame [tkinter.ttk.Frame] -> A long rectangular "Frame" that changes color to warn the user of a specific thing (red for crossing a lane or divider, blue for the fact that the camera is not detecting anything, and yellow to say the user is going below 48 kph (30 mph)). It is a slave to "root."
    
    Methods:
     * __init__ -> Instantiates the class, and provides a user interface for LaDD.
     * begin -> Checks to make sure that all of the configuration variables are in check, and the OBD and camera are connected, warning the user if not, then launches the user interface.
     * do_nothing -> Acts as a dummy method for "root's" "protocol" "WM_DELETE_WINDOW," which disables the "X" button on the user interface's windows.
     * about_window -> Displays the "About" statement in a generic information window.
     * disclaimer_window -> Displays the disclaimer statement in a generic tkinter information dialog window.
     * cp_help_window -> Displays the "'Camera' Help" statement in a generic information window.
     * scvp_help_window -> Displays the "'Set Config. Vars." statement in a generic information window.
     * shutdown_window -> Creates an "Shutdown_Dialog_Window" instance that produces a special "yes/no" dialog window with a built-in 5-second timer that automatically closes the window without shutting down LaDD.
     * shutdown -> Closes LaDD's user interface and signals via "shared_dict's" "turn_off_LaDD" key to all of the other processes to end, effectively shutting down LaDD.
     * show_both_rows_for_warping -> Determines whether to show or hide red lines that denote "shared_dict's" "first_row_for_warping," as well as the row after it, in "shared_dict's" "ROI_frame."
     * update_binary_threshold_value_lower_end -> Updates the value of "shared_dict's" "binary_threshold_value_lower_end" by setting it to "cp_threhold_spinbox_value" when it is editted.
     * update_first_row_for_warping -> Updates the value of "shared_dict's" "first_row_for_warping" by setting it to "cp_warping_spinbox_value" when it is editted.
     * update_feed_frame -> Updates what is being displayed in the "cp_feed_label" with the latest images from "shared_dict's" "full_frame", "ROI_frame", or "processed_ROI_frame," depending on what was selected in the "cp_frame_combobox," after they were converted into usable tkinter images and stored in "ImageTk_obj."
     * update_warning -> Checks to see if there is something for LaDD to warn the user about, and if there is it changes "warning_label" and "warning_frame" accordingly.
     * get_X_vars_helper [static] -> "Reads" the .csv files of LaDD ("configure.csv" or "data.csv"), searches for their respective "variables", makes up for incomplete or missing variables, updates the .csv files (possibly fixing and shortening them), then returns its findings; used by "get_config_vars" and "get_data_vars".
     * get_config_vars [static] -> Passes "configure.csv" and the configuration variables' names to "get_X_vars_helper" to get the variables and their values, checks to see if all of the configuration variables are acceptable and accounted for, and then returns its findings.
     * get_data_vars [static] -> Passes "data.csv" and the data variables' names to "get_X_vars_helper" to get the variables and their values, checks to see if all of the data variables are acceptable and accounted for, and then returns its findings.
     * set_config_vars -> Checks to see if the value of "new_config_var_value" is "acceptable," sets the configuration variable selected in "config_var_name" to "new_config_var_name" if the latter was acceptable, then finally tells the user of the success of setting a new value to a given configuration variable, or instead what was wrong with their value they entered into "scvp_entery."
     * set_data_vars -> Sets the data variables' values equal to that of "cp_threshold_spinbox_value" and "cp_warping_spinbox_value."
    """
    
    def __init__(self, shared_dict, data_vars_defaulted, need_to_set_config_vars, OBD_connected, camera_connected):
        """
        Instantiates the class, and provides a user interface for LaDD.
        
        Arguments:
         * shared_dict [multiprocessing.Manager.dict()] -> A special dictionary returned by the Manager object "manager_obj" located in LaDD's main.py, this is a dictionary shared across the different processes that constitute LaDD.
         * need_to_set_config_vars [bool] -> Determined in main.py, if False, then all of the configuration variables have been successfully pulled from the "configure.csv file", but if True, then that was not the case.
         * OBD_connected [bool] -> The result of running "interfaces.OBD.OBD.test_OBD_connection" in LaDD's main.py.
         * camera_connected [bool] -> The result of running "interfaces.camera.Camera.test_camerea_connection: in LaDD's main.py.
        """
        
        self.shared_dict = shared_dict
        self.data_vars_defaulted = data_vars_defaulted
        self.need_to_set_config_vars = need_to_set_config_vars
        #need_to_set_config_vars = a boolean that if True will stop all other processes, make the user "set" the configuration variables, then make the user restart LaDD
        self.OBD_connnected = OBD_connected
        #OBD_connected = a boolean that if False wil stop all other processes, make the user check the OBD physical connection and the "Baud Rate" configuration variable, then make the user restart LaDD
        self.camera_connected = camera_connected
        #camera_connected = a boolean that if False wil stop all other processes, make the user check the camera physical connection and then make the user restart LaDD
        
        #######################
        #tkinter UI definition#
        #######################
        self.root = Tk()
        self.root.title("LaDD")
        self.root.option_add('*tearOff', FALSE)
        self.root.geometry('+0+0')
        
        self.main_frame = ttk.Frame(self.root)
        self.main_frame['padding']=5
        
        self.notebook = ttk.Notebook(self.main_frame)
        self.main_page = ttk.Frame(self.notebook)
        self.camera_page = ttk.Frame(self.notebook)
        self.set_config_vars_page = ttk.Frame(self.notebook)
        self.notebook.add(self.main_page,text='Main')
        self.notebook.add(self.camera_page,text='Camera')
        self.notebook.add(self.set_config_vars_page,text='Set Config. Vars.')
        
        #mp = main_page
        self.mp_verti_separator = ttk.Separator(self.main_page,orient=VERTICAL)
        self.mp_horiz_separator = ttk.Separator(self.main_page,orient=HORIZONTAL)
        self.mp_about_button = ttk.Button(self.main_page,text='About',command=self.about_window)
        self.mp_disclaimer_button = ttk.Button(self.main_page,text='Disclaimer',command=self.disclaimer_window)
        self.mp_shutdown_button = ttk.Button(self.main_page,text='Shutdown',command=self.shutdown_window)
        self.mp_help_label_frame = ttk.Labelframe(self.main_page, text='Help with...')
        self.mp_cp_help_button = ttk.Button(self.mp_help_label_frame,text='"Camera" Tab',command=self.cp_help_window)
        self.mp_scvp_help_button = ttk.Button(self.mp_help_label_frame,text='"Set Config. Vars." Tab',command=self.scvp_help_window)
        
        #cp = camera_page
        self.feed_name = StringVar()
        self.cp_threshold_spinbox_value = StringVar()
        self.cp_warping_spinbox_value = StringVar()
        self.cp_warping_checkbutton_value = StringVar()
        self.Image_obj = None
        self.ImageTk_obj = None
        
        self.cp_frame_combobox_label = ttk.Label(self.camera_page,text='Frame Type from Camera Feed:')
        self.cp_frame_combobox = ttk.Combobox(self.camera_page, textvariable=self.feed_name)
        self.cp_frame_combobox['values'] = ('Full Frame','Region of Interest Frame','Warped ROI Frame', 'Processed ROI Frame')
        self.cp_frame_combobox.state(['readonly'])
        self.cp_frame_combobox.set(self.cp_frame_combobox['values'][0])
        self.cp_horiz_separator = ttk.Separator(self.camera_page,orient=HORIZONTAL)
        self.cp_threshold_spinbox_label = ttk.Label(self.camera_page,text='Binary Threshold Value (Lower End)')
        self.cp_threshold_spinbox = Spinbox(self.camera_page,from_=0.0,to=255.0,textvariable=self.cp_threshold_spinbox_value,command=self.update_binary_threshold_value_lower_end)
        self.cp_warping_spinbox_label = ttk.Label(self.camera_page,text='First Row for Warping:')
        self.cp_warping_spinbox = Spinbox(self.camera_page,from_=0.0,to=59.0,textvariable=self.cp_warping_spinbox_value,command=self.update_first_row_for_warping)
        self.cp_threshold_spinbox_value.set(self.shared_dict['binary_threshold_value_lower_end'])
        self.cp_warping_spinbox_value.set(self.shared_dict['first_row_for_warping'])
        self.cp_warping_checkbutton = ttk.Checkbutton(self.camera_page,text='Show Both Rows for Warping.',variable=self.cp_warping_checkbutton_value,command=self.show_both_rows_for_warping)
        self.cp_feed_label = ttk.Label(self.camera_page)
        
        #scvp = set_config_vars_page
        self.accepted_characters = ['0','1','2','3','4','5','6','7','8','9','.']
        self.outcome = StringVar()
        self.config_var_name = StringVar()
        self.new_config_var_value = StringVar()
        
        self.scvp_horiz_separator = ttk.Separator(self.set_config_vars_page,orient=HORIZONTAL)
        self.scvp_entry = ttk.Entry(self.set_config_vars_page, textvariable=self.new_config_var_value)
        self.scvp_entry_result = ttk.Label(self.set_config_vars_page,textvariable=self.outcome)
        self.scvp_var_combobox_label = ttk.Label(self.set_config_vars_page,text='Variable:')
        self.scvp_var_combobox = ttk.Combobox(self.set_config_vars_page, textvariable=self.config_var_name)
        self.scvp_var_combobox['values'] = ('Vehicle width','Baud rate')
        self.scvp_var_combobox.state(['readonly'])
        self.scvp_var_combobox.set(self.scvp_var_combobox['values'][0])
        self.scvp_1_button = ttk.Button(self.set_config_vars_page, text='1', command=lambda: self.new_config_var_value.set(self.new_config_var_value.get() + '1'))
        self.scvp_2_button = ttk.Button(self.set_config_vars_page, text='2', command=lambda: self.new_config_var_value.set(self.new_config_var_value.get() + '2'))
        self.scvp_3_button = ttk.Button(self.set_config_vars_page, text='3', command=lambda: self.new_config_var_value.set(self.new_config_var_value.get() + '3'))
        self.scvp_4_button = ttk.Button(self.set_config_vars_page, text='4', command=lambda: self.new_config_var_value.set(self.new_config_var_value.get() + '4'))
        self.scvp_5_button = ttk.Button(self.set_config_vars_page, text='5', command=lambda: self.new_config_var_value.set(self.new_config_var_value.get() + '5'))
        self.scvp_6_button = ttk.Button(self.set_config_vars_page, text='6', command=lambda: self.new_config_var_value.set(self.new_config_var_value.get() + '6'))
        self.scvp_7_button = ttk.Button(self.set_config_vars_page, text='7', command=lambda: self.new_config_var_value.set(self.new_config_var_value.get() + '7'))
        self.scvp_8_button = ttk.Button(self.set_config_vars_page, text='8', command=lambda: self.new_config_var_value.set(self.new_config_var_value.get() + '8'))
        self.scvp_9_button = ttk.Button(self.set_config_vars_page, text='9', command=lambda: self.new_config_var_value.set(self.new_config_var_value.get() + '9'))
        self.scvp_0_button = ttk.Button(self.set_config_vars_page, text='0', command=lambda: self.new_config_var_value.set(self.new_config_var_value.get() + '0'))
        self.scvp_point_button = ttk.Button(self.set_config_vars_page, text='.', command=lambda: self.new_config_var_value.set(self.new_config_var_value.get() + '.'))
        self.scvp_enter_button = ttk.Button(self.set_config_vars_page, text='\u23ce', command=self.set_config_vars)
        self.scvp_backspace_button = ttk.Button(self.set_config_vars_page, text='\u232b', command=lambda: self.new_config_var_value.set(self.new_config_var_value.get()[:-1]))
        
        self.warning_label_value = StringVar()
        self.red_frame_style = ttk.Style()
        self.blue_frame_style = ttk.Style()
        self.yellow_frame_style = ttk.Style()
        self.red_frame_style.configure('Red.TFrame',background='red')
        self.blue_frame_style.configure('Blue.TFrame',background='blue')
        self.yellow_frame_style.configure('Yellow.TFrame',background='yellow')
        #self.flash_warning_frame = False
        
        self.warning_label = ttk.Label(self.root,textvariable=self.warning_label_value)
        self.warning_frame = ttk.Frame(self.root, width=225, height=30, borderwidth=4, relief='ridge')
        
        ##################
        #tkinter UI setup#
        ##################
        self.main_frame.grid(column=0, row=0, columnspan=2, sticky='nwes')
        self.notebook.grid(column=0, row=0, sticky='nwes')
        #self.main_page.columnconfigure(2,weight=1)
        self.main_page.rowconfigure(0,weight=1)
        self.main_page.rowconfigure(1,weight=1)
        self.main_page.rowconfigure(2,weight=1)
        
        self.mp_about_button.grid(column=0,row=0,sticky='s')
        self.mp_disclaimer_button.grid(column=0,row=1,sticky='s')
        self.mp_horiz_separator.grid(column=0,row=2,sticky='we')
        self.mp_shutdown_button.grid(column=0,row=3,sticky='n')
        self.mp_verti_separator.grid(column=1,row=0,rowspan=4,sticky='ns')
        self.mp_help_label_frame.grid(column=2,row=0,rowspan=4,sticky='new')
        self.mp_cp_help_button.grid(column=0,row=0,sticky='nswe')
        self.mp_scvp_help_button.grid(column=0,row=1,sticky='nswe')
        
        self.cp_frame_combobox_label.grid(column=0,row=0,columnspan=2)
        self.cp_frame_combobox.grid(column=0,row=1,columnspan=2)
        self.cp_horiz_separator.grid(column=0,row=2,columnspan=2,sticky='we')
        self.cp_threshold_spinbox_label.grid(column=0,row=3,columnspan=2)
        self.cp_threshold_spinbox.grid(column=0,row=4,columnspan=2)
        self.cp_warping_spinbox_label.grid(column=0,row=5,columnspan=2)
        self.cp_warping_spinbox.grid(column=0,row=6,columnspan=2)
        self.cp_warping_checkbutton.grid(column=0,row=7,columnspan=2)
        self.cp_feed_label.grid(column=2,row=0,rowspan=7)
        
        
        self.scvp_entry_result.grid(column=0,row=0,columnspan=6,sticky='we')
        self.scvp_entry.grid(column=0,row=1,columnspan=6,sticky='we')
        self.scvp_var_combobox_label.grid(column=6,row=0,sticky='we')
        self.scvp_var_combobox.grid(column=6,row=1,sticky='we')
        self.scvp_horiz_separator.grid(column=0,row=2,columnspan=9,sticky='we')
        self.scvp_1_button.grid(column=0,row=3)
        self.scvp_2_button.grid(column=1,row=3)
        self.scvp_3_button.grid(column=2,row=3)
        self.scvp_4_button.grid(column=3,row=3)
        self.scvp_5_button.grid(column=4,row=3)
        self.scvp_0_button.grid(column=5,row=3)
        self.scvp_6_button.grid(column=0,row=4)
        self.scvp_7_button.grid(column=1,row=4)
        self.scvp_8_button.grid(column=2,row=4)
        self.scvp_9_button.grid(column=3,row=4)
        self.scvp_point_button.grid(column=4,row=4)
        self.scvp_backspace_button.grid(column=5,row=4)
        self.scvp_enter_button.grid(column=6,row=3,rowspan=2)
        
        self.warning_label.grid(column=0,row=2,sticky='nsw')
        self.warning_frame.grid(column=1,row=2,sticky='nes')
        
        for child in list(self.main_page.winfo_children() + self.camera_page.winfo_children() + self.set_config_vars_page.winfo_children() + self.mp_help_label_frame.winfo_children()):
            child.grid_configure(padx=2, pady=2)

        self.cp_frame_combobox['width'] = len(self.cp_frame_combobox_label['text']) - 5
        
        for child in self.set_config_vars_page.winfo_children():
            if type(child) == ttk.Button and child != self.scvp_enter_button:
                child['width'] = len(child['text']) + 3
        
        self.scvp_var_combobox['width'] = len(sorted(self.scvp_var_combobox['values'],key=len)[-1]) - 2
        
        #This prevents the user from "X-ing" out of the program.
        self.root.protocol('WM_DELETE_WINDOW', self.do_nothing)
            
    def begin(self):
        """
        Checks to make sure that all of the configuration variables are in check, and the OBD and camera are connected, warning the user if not, then launches the user interface.
        """
        
        if self.need_to_set_config_vars:
            messagebox.showinfo(message='Sorry, at least one of the configuration variables is non-existant or not acceptable.', detail='Go to the "Set Config. Vars." tab to find the variables that equal -1 and give them an acceptable value.')
        if self.data_vars_defaulted:
            messagebox.showinfo(message='Sorry, at least one of the data variables is non-existant or not acceptable.', detail='Any of the data variables that were problematic have been set to their default values. Make sure to reconfigure those variables in the "Camera" tab.')
        if not self.camera_connected:
            messagebox.showinfo(message='Sorry, a camera connection could not be establish.', detail='Check the cabel between LaDD and the Raspberry Pi V2 Camera Module and make sure it is snuggly connected to both.')
        if not self.OBD_connnected:
            messagebox.showinfo(message='Sorry, an OBD connection could not be establish.', detail='Check both your physical connection between your vehicle\'s OBD port and that of LaDD\'s serial port, as well as the current value of the "Baud Rate" configuration variable, which may not be suited to your vehicle.')
        
        if not self.shared_dict['turn_off_LaDD']:
            #16 milliseconds represents 62.5 frames per second, about 60 frames per second
            self.root.after(16,self.update_feed_frame)
            self.root.after(16,self.update_warning)
        self.root.mainloop()
            
    def do_nothing(self):
        """
        Acts as a dummy method for "root's" "protocol" "WM_DELETE_WINDOW," which disables the "X" button on the user interface's windows.
        """
        
        pass
    
    def about_window(self):
        """
        Displays the "About" statement in a generic information window.
        """
        
        messagebox.showinfo(message='LaDD ("La"ne "D"etection "D"evice)', detail='Version 1.0')
    
    def cp_help_window(self):
        """
        Displays the "'Camera' Help" statement in a generic information window.
        """
        
        messagebox.showinfo(message='The "Camera" tab is where the camera feed is displayed.', detail='The "Processed Frame" option shows "lines" on the road (green), "lane lines" (blue), the "divider" (orange), and the sides of the vehicle (red). The "First Row for Warping" Option has to do with which row and it\'s "succesor" below it are used to warp the ROI frame.')
    
    def scvp_help_window(self):
        """
        Displays the "'Set Config. Vars." statement in a generic information window.
        """
        
        messagebox.showinfo(message='The "Set Config. Vars." tab is where the value of the different configuration variables can be seen and changed.', detail='Note: the metric system is used when possible. If you leave the entry field blank, it will display the current value of the select variable. Also, after any of the configuration variables are changed, it requires the restart of LaDD for the changes to come into effect.')
    
    def disclaimer_window(self):
        """
        Displays the disclaimer statement in a generic tkinter information dialog window.
        """
        
        messagebox.showinfo(message='Disclaimer',detail= 'WARNING: This device is not intended as a substitute for normal driving skill and/or driver attentiveness. Drivers are cautioned to use this device only as an aid and not to rely on this device to the exclusion of the normal and proper methods for safe driving. The design/manufacturer is not responsible for accidents or injuries which may occur while this device is in use.')
    
    def shutdown_window(self):
        """
        Creates an "Shutdown_Dialog_Window" instance that produces a special "yes/no" dialog window with a built-in 5-second timer that automatically closes the window without shutting down LaDD.
        """
        
        Shutdown_Dialog_Window(self.root,self.shutdown)
    
    def shutdown(self):
        """
        Closes LaDD's user interface and signals via "shared_dict's" "turn_off_LaDD" key to all of the other processes to end, effectively shutting down LaDD.
        """
        
        self.set_data_vars()
        self.shared_dict['turn_off_LaDD'] = True
        self.root.quit()
        self.root.destroy()
        
    def show_both_rows_for_warping(self):
        """
        Determines whether to show or hide red lines that denote "shared_dict's" "first_row_for_warping," as well as the row after it, in "shared_dict's" "ROI_frame."
        """
        
        if self.cp_warping_checkbutton_value.get() == '0':
            self.shared_dict['show_both_rows_for_warping'] = False
        else:
            self.shared_dict['show_both_rows_for_warping'] = True
            
    def update_binary_threshold_value_lower_end(self):
        """
        Updates the value of "shared_dict's" "binary_threshold_value_lower_end" by setting it to "cp_threhold_spinbox_value" when it is editted.
        """
        
        self.shared_dict['binary_threshold_value_lower_end'] = int(self.cp_threshold_spinbox_value.get())
    
    def update_first_row_for_warping(self):
        """
        Updates the value of "shared_dict's" "first_row_for_warping" by setting it to "cp_warping_spinbox_value" when it is editted.
        """
        
        self.shared_dict['first_row_for_warping'] = int(self.cp_warping_spinbox_value.get())
        
    def update_feed_frame(self):
        """
        Updates what is being displayed in the "cp_feed_label" with the latest images from "shared_dict's" "full_frame", "ROI_frame", or "processed_ROI_frame," depending on what was selected in the "cp_frame_combobox," after they were converted into usable tkinter images and stored in "ImageTk_obj."
        """
        
        if self.feed_name.get() == 'Full Frame' and self.shared_dict['full_frame'] != []:
            self.Image_obj = PIL.Image.fromarray(self.shared_dict['full_frame'],'RGB')
            self.Image_obj = self.Image_obj.resize((int(self.shared_dict['full_frame'].shape[1]/3.75),int(self.shared_dict['full_frame'].shape[0]/3.75)),PIL.Image.LANCZOS)
        elif self.feed_name.get() == 'Region of Interest Frame' and self.shared_dict['ROI_frame'] != []:
            self.Image_obj = PIL.Image.fromarray(self.shared_dict['ROI_frame'],'RGB')
            self.Image_obj = self.Image_obj.resize((int(self.shared_dict['ROI_frame'].shape[1]/1.5),int(self.shared_dict['ROI_frame'].shape[0]/1.5)),PIL.Image.LANCZOS)
        elif self.feed_name.get() == 'Warped ROI Frame' and self.shared_dict['warped_ROI_frame'] != []:
            self.Image_obj = PIL.Image.fromarray(self.shared_dict['warped_ROI_frame'],'RGB')
            self.Image_obj = self.Image_obj.resize((int(self.shared_dict['warped_ROI_frame'].shape[1]/1.5),int(self.shared_dict['warped_ROI_frame'].shape[0]/1.5)),PIL.Image.LANCZOS)
        elif self.feed_name.get() == 'Processed ROI Frame' and self.shared_dict['processed_ROI_frame'] != []:
            self.Image_obj = PIL.Image.fromarray(self.shared_dict['processed_ROI_frame'],'RGB')
            self.Image_obj = self.Image_obj.resize((int(self.shared_dict['processed_ROI_frame'].shape[1]/1.5),int(self.shared_dict['processed_ROI_frame'].shape[0]/1.5)),PIL.Image.LANCZOS)
        else:
            self.Image_obj = None
            
        if self.Image_obj != None:
            self.ImageTk_obj = PIL.ImageTk.PhotoImage(image=self.Image_obj)
            self.cp_feed_label['image'] = self.ImageTk_obj
        else:
            self.cp_feed_label['image'] = ""
        
        if not self.shared_dict['turn_off_LaDD']:
            self.root.after(16,self.update_feed_frame)
    
    def update_warning(self):
        """
        Checks to see if there is something for LaDD to warn the user about, and if there is it changes "warning_label" and "warning_frame" accordingly.
        """
        
        if not self.shared_dict['below_48kph']:
            if self.shared_dict['crossed_lane'] or self.shared_dict['crossed_divider']:
                self.warning_frame['style'] = 'Red.TFrame'
                if self.shared_dict['crossed_lane']:
                    self.warning_label_value.set('Crossed a lane!')
                else:
                    self.warning_label_value.set('Crossed the divider!')
            elif self.shared_dict['nothing_detected']:
                self.warning_frame['style'] = 'Blue.TFrame'
                self.warning_label_value.set('Nothing detected.')
            else:
                self.warning_frame['style'] = 'TFrame'
                self.warning_label_value.set('')
        else:
            self.warning_frame['style'] = 'Yellow.TFrame'
            self.warning_label_value.set('Below 30 mph.')
        
        if not self.shared_dict['turn_off_LaDD']:
            self.root.after(16,self.update_warning)
            
    @staticmethod
    def get_X_vars_helper(name_of_csv_file, X_var1, X_var2):
        """
        "Reads" the .csv files of LaDD ("configure.csv" or "data.csv"), searches for their respective "variables", makes up for incomplete or missing variables, updates the .csv files (possibly fixing and shortening them), then returns its findings; used by "get_config_vars" and "get_data_vars".
        
        Return arguments:
         * X_vars [list] -> A list of two lists whose first elements are a variable "located" in the .csv file being looked at, and whose second element are the value of that variable.
        """
        
        X_vars = []
        
        with open(name_of_csv_file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            rows = [row for row in reader]
        
        found_X_vars = {X_var1:False,X_var2:False}
		
        for row in rows:
            if len(row) > 0:
                if row[0] == X_var1:
                    if not found_X_vars[ X_var1]:
                        found_X_vars[ X_var1] = True
                        X_vars.append(row)
                elif row[0] == X_var2:
                    if not found_X_vars[ X_var2]:
                        found_X_vars[ X_var2] = True
                        X_vars.append(row)
        
        for variable in enumerate(X_vars,0):
            if len(variable[1]) == 1:
                X_vars[variable[0]] = [variable[1][0],'']
        
        if not found_X_vars[X_var1]:
            X_vars.append([X_var1,''])
        if not found_X_vars[ X_var2]:
            X_vars.append([ X_var2,''])
        
        with open(name_of_csv_file, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(X_vars)
        
        return X_vars
    
    @staticmethod
    def get_config_vars():
        """
        Passes "configure.csv" and the configuration variables' names to "get_X_vars_helper" to get the variables and their values, checks to see if all of the configuration variables are acceptable and accounted for, and then returns its findings.
         
        Return Arguments:
         * return_list [list] -> The first element is a bool, which is the answer to the question "Do any of the 'configuration variables' equal '', '0', or '.'?", and its second element is another list whose values are that of the "configuration variables," whether those in "configure.csv" or those given.
        """
        
        config_vars = User_Interface.get_X_vars_helper('configure.csv','vehicle_width','baud_rate')
        #config_vars = configuration variables
        
        return_list = [True,{'vehicle_width':0,'baud_rate':0}]
        
        for var in config_vars:
            if (var[1] != '') and (float(var[1]) > 0) and (var[1] != '.'):
                if var[0] == 'vehicle_width':
                    return_list[1][var[0]] = float(var[1])
                else:
                    return_list[1][var[0]] = int(var[1])
            else:
                return_list[1][var[0]] = -1
                return_list[0] = False
        
        return return_list
        
    @staticmethod
    def get_data_vars():
        """
        Passes "data.csv" and the data variables' names to "get_X_vars_helper" to get the variables and their values, checks to see if all of the data variables are acceptable and accounted for, and then returns its findings.
         
        Return Arguments:
         * return_list [list] -> The first element is a bool, which is the answer to the question "Do any of the 'data variables' equal '' or '.'?", and its second element is another list whose values are that of the "data variables," whether those in "data.csv" or those given.
        """
        
        data_vars = User_Interface.get_X_vars_helper('data.csv','binary_threshold_value_lower_end','first_row_for_warping')
        #data_vars = data variables
        
        return_list = [True,{'binary_threshold_value_lower_end':0,'first_row_for_warping':0}]
        
        for var in data_vars:
            if (var[1] != '') and ('.' not in var[1]):
                if (int(var[1]) >= 0) and ((var[0] == 'binary_threshold_value_lower_end' and int(var[1]) <= 255) or (var[0] == 'first_row_for_warping' and int(var[1]) <= 59)):
                    return_list[1][var[0]] = int(var[1])
                else:
                    if var[0] == 'binary_threshold_value_lower_end':
                        return_list[1]['binary_threshold_value_lower_end'] = 130
                    else:
                        return_list[1]['first_row_for_warping'] = 47
            else:
                if var[0] == 'binary_threshold_value_lower_end':
                    return_list[1]['binary_threshold_value_lower_end'] = 130
                else:
                    return_list[1]['first_row_for_warping'] = 47
                return_list[0] = False
        
        return return_list

    def set_config_vars(self):
        """
        Checks to see if the value of "new_config_var_value" is "acceptable," sets the configuration variable selected in "config_var_name" to "new_config_var_name" if the latter was acceptable, then finally tells the user of the success of setting a new value to a given configuration variable, or instead what was wrong with their value they entered into "scvp_entery."
        """
        
        if self.new_config_var_value.get()=='':
            if self.config_var_name.get() == 'Vehicle width':
                self.outcome.set('Current vehicle width: ' + str(self.shared_dict['vehicle_width']))
            elif self.config_var_name.get() == 'Baud rate':
                self.outcome.set('Current baud rate: ' + str(self.shared_dict['baud_rate']))
            self.root.after(5000,lambda:self.outcome.set(''))
        elif self.new_config_var_value.get()!='.':
            used_a_point = False
            acceptable = True
            for x in self.new_config_var_value.get():
                if x == '.':
                    if not used_a_point:
                        used_a_point = True
                    else:
                        acceptable = False
                        break
                if x not in self.accepted_characters:
                    acceptable = False
                    break
            
            if acceptable:
                with open('configure.csv', 'w', newline='') as config:
                    writer = csv.writer(config)
                    if self.config_var_name.get() == 'Vehicle width':
                        writer.writerow(['vehicle_width',self.new_config_var_value.get()])
                    else:
                        writer.writerow(['vehicle_width',self.shared_dict['vehicle_width']])
                        
                    if self.config_var_name.get() == 'Baud rate':
                        writer.writerow(['baud_rate',self.new_config_var_value.get()])
                    else:
                        writer.writerow(['baud_rate',self.shared_dict['baud_rate']])
                
                self.outcome.set(self.config_var_name.get() + ' set.')
                self.root.after(2000,lambda:self.outcome.set(''))
            else:
                self.outcome.set('Unacceptable characters inputed: "' + self.new_config_var_value.get() + '".')
                self.root.after(2000,lambda:self.outcome.set(''))
        else:
            self.outcome.set('Unacceptable character inputed: "' + self.new_config_var_value.get() + '".')
            self.root.after(2000,lambda:self.outcome.set(''))
    
    def set_data_vars(self):
        """
        Sets the data variables' values equal to that of "cp_threshold_spinbox_value" and "cp_warping_spinbox_value."
        """
        
        with open('data.csv', 'w', newline='') as data:
            writer = csv.writer(data)
            writer.writerow(['binary_threshold_value_lower_end',self.shared_dict['binary_threshold_value_lower_end']])
            writer.writerow(['first_row_for_warping',self.shared_dict['first_row_for_warping']])
