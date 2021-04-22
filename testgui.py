# -*- coding:utf-8 -*-
#imports 
from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas
from luma.core.sprite_system import framerate_regulator
from luma.core import lib
from luma.oled.device import sh1106
import RPi.GPIO as GPIO
import datetime
import time
import subprocess
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import socket, sys
import os
import base64
import struct
import smbus

SCNTYPE = 1 # 1= OLED #2 = TERMINAL MODE BETA TESTS VERSION

bus = smbus.SMBus(2)  # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

GPIO.setwarnings(False)

# Load default font.
font = ImageFont.load_default()
# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = 128
height = 64
image = Image.new('1', (width, height))
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
line1 = top
line2 = top+8
line3 = top+16
line4 = top+25
line5 = top+34
line6 = top+43
line7 = top+52
brightness = 255 #Max
fichier=""
# Move left to right keeping track of the current x position for drawing shapes.
x = 0
RST = 25
CS = 8
DC = 24

#GPIO define and OLED configuration
RST_PIN        = 25 #waveshare settings
CS_PIN         = 8  #waveshare settings
DC_PIN         = 24 #waveshare settings
KEY_UP_PIN     = 6  #stick up
KEY_DOWN_PIN   = 19 #stick down
KEY_LEFT_PIN   = 5 #5  #sitck left // go back
KEY_RIGHT_PIN  = 26 #stick right // go in // validate
KEY_PRESS_PIN  = 13 #stick center button
KEY1_PIN       = 21 #key 1 // up
KEY2_PIN       = 20  #20 #key 2 // cancel/goback
KEY3_PIN       = 16 #key 3 // down
USER_I2C = 0        #set to 1 if your oled is I2C or  0 if use SPI interface
#init GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(KEY_UP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Input with pull-up
GPIO.setup(KEY_DOWN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_LEFT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_RIGHT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY_PRESS_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
screensaver = 0
#SPI
#serial = spi(device=0, port=0, bus_speed_hz = 8000000, transfer_size = 4096, gpio_DC = 24, gpio_RST = 25)
if SCNTYPE == 1:
    if  USER_I2C == 1:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RST,GPIO.OUT)
        GPIO.output(RST,GPIO.HIGH)
        serial = i2c(port=1, address=0x3c)
    else:
        serial = spi(device=0, port=0, bus_speed_hz = 8000000, transfer_size = 4096, gpio_DC = 24, gpio_RST = 25)
if SCNTYPE == 1:
    device = sh1106(serial, rotate=2) #sh1106
def DisplayText(l1,l2,l3,l4,l5,l6,l7):
    # simple routine to display 7 lines of text
    if SCNTYPE == 1:
        with canvas(device) as draw:
            draw.text((0, line1), l1,  font=font, fill=255)
            draw.text((0, line2), l2, font=font, fill=255)
            draw.text((0, line3), l3,  font=font, fill=255)
            draw.text((0, line4), l4,  font=font, fill=255)
            draw.text((0, line5), l5, font=font, fill=255)
            draw.text((0, line6), l6, font=font, fill=255)
            draw.text((0, line7), l7, font=font, fill=255)
    if SCNTYPE == 2:
            os.system('clear')
            print(l1)
            print(l2)
            print(l3)
            print(l4)
            print(l5)
            print(l6)
            print(l7)
def shell(cmd):
    return(subprocess.check_output(cmd, shell = True ))
def switch_menu(argument):
    switcher = {
    0: "_  FLASHER",
        1: "_FASTBOOT COMMANDS",
        2: "_ADB COMMANDS",
        3: "_FLASH OS",
        4: "_TRIGGERS FEATURES",
        5: "_TEMPLATES FEATURES",
        6: "_INFOSEC TOOLS",
        7: "_BOOT TWRP",
        8: "_EPIC",
        9: "_HOST OS detection",
        10: "_Display OFF",
        11: "_Keys Test",
        12: "_Reboot GUI",
        13: "_System shutdown",
        14: "_RUN HID script",
        15: "_GAMEPAD",
        16: "_MOUSE",
        17: "_Set Typing Speed",
        18: "_Set Key layout",
        19: "_",
        20: "_",
        21: "_Scan WIFI AP",
        22: "_",
        23: "_",
        24: "_",
        25: "_",
        26: "_",
        27: "_",
        28: "_Send to oled group",
        29: "_",
        30: "_",
        31: "_",
        32: "_",
        33: "_",
        34: "_",
        35: "_FULL SETTINGS",
        36: "_BLUETOOTH",
        37: "_USB",
        38: "_WIFI",
        39: "_TRIGGER ACTIONS",
        40: "_NETWORK",
        41: "_",
        42: "_Inject Rshell(ADMIN)",
        43: "_Inject Rshell (USER)",
        44: "_Revesreshell Exploit",
        45: "_",
        46: "_",
        47: "_",
        48: "_"
}
    return switcher.get(argument, "Invalid")
