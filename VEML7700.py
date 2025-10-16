# this program reads sensor VEML6030 and correct non linearity values above 1000 lux
# original code based on veml7700 example of Joe Robidoux.

import smbus
import time

bus = smbus.SMBus(1)

addr = 0x10

#Write registers
als_conf_0 = 0x00
als_WH = 0x01
als_WL = 0x02
pow_sav = 0x03

#Read registers
als = 0x04
white = 0x05
interrupt = 0x06

confValues = [0x00, 0x18] 
interrupt_high = [0x00, 0x00]
interrupt_low = [0x00, 0x00]
power_save_mode = [0x00, 0x00]

bus.write_i2c_block_data(addr, als_conf_0, confValues)
bus.write_i2c_block_data(addr, als_WH, interrupt_high)
bus.write_i2c_block_data(addr, als_WL, interrupt_low)
bus.write_i2c_block_data(addr, pow_sav, power_save_mode)

while True:
    time.sleep(.04) 

    word = bus.read_word_data(addr,als)
    gain = 0.2304

    val = word * gain
    val = round(val,1) #Round value for presentation

    print ("Measures: " + str(val) + " Lux")