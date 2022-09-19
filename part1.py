import picar_4wd as fc
import time


speed = 70

def main():
    avoided = False
    while True:
        
        scan_list = fc.scan_step(35)
        if not scan_list:
            continue
        tmp = scan_list[3:7]
        # print(tmp)
        if tmp != [2,2,2,2]:
            print('here')
            fc.turn_right(speed)
            avoided = True
        else:
            if avoided:
                avoided = False
                #turn right for 0.1 sec
                st_time = time.time()
                while True:
                    curr_time = time.time()
                    if curr_time - st_time > 0.8:
                        break
                st_time = time.time()
                fc.turn_left(speed)
                #turn back left for 0.1sec
                while True:
                    curr_time = time.time()
                    if curr_time - st_time > 2.3:
                        break
                st_time = time.time()
                fc.turn_right(speed)
                while True:
                    curr_time = time.time()
                    if curr_time - st_time > 0.4:
                        break
            fc.forward(speed)

if __name__ == "__main__":
    try: 
        main()
    finally: 
        fc.stop()
