#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import time
import math
import smbus
from periphery import GPIO

I2C_ADDR = 0x5B

# set pin
RST_PIN = 146   #GPIO4_C2_d

P0_INPUT	=	0x00
P1_INPUT	=	0x01
P0_OUTPUT	=	0x02
P1_OUTPUT	=	0x03
P0_CONFIG	=	0x04
P1_CONFIG	=	0x05
P0_INT		=	0x06
P1_INT		=	0x07
ID_REG		=	0x10
CTL_REG		=	0x11
P0_LED_MODE	=	0x12
P1_LED_MODE	=	0x13
P1_0_DIM0	=	0x20
P1_1_DIM0	=	0x21
P1_2_DIM0	=	0x22
P1_3_DIM0	=	0x23
P0_0_DIM0	=	0x24
P0_1_DIM0	=	0x25
P0_2_DIM0	=	0x26
P0_3_DIM0	=	0x27
P0_4_DIM0	=	0x28
P0_5_DIM0	=	0x29
P0_6_DIM0	=	0x2A
P0_7_DIM0	=	0x2B
P1_4_DIM0	=	0x2C
P1_5_DIM0	=	0x2D
P1_6_DIM0	=	0x2E
P1_7_DIM0	=	0x2F
SW_RSTN		=	0x7F

AW9523B_ID_REG = 0x10
AW9523B_ID_VALUE = 0x23

"""
i2cset -y 2 0x5b 0x12 00
i2cset -y 2 0x5b 0x13 00
"""
class AW9523B:
    def __init__(self, address=I2C_ADDR, debug=0):
        try:
            self.i2c = smbus.SMBus(2)
        except:
            print("open i2c bus failed")
            return

        self.address = address
        
        self.debug = debug
        
        #self.gpioInt = GPIO(INI_PIN, "in")
        self.gpioRst = GPIO(RST_PIN, "out")

        self.gpioRst.write(False)
        time.sleep(1)
        self.gpioRst.write(True)

    def AW9523BCheck(self):
        data = self.ReadByte(AW9523B_ID_REG)
        if data is not None and AW9523B_ID_VALUE == data:
            return True
        return False

    def setting_ctl(self):
        #ouput
        self.PortMode(0, 0)
        self.PortMode(1, 0)
        self.PortCtrl(1, 0) 
        #Led MODE
        self.LEDModeSwitch(0, 0)
        self.LEDModeSwitch(1, 0)
        
    def ReadByte(self, Addr):
        data = None
        try:
            data = self.i2c.read_byte_data(self.address, Addr)
        except OSError:
            print("i2c read bytes error, failed", hex(Addr))
        finally:
            return data

    def WriteByte(self, Addr, val):
        try:
            self.i2c.write_byte_data(self.address, Addr, val & 0xFF)
        except IOError:
            print("i2c write error, failed", hex(Addr))
            
    def PortInput(self, port):#port:00h 01H
        if(self.debug == 1):
            print("input port%d val = 0x%x"%(port, self.ReadByte(P0_INPUT if port==0 else P1_INPUT)))
        return self.ReadByte(P0_INPUT if port==0 else P1_INPUT)
    
    def PortOutput(self, port, val):#port:02H 03H , mode:0-Llev 0xff-Hlev
        if(self.debug == 1):
            print("output port%d val = 0x%x"%(port, val))		
        self.WriteByte(P0_OUTPUT if port==0 else P1_OUTPUT, val)

    #port 8pin
    def PortMode(self, port, mode):#port:04H 05H , mode:0-out 1-in
        if(self.debug == 1):
            print("set port%d mode = %s"%(port, "out" if mode==0 else "in"))
        self.WriteByte(P0_CONFIG if port==0 else P1_CONFIG, 0 if mode==0 else 0xff)

    def PortInt(self, port, en):#port:06h 07h, en:0-enable 1-uenable,Int Port
        if(self.debug == 1):
            print("enable port%d int = 0x%x"%(port, en))
        self.WriteByte(P0_INT if port==0 else P1_INT, en)

    def PortIntClear(self, port):#port:06h 07h, en:0-enable 1-uenable
        if(self.debug == 1):
            print("clear port%d int" %port)
        self.ReadByte(P0_INT if port==0 else P1_INT)

    def PinMode(self, port, pin, mode):#port:04H 05H , mode:0-out 1-in
        self.WriteByte(P0_CONFIG if port==0 else P1_CONFIG, mode<<pin)

    def PinInput(self, port, pin):#port:00h 01H
        return self.ReadByte(P0_INPUT if port==0 else P1_INPUT)&(1<<pin)
 
    def PinOutput(self, port, pin, val):#port:02H 03H , mode:0-Llev 0-Hlev
        self.WriteByte(P0_OUTPUT if port==0 else P1_OUTPUT, val<<pin)

    def PinInt(self, port, pin, en):#port:06h 07h, en:0-enable 1-uenable
        self.WriteByte(P0_INT if port==0 else P1_INT, en<<pin)
        
    #gpomd=D[4]:0-Open-Drain 1-Push-Pull; just p0
    #iseld[1:0]:00-11(IMAX×1/4,IMAX×2/4, IMAX×3/4,IMAX)
    def PortCtrl(self,  gpomd, isel):
        g = gpomd << 4
        s = isel << 2
        val = g | s
        self.WriteByte(CTL_REG, val)#AW9523B_REG_GLOB_CTR
        
    def LEDModeSwitch(self, port, mode):# PORT 12H 13H, MODE:0(led) 1(gpio)
        self.WriteByte(P0_LED_MODE if port==0 else P1_LED_MODE, 0 if mode==0 else 0xff)

    def LEDDims(self, lednum, i):# lednum:0x20->0x2F, i: i/255×IMAX, IMAX= 37Ma
        self.WriteByte(lednum, i)
    
    def SystemReset(self):# Software Reset
        self.WriteByte(SW_RSTN, 0x00)

