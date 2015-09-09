#!/usr/bin/python
import RPi.GPIO as GPIO
from time import sleep

def delay(ms):
    sleep(ms/1000.)

class LCD:
    def __init__(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        #https://howto8165.files.wordpress.com/2014/08/rpi-pinout.png
        D0 = 17
        D1 = 18
        D2 = 27
        D3 = 22
        D4 = 23
        D5 = 24
        D6 = 25
        D7 = 4
        self.RS = 7   #Register Select
        self.E = 8    #Enable
        self.RW = 11  #Read/Write

        #All out
        allPins = (D0,D1,D2,D3,D4,D5,D6,D7,self.RS,self.E, self.RW)
        for pin in allPins:
            GPIO.setup(pin, GPIO.OUT)

        self.off(self.RW)

        self.dataPins = (D0,D1,D2,D3,D4,D5,D6,D7)
        self.position = 0
        self.row = 0
        self.column = -1

    def on(self, pin):
        GPIO.output(pin, 1)

    def off(self, pin):
        GPIO.output(pin, 0)

    def mask(self, num, bit):
        result = num & (1 << bit)
        return result!=0

    def port(self, num):
        bits = range(8)
        for bit in bits:
            if self.mask(num, bit):
                self.on(self.dataPins[bit])
            else:
                self.off(self.dataPins[bit])

    def strobe(self):
        self.on(self.E)
        delay(1)
        self.off(self.E)
        delay(1)

    def moveLine(self, line):
        if line < 0:
            raise("Negative move value")
        elif line > 3:
            raise("Line value off limit")

        self.column = 0
        if line == 0:
            self.row = 0
            self.sendMove(0)
        elif line == 1:
            self.row = 1
            self.sendMove(40)
        elif line == 2:
            self.row = 2
            self.sendMove(20)
        elif line == 3:
            self.row = 3
            self.sendMove(84)
    
    def writeChar(self, c):
        self.column+=1
        if self.column>=20:
            if self.row == 0:
                self.moveLine(1)
            elif self.row == 1:
                self.moveLine(2)
            elif self.row == 2:
                self.moveLine(3)
            elif self.row == 3:
                self.moveLine(0)
            
        self.sendData(ord(c))
        #print((c, self.row, self.column))

    def writeText(self, text):
        for c in text:
            self.writeChar(c)

    def clear(self):
        self.sendCommand(0x01)

    def init(self, D=True, C=False, B=False):
        command = 0x08 #Display on/off control
        if D:
            command|=0x04
        if C:
            command|=0x02
        if B:
            command|=0x01

        self.sendCommand(command)
        self.sendCommand(0x3F) #Set to 4 lines display

    def sendData(self, data):
        self.on(self.RS)
        self.port(data)
        self.strobe()

    def sendCommand(self, command):
        self.off(self.RS)
        self.port(command)
        self.strobe()

    def sendMove(self, position):
        self.sendCommand(0x80|position)

def CommandLineUse():
    import argparse
    lcd = LCD()
    parser = argparse.ArgumentParser(description="Display text to 4 lines character LCD")
    parser.add_argument("-c", "--cursor", action="store_true", help="display cursor")
    parser.add_argument("-b", "--blink", action="store_true", help="blink cursor")
    parser.add_argument("--demo", action="store_true", help="display demo text")
    parser.add_argument("--fill", action="store_true", help="fill screen with characters")
    parser.add_argument("text", nargs='?', help="text to display")

    args = parser.parse_args()
    #print(args)

    lcd.init(C=args.cursor, B=args.blink)
    lcd.clear()

    if args.demo:
        lcd.writeText("       Voici        ")
        lcd.writeText("     un message     ")
        lcd.writeText("        sur         ")
        lcd.writeText("  quatre lignes :)  ")
    elif args.fill:
        lcd.writeText("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ABCDEFGH")
    elif args.text:
        #print args.text
        lines = args.text.replace(r"\\\"",r"\\").split(r'\n')
        #print(lines)
        for line in lines:
            lcd.writeText(line)
    else:
        parser.print_help()

def PipeUse():
    lcd = LCD()
    lcd.init(C=False, B=False)
    lcd.clear()

    for line in stdin:
        lcd.writeText(line[:-1])

#Used as a tool (command line or accept text from stdin)
if __name__=="__main__":
    from sys import stdin
    if stdin.isatty():
        #Example: sudo python lcd.py '   Hello, World!!   '
        CommandLineUse()        
    else:
        #Example: /opt/vc/bin/vcgencmd measure_temp | sudo python lcd.py
        PipeUse()
