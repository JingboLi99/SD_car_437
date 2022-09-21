import picar_4wd as fc
import sys
import tty
import termios
import asyncio
import numpy as np
import math
from picar_4wd.servo import Servo
from picar_4wd.pwm import PWM

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
