#for mapping
import picar_4wd as fc
import sys
import tty
import termios
import asyncio
import numpy as np
import math
from picar_4wd.servo import Servo
from picar_4wd.pwm import PWM
#for object detector
import argparse
import sys
import time

import cv2
from tflite_support.task import core
from tflite_support.task import processor
from tflite_support.task import vision
import utils
#for pathfinding
import a_star_search as astar
class Mapping:
    def __init__(self):
        self.max_angle = 60
        self.min_angle = -63
        self.speed = 60
        self.dim = 300 #give even numbers
    def getXYCoords(self, dist, angle):
        xDist = abs(int(math.sin(math.radians(angle)) * dist))
        yDist = abs(int(math.cos(math.radians(angle)) * dist))
        yCoord = self.dim - 1 - yDist
        if angle < 0: # on right
            xCoord = int(self.dim/2)-1+xDist
        else:
            xCoord = int(self.dim/2)-1- xDist
        if xCoord > self.dim-1 or xCoord < 0 or yDist < 0: # if scanned object is out or range, return None
            return None
        return [xCoord, yCoord]
    def drawline(self, x, y):
        #check first quadrant: (quadrant size: 20x20)
        for r in range(y-19,y):
            for c in range(x, x+20):
                if self.omap[r][c] == 1:
                    self.bresenham(x,y,c,r)
        #check second quadrant: (quadrant size: 20x20)
        for r in range(y,y+19):
            for c in range(x, x+20):
                if self.omap[r][c] == 1:
                    self.bresenham(x,y,c,r)
                    
    def bresenham(self,x1,y1,x2,y2):
        m_new = 2*(y2-y1)
        slope_error_new = m_new - (x2 - x1)
        y = y1
        for x in range(x1, x2 + 1):
            self.omap[y][x] = 2
            slope_error_new = slope_error_new + m_new
            if(slope_error_new >= 0):
                y=y+1
                slope_error_new = slope_error_new - 2 * (x2-x1)
        self.omap[y1][x1] = 1
        self.omap[y2][x2] = 1
    def mapCurr(self):
        self.omap = np.zeros((self.dim, self.dim), dtype=int)
        sv = Servo(PWM("P3"))
        curr_angle = self.min_angle
        sv.set_angle(curr_angle)
        
        carRow = self.dim-1
        carCol = int(self.dim/2)-1
        # scanning env from -60 -> 60 deg and getting all obstacles marked 1
        while curr_angle <= self.max_angle:
            sv.set_angle(curr_angle)
            curr_obs_dis = fc.get_distance_at(curr_angle)
            obs_coords = self.getXYCoords(curr_obs_dis, curr_angle)
            if obs_coords: # if obj detected is not out of range
                print(obs_coords)
                curr_xCoord = obs_coords[0]
                curr_yCoord = obs_coords[1]
                self.omap[curr_yCoord][curr_xCoord] = 1
            curr_angle += 5
        sv.set_angle(0)
        #filling up gaps and un reachable areas
        #for every one we reach, try to reach other ones in first and second quadrant, using that 1 as centre point
        depth = len(self.omap)
        width = len(self.omap[0])
        for r in range(19, depth-19):
            for c in range(width-20):
                if self.omap[r][c] == 1:
                    self.drawline(c,r)
                    
                    
        for r in range(len(self.omap)):
            for c in range(len(self.omap[r])):
                if r==self.dim-1 and c in range(145,154):
                    print(7,end="")
                    continue
                print(self.omap[r][c],end="")
            print("")
        return self.omap