class LedGPIO():
    def __init__(self, gpio_R, gpio_G, gpio_B):
        """
        led 5:
        GPIO2_C2_d 82 IO_R1
        GPIO2_A7_u 71 IO_G1
        GPIO2_B0_d 72 IO_B1

        led 6:
        GPIO2_C3_d   83 IO_R2
        GPIO2_C4_d   84 IO_G2
        SPI1_MOSI_M0 79 IO_B2

        led 7:
        SPI1_MISO_M0 78 IO_R3
        GPIO2_C5_d   85 IO_G3
        SPI1_CLK_M0  77 IO_B3

        led 8:
        SPI1_CS0_M0  80 IO_R4
        SPI1_CS1_M0  86 IO_G4
        GPIO2_B2_d   74 IO_B4
        eof
        """
        self.gpioR = GPIO(gpio_R, "out")
        self.gpioG = GPIO(gpio_G, "out")
        self.gpioB = GPIO(gpio_B, "out")
        self.gpioR.write(True)
        self.gpioG.write(True)
        self.gpioB.write(True)
        
    def LEDctl(self,R,G,B):
        self.gpioR.write(False if R != 0 else True)
        self.gpioG.write(False if G != 0 else True)
        self.gpioB.write(False if B != 0 else True)
    
    def LEDon(self,R=255,G=255,B=255):
        self.LEDctl(R,G,B)

    def LEDoff(self,R=0,G=0,B=0):
        self.LEDctl(R,G,B)

