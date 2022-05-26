#import RPi.GPIO as gp
import time
import board
import busio
from adafruit_ht16k33 import segments
import math
import adc
import statistics
import RPi.GPIO as gp
global beep
beep = 0
gp.setwarnings(False)
gp.setmode(gp.BCM)
gp.setup(13, gp.OUT, initial=gp.LOW)
gp.setup(19, gp.OUT, initial=gp.LOW)
gp.setup(26, gp.OUT, initial=gp.LOW)
gp.setup(23, gp.OUT, initial=gp.LOW)



class LunchLine:
    def __init__(self):
        self.students_enter = []
        self.students_time = []
    def student_in(self):
        global beep
        print(time.time())
        gp.output(23,gp.HIGH)
        beep = 5
        self.students_enter.append(time.time())
    def student_out(self):
        if(len(self.students_enter)>0):
            self.students_time.append(time.time()-self.students_enter.pop(0))
            self.get_avg()
    def get_avg(self):
        if(len(self.students_time)==0):
            return 0
        return statistics.mean(self.students_time[len(self.students_time)-5:])



#commonly used variables
global ppl_in_line
global on_in
global ll
ll = LunchLine()
on_in = False
global on_out
on_out = False
ppl_in_line = 0
def step_in():
    global on_in
    on_in = True

def step_out():
    global on_out
    on_out = True

def step_in_confirmed():
    global ppl_in_line
    global on_in
    global ll
    if(on_in):
        ppl_in_line += 1
        on_in = False
        ll.student_in()

def step_out_confirmed():
    global ppl_in_line
    global on_out
    global ll
    if(on_out):
        if(ppl_in_line > 0):
            ppl_in_line -= 1
        on_out = False
        ll.student_out()



        
















#setup photosensor
# Variable to hold how long the tripwire has been tripped
tripped_time_sec = 0
# Variable to keep track if something "tripped" the beam
is_tripped = False
# Variable for storing what "tripped" threshold should be in volts
TRIPPED_THRESHOLD=2.3
#Variable for total time in seconds to be tripped to count as entered/exited
TRIPPED_TIME_FOR_COUNT=0.25

def check_entrance_switch():
  global is_tripped
  global tripped_time_sec
  voltage = adc.get_adc(0)
  if(voltage < TRIPPED_THRESHOLD):
     # see if tripped for more than 2 seconds
     if(is_tripped):
       tripped_time_sec = tripped_time_sec + time.time()
       if(tripped_time_sec > TRIPPED_TIME_FOR_COUNT):
         step_in()
     else:
       tripped_time_sec = 0
       is_tripped = True
    # else not tripped (not dropped below 2.3v
  else:
     tripped_time_sec = 0
     is_tripped = False
     step_in_confirmed()


def check_exit_switch():
    global is_tripped_1
    global tripped_time_sec_1
    voltage = adc.get_adc(1)
    if(voltage < TRIPPED_THRESHOLD):
     # see if tripped for more than 2 seconds
        if(is_tripped_1):
            tripped_time_sec_1 = tripped_time_sec_1 + time.time()
            if(tripped_time_sec_1 > TRIPPED_TIME_FOR_COUNT):
                step_out()
        else:
            tripped_time_sec_1 = 0
            is_tripped_1 = True
    # else not tripped (not dropped below 2.3v
    else:
        tripped_time_sec_1 = 0
        is_tripped_1 = False
        step_out_confirmed()
# Report the photoresistor  voltages to the terminal






#setup 7 segments displays
i2c =  busio.I2C(board.SCL, board.SDA)
display = segments.Seg7x4(i2c)
i = 0;
updated = 0

def light_on(id):
    gp.output(13, gp.LOW)
    gp.output(19, gp.LOW)
    gp.output(26, gp.LOW)
    gp.output(id, gp.HIGH)


display.fill(0)
while True:
    print(beep)
    if(beep > 0):
        beep -= 1
    if(beep <= 0):
        gp.output(23,gp.LOW)
    time.sleep(0.1)
    check_entrance_switch()
    check_exit_switch()
    updated += 1
    if(ppl_in_line == 0):
        light_on(26)
        if(math.floor(updated/25)%4 < 2):
            team_name = "fabdab "
            if(updated%2 == 0):
                display.print(team_name[math.floor(updated/2)%7])
        if(math.floor(updated/25)%4 == 2): 
            if(i>4):
                i = 0
            else:
                i = i+1
            display.set_digit_raw(0,2**i)
            display.set_digit_raw(1,2**(5-i))
            display.set_digit_raw(2,2**i)
            display.set_digit_raw(3,2**(5-i))
        if(math.floor(updated/25)%4 == 3):
            if(i>4):
                i = 0
            else:
                i = i+1
            display.set_digit_raw(0,2**i)
            display.set_digit_raw(1,2**i)
            display.set_digit_raw(2,2**i)
            display.set_digit_raw(3,2**i)
    else:
        if(ppl_in_line<10):
            light_on(26)
        elif(ppl_in_line<20):
            light_on(19)
        else:
            light_on(13)
        if(math.floor(updated/25)%2 == 0):
            display.print(";")
            display.print(str(ppl_in_line).zfill(4))
        else:
            display.print(":")
            time1 = int(ll.get_avg())
            minute = 0
            if(time1 > 60):
                minute = math.floor(time1/60)
                time1 = time1%60
            display.print(str(minute).zfill(2) + str(time1).zfill(2))




