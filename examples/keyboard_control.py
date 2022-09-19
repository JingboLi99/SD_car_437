import picar_4wd as fc
import sys
import tty
import termios
import asyncio
from picar_4wd import Ultrasonic
from picar_4wd.pin import Pin

power_val = 50
key = 'status'
print("If you want to quit.Please press q")
def readchar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def readkey(getchar_fn=None):
    getchar = getchar_fn or readchar
    c1 = getchar()
    if ord(c1) != 0x1b:
        return c1
    c2 = getchar()
    if ord(c2) != 0x5b:
        return c1
    c3 = getchar()
    return chr(0x10 + ord(c3) - 65)

def Keyborad_control():
    us = Ultrasonic(Pin('D8'), Pin('D9'))
    while True:
        dis_val = us.get_distance()
        print(dis_val)
        if dis_val < 5.0:
            print('Obstacle detected')
            break
        global power_val
        key=readkey()
        if key=='6':
            if power_val <=90:
                power_val += 10
                print("power_val:",power_val)
        elif key=='4':
            if power_val >=10:
                power_val -= 10
                print("power_val:",power_val)
        if key=='s':
            fc.forward(power_val)
            
        elif key=='d':
            fc.turn_left(power_val)
            
        elif key=='w':
            fc.backward(power_val)
            
        elif key=='a':
            fc.turn_right(power_val)
            
        else:
            fc.stop()
        if key=='q':
            print("quit")  
            break  
if __name__ == '__main__':
    Keyborad_control()






