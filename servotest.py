import picar_4wd as fc
import sys
import tty
import termios
import asyncio

from picar_4wd.servo import Servo
from picar_4wd.pwm import PWM

max_angle = 60
min_angle = -60

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

def main():
    sv = Servo(PWM("P3"))
    curr_angle = 0
    sv.set_angle(curr_angle)
    while True:
        if curr_angle > max_angle:
            sv.set_angle(max_angle)
            curr_angle = max_angle
        elif curr_angle < min_angle:
            sv.set_angle(min_angle)
            curr_angle = min_angle
        
        key=readkey()
        
        if key=='d':
            print('d')
            sv.set_angle(curr_angle-5)
            curr_angle -= 5
        elif key=='a':
            print('a')
            sv.set_angle(curr_angle+5)
            curr_angle += 5
        elif key=='r':
            sv.set_angle(0)
            curr_angle =0
        
        else:
            print('Not a valid key command')
        if key=='q':
            print("quit")  
            break  

if __name__ == "__main__":
    try: 
        main()
    finally: 
        fc.stop()