def OLEDContrast(contrast):
    #set contrast 0 to 255
    if SCNTYPE == 1:
        while GPIO.input(KEY_LEFT_PIN):
            #loop until press left to quit
            with canvas(device) as draw:
                if GPIO.input(KEY_UP_PIN): # button is released
                        draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0)  #Up
                else: # button is pressed:
                        draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=1)  #Up filled
                        contrast = contrast +5
                        if contrast>255:
                            contrast = 255

                if GPIO.input(KEY_DOWN_PIN): # button is released
                        draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=0) #down
                else: # button is pressed:
                        draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=1) #down filled
                        contrast = contrast-5
                        if contrast<0:
                            contrast = 0
                device.contrast(contrast)
                draw.text((54, line4), "Value : " + str(contrast),  font=font, fill=255)
    return(contrast)
def splash():
    img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'images', 'bootwhat.bmp'))
    splash = Image.open(img_path) \
        .transform((device.width, device.height), Image.AFFINE, (1, 0, 0, 0, 1, 0), Image.BILINEAR) \
        .convert(device.mode)
    device.display(splash)
    time.sleep(5) #5 sec splash boot screen
def SreenOFF():
    #put screen off until press left
    if SCNTYPE == 1:
        while GPIO.input(KEY_LEFT_PIN):
            device.hide()
            time.sleep(0.1)
        device.show()

def BootTWRP():
    shell("fastboot boot twrp.img")


def KeyTest():
    if SCNTYPE == 1:
        while GPIO.input(KEY_LEFT_PIN):
            with canvas(device) as draw:
                if GPIO.input(KEY_UP_PIN): # button is released
                        draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0)  #Up
                else: # button is pressed:
                        draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=1)  #Up filled

                if GPIO.input(KEY_LEFT_PIN): # button is released
                        draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=0)  #left
                else: # button is pressed:
                        draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=1)  #left filled

                if GPIO.input(KEY_RIGHT_PIN): # button is released
                        draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=0) #right
                else: # button is pressed:
                        draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=1) #right filled

                if GPIO.input(KEY_DOWN_PIN): # button is released
                        draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=0) #down
                else: # button is pressed:
                        draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=1) #down filled

                if GPIO.input(KEY_PRESS_PIN): # button is released
                        draw.rectangle((20, 22,40,40), outline=255, fill=0) #center 
                else: # button is pressed:
                        draw.rectangle((20, 22,40,40), outline=255, fill=1) #center filled

                if GPIO.input(KEY1_PIN): # button is released
                        draw.ellipse((70,0,90,20), outline=255, fill=0) #A button
                else: # button is pressed:
                        draw.ellipse((70,0,90,20), outline=255, fill=1) #A button filled

                if GPIO.input(KEY2_PIN): # button is released
                        draw.ellipse((100,20,120,40), outline=255, fill=0) #B button
                else: # button is pressed:
                        draw.ellipse((100,20,120,40), outline=255, fill=1) #B button filled
                        
                if GPIO.input(KEY3_PIN): # button is released
                        draw.ellipse((70,40,90,60), outline=255, fill=0) #A button
                else: # button is pressed:
                        draw.ellipse((70,40,90,60), outline=255, fill=1) #A button filled

#init vars 
curseur = 1
page=0  
menu = 1
ligne = ["","","","","","","",""]
selection = 0
if SCNTYPE == 1:
    splash()  # display boot splash image ---------------------------------------------------------------------
    #print("selected : " + FileSelect(hidpath,".js"))
    device.contrast(2)