class Led():
    def __init__(self):
        self.sensor = AW9523B()
        self.check_flag = self.sensor.AW9523BCheck()
        if self.check_flag:
            self.sensor.setting_ctl()
        
        self.led5 = LedGPIO(82, 71, 72)
        self.led6 = LedGPIO(83, 84, 79)
        self.led7 = LedGPIO(78, 85, 77)
        self.led8 = LedGPIO(80, 86, 74)
        
    def set_led_rgb(self, index, r, g, b):
        if index <= 3 and self.check_flag == False:
            return
 
        if index == 0:
            self.sensor.LEDDims(P1_0_DIM0, r)
            self.sensor.LEDDims(P1_1_DIM0, g)
            self.sensor.LEDDims(P1_2_DIM0, b)
        elif index == 1:
            self.sensor.LEDDims(P1_3_DIM0, r)
            self.sensor.LEDDims(P0_0_DIM0, g)
            self.sensor.LEDDims(P0_1_DIM0, b)
        elif index == 2:
            self.sensor.LEDDims(P0_2_DIM0, r)
            self.sensor.LEDDims(P0_3_DIM0, g)
            self.sensor.LEDDims(P0_4_DIM0, b)
        elif index == 3:
            self.sensor.LEDDims(P0_5_DIM0, r)
            self.sensor.LEDDims(P0_6_DIM0, g)
            self.sensor.LEDDims(P0_7_DIM0, b)
        elif index == 4:
            self.led5.LEDctl(r, g, b)
        elif index == 5:
            self.led6.LEDctl(r, g, b)
        elif index == 6:
            self.led7.LEDctl(r, g, b)
        elif index == 7:
            self.led8.LEDctl(r, g, b)
        else:
            print("not have the LED")
 
    def fade_led(self, index, steps=256, duration=5):
        if index < 0 or index > 7:
            print("Invalid LED index")
            return
 
        for i in range(steps + 1):
            r = int(255 * i / steps)
            g = int(255 * i / steps)
            b = int(255 * i / steps)
            self.set_led_rgb(index, r, g, b)
            time.sleep(duration / steps)
 
        for i in range(steps, -1, -1):
            r = int(255 * i / steps)
            g = int(255 * i / steps)
            b = int(255 * i / steps)
            self.set_led_rgb(index, r, g, b)
            time.sleep(duration / steps)
 
if __name__ == '__main__':
    led = Led()
    
    # 逐个LED执行渐变效果
    for i in range(8):
        led.fade_led(i)
    
    """
    sensor = AW9523B()

    led5 = LedGPIO(82,71,72)
    led6 = LedGPIO(83,84,79)
    led7 = LedGPIO(78,85,77)
    led8 = LedGPIO(80,86,74)
    
    check_flag = sensor.AW9523BCheck()
    if check_flag:
        sensor.setting_ctl()
        #for LED 1, P1_0, P1_1,P1_2, r,g,b
        for x in range(0, 128, 16):
            sensor.LEDDims(0x20, x)
            time.sleep(0.5)
 
    colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,255), (0,0,0)]
    for color in colors:
        R=color[0]
        G=color[1]
        B=color[2]
        
        if check_flag:
            #for LED 1, P1_0, P1_1,P1_2, r,g,b
            sensor.LEDDims(P1_0_DIM0, R)
            sensor.LEDDims(P1_1_DIM0, G)
            sensor.LEDDims(P1_2_DIM0, B)

            #for LED 2, P1_3, P0_0,P0_1, r,g,b
            sensor.LEDDims(P1_3_DIM0, R)
            sensor.LEDDims(P0_0_DIM0, G)
            sensor.LEDDims(P0_1_DIM0, B)
            
            #for LED 3, P0_2, P0_3,P0_4, r,g,b
            sensor.LEDDims(P0_2_DIM0, R)
            sensor.LEDDims(P0_3_DIM0, G)
            sensor.LEDDims(P0_4_DIM0, B)    

            #for LED 4, P0_5, P0_6,P0_7, r,g,b
            sensor.LEDDims(P0_5_DIM0, R)
            sensor.LEDDims(P0_6_DIM0, G)
            sensor.LEDDims(P0_7_DIM0, B)
        
        led5.LEDon(R,G,B)
        led6.LEDon(R,G,B)
        led7.LEDon(R,G,B)
        led8.LEDon(R,G,B)
        
        time.sleep(0.5)
    print("Artificial judgement")
    """