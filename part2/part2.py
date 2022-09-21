#for mapping
import mapper as mapper
#for object detection
import cv as cv
#for pathfinding
import a_star_search as astar


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
    #detector = cv()
    #detector.driver()
    
    


if __name__ == "__main__":
    try: 
        main()
    finally: 
        fc.stop()