class Obj_detection:
    def run(self,model: str, camera_id: int, width: int, height: int, num_threads: int,
        enable_edgetpu: bool) -> None:
        """Continuously run inference on images acquired from the camera.

        Args:
        model: Name of the TFLite object detection model.
        camera_id: The camera id to be passed to OpenCV.
        width: The width of the frame captured from the camera.
        height: The height of the frame captured from the camera.
        num_threads: The number of CPU threads to run the model.
        enable_edgetpu: True/False whether the model is a EdgeTPU model.
        """

        # Variables to calculate FPS
        counter, fps = 0, 0
        start_time = time.time()

        # Start capturing video input from the camera
        cap = cv2.VideoCapture(camera_id)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        # Visualization parameters
        row_size = 20  # pixels
        left_margin = 24  # pixels
        text_color = (0, 0, 255)  # red
        font_size = 1
        font_thickness = 1
        fps_avg_frame_count = 10

        # Initialize the object detection model
        base_options = core.BaseOptions(
          file_name=model, use_coral=enable_edgetpu, num_threads=num_threads)
        detection_options = processor.DetectionOptions(
          max_results=3, score_threshold=0.3)
        options = vision.ObjectDetectorOptions(
          base_options=base_options, detection_options=detection_options)
        detector = vision.ObjectDetector.create_from_options(options)

        # Continuously capture images from the camera and run inference
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                sys.exit(
                  'ERROR: Unable to read from webcam. Please verify your webcam settings.'
                )

            counter += 1
            image = cv2.flip(image, 1)

            # Convert the image from BGR to RGB as required by the TFLite model.
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Create a TensorImage object from the RGB image.
            input_tensor = vision.TensorImage.create_from_array(rgb_image)

            # Run object detection estimation using the model.
            detection_result = detector.detect(input_tensor)
            #check for Stop sign and person
            detect_res = detection_result.detections
            for detection in detect_res:
                cat = detection.categories[0].category_name
                print(cat)
                if cat == 'stop sign' or cat == "person":
                    print("STOP HERE!!!!")
                    
            # Draw keypoints and edges on input image
            image = utils.visualize(image, detection_result)

            # Calculate the FPS
            if counter % fps_avg_frame_count == 0:
              end_time = time.time()
              fps = fps_avg_frame_count / (end_time - start_time)
              start_time = time.time()

            # Show the FPS
            fps_text = 'FPS = {:.1f}'.format(fps)
            text_location = (left_margin, row_size)
            cv2.putText(image, fps_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                        font_size, text_color, font_thickness)

            # Stop the program if the ESC key is pressed.
            if cv2.waitKey(1) == 27:
                break
            cv2.imshow('object_detector', image)

        cap.release()
        cv2.destroyAllWindows()
    
    def driver(self):
        parser = argparse.ArgumentParser(
          formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument(
          '--model',
          help='Path of the object detection model.',
          required=False,
          default='efficientdet_lite0.tflite')
        parser.add_argument(
          '--cameraId', help='Id of camera.', required=False, type=int, default=0)
        parser.add_argument(
          '--frameWidth',
          help='Width of frame to capture from camera.',
          required=False,
          type=int,
          default=640)
        parser.add_argument(
          '--frameHeight',
          help='Height of frame to capture from camera.',
          required=False,
          type=int,
          default=480)
        parser.add_argument(
          '--numThreads',
          help='Number of CPU threads to run the model.',
          required=False,
          type=int,
          default=4)
        parser.add_argument(
          '--enableEdgeTPU',
          help='Whether to run the model on EdgeTPU.',
          action='store_true',
          required=False,
          default=False)
        args = parser.parse_args()

        self.run(args.model, int(args.cameraId), args.frameWidth, args.frameHeight,
          int(args.numThreads), bool(args.enableEdgeTPU))
        
def main():
    ## car maps all observable locations using ultrasonic sensor in a 300 by 300 numpy 2d array
    ##car directs towards a certain location in teh map using angle and distance calculation (camera)
    ## accounts for and avoids any obstacles, correcting for route in the way.
    
    #Map from current position
    mapper = Mapping()
    og_map = mapper.mapCurr()
    #Get shortest path:
    start = (149,299)
    end = (0,0)
    path = astar.astar(og_map, start, end)
    
    print(path)
    #detector = Obj_detection()
    #detector.driver()
    
    
    

if __name__ == "__main__":
    try: 
        main()
    finally: 
        fc.stop()