while 1:
    if GPIO.input(KEY_UP_PIN): # button is released
        menu = 1
    else: # button is pressed:
        curseur = curseur -1
        if curseur<1:
            curseur = 7     
    if GPIO.input(KEY_LEFT_PIN): # button is released
        menu = 1
    else: # button is pressed:
                # back to main menu on Page 0
        page = 0    
    if GPIO.input(KEY_RIGHT_PIN): # button is released
        menu = 1
    else: # button is pressed:
        selection = 1
    if GPIO.input(KEY_DOWN_PIN): # button is released
        menu = 1
    else: # button is pressed:
        curseur = curseur + 1
        if curseur>7:
            curseur = 1
    #-----------
    if selection == 1:

            # Fastboot menu
            if page == 7:

                #Fastboot Boot TWRP
                if curseur == 1:
                    BootTWRP()

                if curseur == 2:
                    brightness = OLEDContrast(brightness)
                if curseur == 3:
                    #os detection
                    Osdetection()
                if curseur == 4:
                    SreenOFF()
                if curseur == 5:
                    KeyTest()
                if curseur == 6:
                    restart()
                if curseur == 7:
                    exit()
            if page == 14:
                #HID related menu
                if curseur == 1:
                    #run hid script
                    runhid()
                if curseur == 2:
                    #gamepad
                    Gamepad()
                if curseur == 3:
                    #mouse
                    Mouse()
                if curseur == 4:
                    #Set typing speed
                    SetTypingSpeed()
            if page == 21:
                if curseur == 1:
                    #SSID LIST
                    scanwifi()
            if page == 28:
                    #trigger section
                if curseur == 1:
                    trigger1()
            if page == 35:
                #template section menu
                if curseur == 1:
                    #FULL_SETTINGS
                    template = templateSelect("FULL_SETTINGS")
                    if template!="":
                        ApplyTemplate(template,"f")
                if curseur == 2:
                    #BLUETOOTH
                    template = templateSelect("BLUETOOTH")
                    if template!="":
                        ApplyTemplate(template,"b")
                if curseur == 3:
                    #USB
                    template = templateSelect("USB")
                    print(template)
                    if template!="":
                        ApplyTemplate(template,"u")
                if curseur == 4:
                    #WIFI
                    template = templateSelect("WIFI")
                    if template!="":
                        ApplyTemplate(template,"w")
                if curseur == 5:
                    #TRIGGER_ACTIONS
                    template = templateSelect("TRIGGER_ACTIONS")
                    if template!="":
                        ApplyTemplate(template,"t")
                if curseur == 6:
                    #NETWORK
                    template = templateSelect("NETWORK")
                    if template!="":
                        ApplyTemplate(template,"n")
            if page == 42:
                #infosec commands
                if curseur == 1:
                    # reverseshell injection
                    answer = 0
                    while answer == 0:
                        DisplayText(
                            "                 YES",
                            "",
                            "INJECT REVERSESHELL",
                            "TO CONNECTED HOST",
                            "ARE YOU SURE ?",
                            "",
                            "                  NO"
                            )
                        if GPIO.input(KEY1_PIN): # button is released
                            menu = 1
                        else: # button is pressed:
                            answer = 1
                        if GPIO.input(KEY3_PIN): # button is released
                            menu = 1
                        else: # button is pressed:
                            answer = 2
                    if answer == 1:
                        shell("P4wnP1_cli hid job 'gui inject revshell.js'")
                if curseur == 3:
                    # reverseshell exploitation
                    answer = 0
                    while answer == 0:
                        DisplayText(
                            "                 YES",
                            "",
                            "EXPLOIT REVERSESHELL",
                            " ON CONNECTED HOST",
                            "  ARE YOU SURE ?",
                            "",
                            "                  NO"
                            )
                        if GPIO.input(KEY1_PIN): # button is released
                            menu = 1
                        else: # button is pressed:
                            answer = 1
                        if GPIO.input(KEY3_PIN): # button is released
                            menu = 1
                        else: # button is pressed:
                            answer = 2
                    if answer == 1:
                        main()
                if curseur == 2:
                    # reverseshell injection user
                    answer = 0
                    while answer == 0:
                        DisplayText(
                            "                 YES",
                            "",
                            "INJECT REVERSESHELL",
                            "TO CONNECTED HOST",
                            "ARE YOU SURE ?",
                            "",
                            "                  NO"
                            )
                        if GPIO.input(KEY1_PIN): # button is released
                            menu = 1
                        else: # button is pressed:
                            answer = 1
                        if GPIO.input(KEY3_PIN): # button is released
                            menu = 1
                        else: # button is pressed:
                            answer = 2
                    if answer == 1:
                        shell("P4wnP1_cli hid job 'gui inject revshell user.js'")                    
            if page == 0:
            #we are in main menu
                if curseur == 1:
                    # call about
                    about()
                if curseur == 2:
                    #system menu 
                    page = 7
                    curseur = 1
                if curseur == 3:
                #hid attacks menu
                    page = 14
                    curseur = 1
                if curseur == 4:
                    page = 21
                    curseur = 1
                if curseur == 5:
                    page = 28
                    curseur = 1
                if curseur == 6:
                    page = 35
                    curseur = 1
                if curseur == 7:
                    page = 42
                    curseur = 1
                print(page+curseur)
    ligne[1]=switch_menu(page)
    ligne[2]=switch_menu(page+1)
    ligne[3]=switch_menu(page+2)
    ligne[4]=switch_menu(page+3)
    ligne[5]=switch_menu(page+4)
    ligne[6]=switch_menu(page+5)
    ligne[7]=switch_menu(page+6)
    #add curser on front on current selected line
    for n in range(1,8):
        if page+curseur == page+n:
            if page == 1:
                if readCapacity(bus) < 16:
                    ligne[n] = ligne[n].replace("_","!")
                else:
                    ligne[n] = ligne[n].replace("_",">")
            else:
                ligne[n] = ligne[n].replace("_",">")
        else:
            ligne[n] = ligne[n].replace("_"," ")
    DisplayText(ligne[1],ligne[2],ligne[3],ligne[4],ligne[5],ligne[6],ligne[7])
    #print(page+curseur) #debug trace menu value
    time.sleep(0.1)
    selection = 0
GPIO.cleanup()