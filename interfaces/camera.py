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

import numpy as np
import cv2

"""
"camera" Module:

Packages Imported:
 * numpy (as np),
 * cv2.

Classes:
 * Camera -> An "interface" for LaDD's Pi Camera Module V2.
"""

class Camera:
    """
    Instance Variables:
     * AVERAGE_LANE_WIDTH [int (constant)] -> The average width of a lane in the US in meters.
     * shared_dict [multiprocessing.Manager.dict()] -> A special dictionary returned by the Manager object "manager_obj" located in LaDD's main.py, this is a dictionary shared across the different processes that constitute LaDD.
     * camera_res [list] -> The set resolution of the Pi Camera Module V2 in [width,height] (needs to be at least 320x80, as that is the size of "ROI").
     * row_slice {and} col_slice [list] -> The "range" of rows and columns in the captured, unprocesseed frame that make up the Region of Interest frame.
     * ROI [np.ndarray] -> The frame that is derived from "begin's" "frame" using "row_slice" and "col_slice."
     * AlteredROI [np.ndarray] -> The version of "ROI" that "shared_dict's" "ROI_frame" is set to instead of "ROI" when "shared_dict's" "show_both_rows_for_warping" is True, it shows with red lines what rows of "ROI" are being used to warp "ROI" into "WarpedROI."
     * WarpedROI [np.ndarray] -> The frame that is derived from a binary-thresholded "ROI" by using the "cv2.warpPerspective" method with "M" as an argument.
     * CannyROI [np.ndarray] -> The frame that is derived from "WarpedROI" by using the "cv2,Canny" method.
     * HoughROI [np.ndarray] -> The frame that is dervied from "CannyROI" by drawing the "Hough lines" found using the "cv2.HoughLinesP" method stored in "lines" onto "CannyROI."
     * pts1 {and} pts2 [np.ndarray] -> Two sets of for coresponding points of "ROI" before (pts1) and after (pts2) sent into "cv2.getPerspectiveTransform," with its outcome saved in "M."
     * M [np.ndarray] -> The result of running "cv2.getPerspectiveMapping" with "pts1" an "pts2" as arguments.
     * kernel [np.ndarray] -> The "structuring argument" passed into "cv2.morphologyEx" that is used on "WarpedROI" to "open" the image.
     * lines [np.ndarray] -> The lines found using "cv2.HoughLinesP" on "CannyROI."
     * avrg_x_coor_of_lines [list] -> The averages of the x-coordinates of the endpoints of the lines in "lines," which are displayed as vertical lines on "HoughROI" in green.
     * avrg_x_coor_of_lane_lines [list] -> Those average x-coordinates from "avrg_x_coor_of_lines" that form the "lane" on the road; if length equals 2, then both sides of a lane can be "seen"; if length equals 1, then one side of a lane can be "seen", and the vehicle is most likely crossing a lane; if length equals 0, then nothingis detected.
     * avrg_x_coor_of_divider_lines [list] -> Those average x-ccordinates from "avrg_x_coor_of_lines" that form the "divider" on the road; if length equals 4, then the entire divider can be "seen," but if otherwise then not the entire divider, if any of it, can be "seen." 
     * frames_taken [int] -> The number of frames taken since LaDD has been turned on; this is supposed to act as a buffer of sorts to prevent early, messy images from ruining averages and other calculated instance variables vital to LaDD's accuracy. When this variable equals 30, it is not incremented anymore and is "forgotten."
     * buffer_of_lane_frames [list] -> The "queue-like" list of the "avrg_x_coor_of_lane_lines" of frames, with index 0 being the newest "avrg_x_coor_lane_lines" value and the last one being removed when another value is added to the "front" of the list. This list is used to produce an "average" frame using multiple frames to determine where the vehicle is on the road in terms of its position in relation of "lane lines."
     * buffer_of_divider_frames [list] -> Like "buffer_of_lane_frames," except it stores the "avrg_x_coors_of_divider_lines" of frames. This list is used to produce an "average" frame using multiple frames to determine where the vehicle is on the road in terms of its position in relation of "divider lines."
     * state [str] -> The "state" of the vehicle ("in_lane," "out_lane," "no_lane," "over_divider") of the vehicle, determined on a frame-by-frame basis.
     * previous_state [str] -> The previous "state" of the vehicle determined from the last frame before the current one.
     * lane_frames_to_avrg [list] -> Assigned to and used in the "calculate_lane_avrg" and "calculate_lane_line_avrg" methods, depending on what is "available" in "buffer_of_lane_frames," they are the values in the "buffer_of_lane_frames" to average that result in the average x-coordinates of "lane lines" that are used in determining the "state" and are displayed on the "HoughROI" in blue.
     * divider_frames_to_avrg [list] -> Assigned to and used in "calculate_divider_avrg," they are the values in the "buffer_of_divider_frames" to average that result in the average x-coordinates of "divider lines" that are used in determining the "state" and are displayed on the "HoughROI" in orange.
     * avrg_lane_x1 {and} avrg_lane_x2 [int] -> Represent the x-coordinates averaged from "lane_frames_to_avrg"; if both do not equal None, then LaDD has "seen" a complete lane, and "avrg_lane_x1" and "avrg_lane_x2" are the left and right lines of that lane, respectively; if only "avrg_lane_x2" equals None, then LaDD thinks it has seen one line of a lane and "avrg_lane_x1" is that value; if both equal None, then LaDD has detected nothing..
     * avrg_divider_x1 {through} avrg_divider_x4 [int] -> Represent the x-coordinatesa avereage from "divider_frames_to_avrg"; if all do not equal None, then LaDD has seen a complete divider, and "avrg_lane_x1-4" are the first, second, third, and fourth lines of the divider from left to right; if all equal None, then LaDD has detected nothing.
     * meter_per_pixel [float] -> The meters-per-pixel calculated with "AVERAGE_LANE_WIDTH" and "avrg_lane_x1/2" (when the latter do not equal None) that used to find "vehicle_pixel_width."
     * vehicle_pixel_width [float] -> The width in pixels of the vehicle in "HoughROI."
     * vehicle_width_x_coors [list] -> The x-coordinates of the sides of the vehicle on a frame-by-frame basis.
     * count_for_averaging [int] -> The count to conduct a running average on "avrg_vehicle_width_x_coors" using each average frames' "vehicle_width_x_coors." When it equals to 1000, it is set to 1 for two reasons: one, if LaDD is run for a long time, without setting it to a small number, it would eventually grow in size and take up a vast amount of precious memory; two, by "reseting" to a degree the running average, it can allow for a recalculation of the "avrg_vehicle_width_x_coors" that could make its values more accurate.
     * avrg_vehicle_width_x_coors [list] -> The average x-coordinates of the sides of the vehicle.
    
    Methods:
     * __init__ -> Initiates the class, and prepares LaDD for the footage it will take.
     * calculate_avrg_vehicle_width_x_coors -> Calculates the vehicle's sides' average x-coordinates via a running average.
     * calculate_lane_line_avrg -> Called by "calculate_lane_avrg" if the two sides of a lane had not be detected, it atempts to average all lists with a length of 1 in "buffer_of_lane_frames," which are considered to be one side of a lane, else both "avrg_lane_x1/2" are set to None.
     * calculate_lane_avrg -> Attempts to average all of the lists with a length of 2 in "buffer_of_lane_frames," which are considered to be the two sides of a lane, else calls "calculate_lane_line_avrg."
     * calculate_divider_avrg -> Attempts to average all of the lists with a length of 4 in "buffer_of_divider_frames," which are considered to be the four lines of an entire divider, else "avrg_divider_x1-4" are set to None.
     * begin -> Runs the main camera loop that captures footage, processes it, and makes the decisions off of it of whether to warn the user and if so what for ("in_lane","out_lane","over_divider","no_lane").
     * test_camera_connection [static] -> Tests whether or not a connection to a Pi Camera Module V2 can be established.
    """
    
    def __init__(self, shared_dict, camera_res):
        """
        Initiates the class, and prepares LaDD for the footage it will take.
        
        Arguments:
         * shared_dict [multiprocessing.Manager.dict()] ->
         * camera_res [list] ->
        """
        
        self.AVERAGE_LANE_WIDTH = 3
        #3.048 is exactly 10 feet.
        
        self.shared_dict = shared_dict
        self.camera_res = camera_res
        
        self.row_slice = [(self.camera_res[1]/2)-30,(self.camera_res[1]/2)+30]
        self.col_slice = [(self.camera_res[0]/2)-160,(self.camera_res[0]/2)+160]
        
        self.ROI = []
        #ROI = Region Of Interest.
        self.AlteredROI = []
        #AlteredROI = A copy of "ROI" used to display with red lines what rows of "ROI" are being used to warp "ROI" into "WarpedROI," but "AlteredROI" itself is not used to create "WarpedROI."
        self.WarpedROI = []
        #WarpedROI = Perspective Transformation applied on binary-thresholded "ROI."
        self.CannyROI = []
        #CannyROI = Canny Edge Detection applied on "WarpedROI."
        self.HoughROI = []
        #HoughROI = Probabilistic Hough Lines Transformation applied to "CannyROI," and lines returned as a result are drawn on "HoughROI."
        
        self.pts1 = []
        #pts1 = (column,row) coordinates of the unwarped "ROI"
        self.pts2 = np.float32([[0,0],[320,0],[0,60],[320,60]])
        #pts2 = (column,row) coordinates of where pts1 are to be in the newly warped "WarpedROI."
        self.M = 0
        #M = result of cv2.getPerspectiveTransform for warping "ROI."
        self.kernel = np.ones((5,5),np.uint8)
        #kernel used in "opening" "WarpedROI."
        
        self.lines = 0
        #Lines return from Probabilistic Hough Transformation.
        
        self.avrg_x_coor_of_lines = []
        self.avrg_x_coors_of_lane_lines = []
        self.avrg_x_coors_of_divider_lines = []
        
        self.frames_taken = 0
        self.buffer_of_lane_frames = [[],[],[],[]]
        self.buffer_of_divider_frames = [[],[],[],[]]
        
        self.state = None
        #state = the "state" ('in_lane','out_lane," "no_lane," over_divider," "undetermined") of the vehicle. "undetermined" is a temporary state which is shortly replaced by either "in_lane," "out_lane," or "no_lane."
        self.previous_state = None
        self.lane_frames_to_avrg = []
        self.divider_frames_to_avrg = []
        
        self.avrg_lane_x1 = 0
        self.avrg_lane_x2 = 0
        self.avrg_divider_x1 = 0
        self.avrg_divider_x2 = 0
        self.avrg_divider_x3 = 0
        self.avrg_divider_x4 = 0
        
        self.meter_per_pixel = 0
        self.vehicle_pixel_width = 0
        
        self.vehicle_width_x_coors = [0,0]
        self.count_for_averaging = 0
        self.avrg_vehicle_width_x_coors = []
    
    
    #The below two methods are for testing purposes only, not for actual use in LaDD.
    '''
    def save_camera_feed(self):
        cap = cv2.VideoCapture(0)
        
        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        out = cv2.VideoWriter('-video.avi',fourcc, 60.0, (640,480))
        
        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret==True:
                cv2.imshow('Full Frame',frame)
                self.ROI = frame[self.row_slice[0]:self.row_slice[1],self.col_slice[0]:self.col_slice[1]]
                cv2.imshow('Color ROI frame',self.ROI)
                out.write(frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                break
        
        # Release everything if job is finished
        cap.release()
        out.release()
        cv2.destroyAllWindows()
    
    def view_camera_feed(self):
        cap = cv2.VideoCapture("-video.avi")
        #count = 0
        
        while cap.isOpened():
            ret,frame = cap.read()
            if ret:
                cv2.imshow('Full Frame',frame)
                self.ROI = frame[self.row_slice[0]:self.row_slice[1],self.col_slice[0]:self.col_slice[1]]
                cv2.imshow('Color ROI',self.ROI)
            else:
                break
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
               break
        
        cap.release()
        cv2.destroyAllWindows()
    '''
    
    def calculate_avrg_vehicle_width_x_coors(self):
        """
        Calculates the vehicle's sides' average x-coordinates via a running average.
        
        Internal Functions:
         * calculate_running_avrg -> Calculates the running average.
        """
        
        def calculate_running_avrg(newValue, oldValue):
            """
            Calculates the running average.
            
            Arguments:
             * newValue [float] -> The new value to be added to the running average.
             * oldValue [int] -> The previous value of the running average needed to continue the running average.
            """
            
            return int(oldValue + ((newValue - oldValue)/self.count_for_averaging))
        
        self.vehicle_width_x_coors = [(((self.HoughROI.shape[1]/2)-1)-(self.vehicle_pixel_width/2)),(((self.HoughROI.shape[1]/2)-1)+(self.vehicle_pixel_width/2))]
        if self.count_for_averaging == 0:
            self.avrg_vehicle_width_x_coors = [int(self.vehicle_width_x_coors[0]),int(self.vehicle_width_x_coors[1])]
        else:
            self.avrg_vehicle_width_x_coors = [calculate_running_avrg(self.vehicle_width_x_coors[0] ,self.avrg_vehicle_width_x_coors[0]), calculate_running_avrg(self.vehicle_width_x_coors[1] ,self.avrg_vehicle_width_x_coors[1])]
        
        self.count_for_averaging+=1
        
        if self.count_for_averaging >= 1000:
            self.count_for_averaging = 1
    
    def calculate_lane_line_avrg(self):
        """
        Called by "calculate_lane_avrg" if the two sides of a lane had not be detected, it atempts to average all lists with a length of 1 in "buffer_of_lane_frames," which are considered to be one side of a lane, else both "avrg_lane_x1/2" are set to None.
        """
        
        self.lane_frames_to_avrg = [x[0] for x in self.buffer_of_lane_frames if len(x) == 1]
        if len(self.lane_frames_to_avrg) >0:
            for x in self.lane_frames_to_avrg:
                self.avrg_lane_x1 += x
            self.avrg_lane_x1 = int(self.avrg_lane_x1/len(self.lane_frames_to_avrg))
        else:
            self.avrg_lane_x1 = None
        self.avrg_lane_x2 = None
    
    def calculate_lane_avrg(self):
        """
        Attempts to average all of the lists with a length of 2 in "buffer_of_lane_frames," which are considered to be the two sides of a lane, else calls "calculate_lane_line_avrg."
        """
        
        self.avrg_lane_x1 = self.avrg_lane_x2 = 0
        self.lane_frames_to_avrg = [x for x in self.buffer_of_lane_frames if len(x) == 2]
        if len(self.lane_frames_to_avrg) > 0:
            for x in self.lane_frames_to_avrg:
                self.avrg_lane_x1 += x[0]
                self.avrg_lane_x2 += x[1]
            self.avrg_lane_x1 = int(self.avrg_lane_x1/len(self.lane_frames_to_avrg))
            self.avrg_lane_x2 = int(self.avrg_lane_x2/len(self.lane_frames_to_avrg))
            
            self.meter_per_pixel = self.AVERAGE_LANE_WIDTH/(self.avrg_lane_x2 - self.avrg_lane_x1)
            self.vehicle_pixel_width = (1.0/self.meter_per_pixel) * self.shared_dict['vehicle_width']
            self.calculate_avrg_vehicle_width_x_coors()
        else:
            self.calculate_lane_line_avrg()
    
    def calculate_divider_avrg(self):
        """
        Attempts to average all of the lists with a length of 4 in "buffer_of_divider_frames," which are considered to be the four lines of an entire divider, else "avrg_divider_x1-4" are set to None.
        """
        
        self.avrg_divider_x1 = self.avrg_divider_x2 = self.avrg_divider_x3 = self.avrg_divider_x4 = 0
        self.divider_frames_to_avrg = [x for x in self.buffer_of_divider_frames if len(x) == 4]
        if len(self.divider_frames_to_avrg) > 0:
            for x in self.divider_frames_to_avrg:
                self.avrg_divider_x1 += x[0]
                self.avrg_divider_x2 += x[1]
                self.avrg_divider_x3 += x[2]
                self.avrg_divider_x4 += x[3]
            self.avrg_divider_x1 = int(self.avrg_divider_x1/len(self.divider_frames_to_avrg))
            self.avrg_divider_x2 = int(self.avrg_divider_x2/len(self.divider_frames_to_avrg))
            self.avrg_divider_x3 = int(self.avrg_divider_x3/len(self.divider_frames_to_avrg))
            self.avrg_divider_x4 = int(self.avrg_divider_x4/len(self.divider_frames_to_avrg))
        else:
            self.avrg_divider_x1 = self.avrg_divider_x2 = self.avrg_divider_x3 = self.avrg_divider_x4 = None
    
    def begin(self):
        """
        Runs the main camera loop that captures footage, processes it, and makes the decisions off of it of whether to warn the user and if so what for ("in_lane","out_lane","over_divider","no_lane").
        """
        
        cap = cv2.VideoCapture(0)
        #If you want to pull frames from an actual camera feed, pass 0 as an argument in the above "cv2.VideoCapture" object constructor. Ex: cv2.VideoCapture(0)
        #If you want to use the provided test footage in the "test_footage" directory, pass the string "test_footage/" plus the file name of the test footage. Ex: cv2.VideoCapture("test_footage/WTSB_West-video2.avi")
        #Note: "WTSB_East-video3.avi" is very glitchy, as well as "WTSB_West-video1.avi."
        
        while not self.shared_dict['turn_off_LaDD'] and cap.isOpened():
            ret, frame = cap.read()
            if ret:
                #Find the region of interest (ROI).
                self.shared_dict['full_frame'] = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
                #cv2.imshow("Full Frame", frame)
                self.ROI = frame[int(self.row_slice[0]):int(self.row_slice[1]),int(self.col_slice[0]):int(self.col_slice[1])]
                if self.shared_dict['show_both_rows_for_warping']:
                    self.AlteredROI = self.ROI.copy()
                    cv2.line(self.AlteredROI,(0,self.shared_dict['first_row_for_warping']),(320,self.shared_dict['first_row_for_warping']),(0,0,255),2)
                    cv2.line(self.AlteredROI,(0,self.shared_dict['first_row_for_warping']+1),(320,self.shared_dict['first_row_for_warping']+1),(0,0,255),2)
                    self.shared_dict['ROI_frame'] = cv2.cvtColor(self.AlteredROI,cv2.COLOR_BGR2RGB)
                else:
                    self.shared_dict['ROI_frame'] = cv2.cvtColor(self.ROI,cv2.COLOR_BGR2RGB)
                #cv2.imshow('Color ROI',self.ROI)
                
                self.ROI = cv2.cvtColor(self.ROI,cv2.COLOR_BGR2GRAY)
                #cv2.imshow('Grey ROI',self.ROI)
        
                #Apply a binary threshold on the ROI.
                ret,self.ROI = cv2.threshold(self.ROI,self.shared_dict['binary_threshold_value_lower_end'],255,cv2.THRESH_BINARY)
                #cv2.imshow('Thresholded ROI',self.ROI)
                
                #Then, warp the ROI to a top-down view.
                self.pts1 = np.float32([[0,self.shared_dict['first_row_for_warping']],[320,self.shared_dict['first_row_for_warping']],[0,self.shared_dict['first_row_for_warping']+1],[320,self.shared_dict['first_row_for_warping']+1]])
                self.M = cv2.getPerspectiveTransform(self.pts1,self.pts2)
                self.WarpedROI = cv2.warpPerspective(self.ROI,self.M,(320,60))
                self.WarpedROI = cv2.morphologyEx(self.WarpedROI,cv2.MORPH_OPEN,self.kernel)
                self.shared_dict['warped_ROI_frame'] = cv2.cvtColor(self.WarpedROI, cv2.COLOR_GRAY2RGB)
                #cv2.imshow('WarpedROI',self.WarpedROI)
                
                #Then, apply Canny Edge Detection then Probabilistic Hough Transformation to find the endpoints of "lines" in the ROI, which are supposed to be the edges of the lines on a road.
                self.CannyROI = cv2.Canny(self.WarpedROI,200,225)
                #cv2.imshow('Canny ROI',self.CannyROI)
                self.lines = cv2.HoughLinesP(self.CannyROI,1.0,np.pi/180,30,minLineLength=30,maxLineGap=20)
                self.HoughROI = cv2.cvtColor(self.CannyROI,cv2.COLOR_GRAY2BGR)
                
                if self.lines != None:
                    if len(self.lines) <= 8:
                        for coor in self.lines:
                            for x1,y1,x2,y2 in coor:
                                self.avrg_x_coor_of_lines.append(((x2+x1)/2.0))
                                cv2.line(self.HoughROI,(x1,y1),(x2,y2),(0,255,0),2)
                        self.avrg_x_coor_of_lines.sort()
                        
                        if len(self.avrg_x_coor_of_lines) >= 2 and len(self.avrg_x_coor_of_lines) <= 10:
                            if len(self.avrg_x_coor_of_lines) >=4:
                                for x in range(len(self.avrg_x_coor_of_lines)-3):
                                    difference_A = self.avrg_x_coor_of_lines[x+1] - self.avrg_x_coor_of_lines[x]
                                    difference_B = self.avrg_x_coor_of_lines[x+2] - self.avrg_x_coor_of_lines[x+1]
                                    difference_C = self.avrg_x_coor_of_lines[x+3] - self.avrg_x_coor_of_lines[x+2]
                                    if (difference_A <= 12) and (difference_C <= 12) and (difference_B <= 16):
                                        #Divider detected
                                        self.avrg_x_coors_of_divider_lines = [self.avrg_x_coor_of_lines[x],self.avrg_x_coor_of_lines[x+1],self.avrg_x_coor_of_lines[x+2],self.avrg_x_coor_of_lines[x+3]]
                                        break
                                else:
                                    self.avrg_x_coors_of_divider_lines = []
                            else:
                                self.avrg_x_coors_of_divider_lines = []
                            for x in range(len(self.avrg_x_coor_of_lines)-1):
                                difference = self.avrg_x_coor_of_lines[x+1] - self.avrg_x_coor_of_lines[x]
                                if (difference >= 210) and (difference <= 240):
                                    #Full-lane detected
                                    self.avrg_x_coors_of_lane_lines = [self.avrg_x_coor_of_lines[x], self.avrg_x_coor_of_lines[x+1]]
                                    break
                            else:
                                #Right-side of divider detected
                                self.avrg_x_coors_of_lane_lines = [self.avrg_x_coor_of_lines[-1]]
                        else:
                            #Shoulder-line detected
                            self.avrg_x_coors_of_lane_lines = [self.avrg_x_coor_of_lines[0]]
                            self.avrg_x_coors_of_divider_lines = []
                    else:
                        #Nothing detected
                        self.avrg_x_coors_of_lane_lines = []
                        self.avrg_x_coors_of_divider_lines = []
                    
                    self.buffer_of_lane_frames.insert(0,[])
                    self.buffer_of_divider_frames.insert(0,[])
                    self.buffer_of_lane_frames[0] = self.avrg_x_coors_of_lane_lines
                    self.buffer_of_divider_frames[0] = self.avrg_x_coors_of_divider_lines
                    self.buffer_of_lane_frames.pop(-1)
                    self.buffer_of_divider_frames.pop(-1)
                    
                    #if len([x for x in self.buffer_of_lane_frames if len(x) == 2]) > 2:
                    self.calculate_lane_avrg()
                    #if len([x for x in self.buffer_of_divider_frames if len(x) == 4]) > 2:
                    self.calculate_divider_avrg()
                    
                    if self.frames_taken < 30:
                        self.frames_taken+=1
                    
                    if self.frames_taken >= 30 and len(self.avrg_vehicle_width_x_coors)==2 and not self.shared_dict['below_48kph']:
                        if self.state != 'over_divider':
                            if self.avrg_divider_x4 != None:
                                if self.avrg_vehicle_width_x_coors[0] >= self.avrg_divider_x4:
                                    self.state = 'undetermined'
                                else:
                                    self.state = 'over_divider'
                            else:
                                self.state = 'undetermined'
                        else:
                            if self.avrg_divider_x4 != None:
                                if self.avrg_vehicle_width_x_coors[0] < self.avrg_divider_x4:
                                    self.state = 'over_divider'
                                else:
                                    self.state = 'undetermined'
                            else:
                                self.state = 'over_divider'
                        
                        if self.state == 'undetermined':
                            if self.avrg_lane_x1 != None and self.avrg_lane_x2 != None:
                                if ((self.avrg_vehicle_width_x_coors[0] > self.avrg_lane_x1) and (self.avrg_vehicle_width_x_coors[1] > self.avrg_lane_x2)) or ((self.avrg_vehicle_width_x_coors[0] < self.avrg_lane_x1) and (self.avrg_vehicle_width_x_coors[1] < self.avrg_lane_x2)):
                                    self.state = 'out_lane'
                                else:
                                    self.state = 'in_lane'
                            elif self.avrg_lane_x1 != None and self.avrg_lane_x2 == None:
                                if ((self.avrg_vehicle_width_x_coors[0] < self.avrg_lane_x1) and (self.avrg_vehicle_width_x_coors[1] > self.avrg_lane_x1)):
                                    self.state = 'out_lane'
                            elif self.avrg_lane_x1 == None and self.avrg_lane_x2 == None:
                                self.state = 'no_lane'
                        
                        if self.state == self.previous_state:
                            if self.state == 'in_lane':
                                self.shared_dict['crossed_divider'] = False
                                self.shared_dict['crossed_lane'] = False
                                self.shared_dict['nothing_detected'] = False
                            elif self.state == 'out_lane':
                                self.shared_dict['crossed_divider'] = False
                                self.shared_dict['crossed_lane'] = True
                                self.shared_dict['nothing_detected'] = False
                            elif self.state == 'over_divider':
                                self.shared_dict['crossed_divider'] = True
                                self.shared_dict['crossed_lane'] = False
                                self.shared_dict['nothing_detected'] = False
                            elif self.state == 'no_lane':
                                self.shared_dict['crossed_divider'] = False
                                self.shared_dict['crossed_lane'] = False
                                self.shared_dict['nothing_detected'] = True
                        
                        if self.avrg_divider_x1 != None:
                            for l in [self.avrg_divider_x1, self.avrg_divider_x2, self.avrg_divider_x3, self.avrg_divider_x4]:
                                cv2.line(self.HoughROI,(int(l),0),(int(l),60),(0,165,255),2)
                                
                        if self.avrg_lane_x1 != None:
                            cv2.line(self.HoughROI,(int(self.avrg_lane_x1),0),(int(self.avrg_lane_x1),60),(255,0,0),2)
                        if self.avrg_lane_x2 != None:
                            cv2.line(self.HoughROI,(int(self.avrg_lane_x2),0),(int(self.avrg_lane_x2),60),(255,0,0),2)
    
                        if len(self.avrg_vehicle_width_x_coors) == 2:
                            cv2.line(self.HoughROI,(int(self.avrg_vehicle_width_x_coors[0]),0),(int(self.avrg_vehicle_width_x_coors[0]),60),(0,0,255),2)
                            cv2.line(self.HoughROI,(int(self.avrg_vehicle_width_x_coors[1]),0),(int(self.avrg_vehicle_width_x_coors[1]),60),(0,0,255),2)
                        
                        self.shared_dict['processed_ROI_frame'] = cv2.cvtColor(self.HoughROI,cv2.COLOR_BGR2RGB)
                    else:
                        self.state = 'no_lane'
                        self.shared_dict['crossed_divider'] = False
                        self.shared_dict['crossed_lane'] = False
                        self.shared_dict['nothing_detected'] = False
                        
                        self.shared_dict['processed_ROI_frame'] = []
                else:
                    self.state = 'no_lane'
                    self.shared_dict['crossed_divider'] = False
                    self.shared_dict['crossed_lane'] = False
                    self.shared_dict['nothing_detected'] = True
                                
                if self.previous_state == None or self.state != self.previous_state:
                    self.previous_state = self.state
                    
                self.avrg_x_coor_of_lines=[]
                
                cv2.waitKey(1)
                """
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.shared_dict['interfaces_on']['camera'] = False
                    break
                """
            else:
                break
        
        cap.release()
        cv2.destroyAllWindows()
    
    @staticmethod
    def test_camera_connection():
        """
        Tests whether or not a connection to a Pi Camera Module V2 can be established.
        
        Return Arguments:
         * result [bool] -> Represents whether a camera connection has been successfully established.
        """
        test_con = cv2.VideoCapture(0)
        result = test_con.isOpened()
        test_con.release()
        del test_con
        return result
