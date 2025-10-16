import smbus2 as smbus
import time


class VEML7700Result:
    """Result object for VEML7700 readings"""
    ERR_NO_ERROR = 0
    ERR_NOT_FOUND = 1
    ERR_READ_ERROR = 2

    def __init__(self, error_code, lux):
        self.error_code = error_code
        self.lux = lux

    def is_valid(self):
        return self.error_code == VEML7700Result.ERR_NO_ERROR


class VEML7700:
    """
    VEML7700 Light Sensor Driver
    This sensor reads ambient light levels using the VEML7700 sensor via I2C.
    """
    
    # I2C address
    ADDR = 0x10
    
    # Write registers
    ALS_CONF_0 = 0x00
    ALS_WH = 0x01
    ALS_WL = 0x02
    POW_SAV = 0x03
    
    # Read registers
    ALS = 0x04
    WHITE = 0x05
    INTERRUPT = 0x06
    
    def __init__(self, bus_number=1):
        """
        Initialize the VEML7700 sensor
        
        Args:
            bus_number: I2C bus number (default 1 for Raspberry Pi)
        """
        self.bus_number = bus_number
        self.bus = None
        self.gain = 0.2304  # Default gain value
        
    def initialize(self):
        """Initialize the I2C bus and configure the sensor"""
        try:
            self.bus = smbus.SMBus(self.bus_number)
            
            # Configuration values
            conf_values = [0x00, 0x18]
            interrupt_high = [0x00, 0x00]
            interrupt_low = [0x00, 0x00]
            power_save_mode = [0x00, 0x00]
            
            # Write configuration to sensor
            self.bus.write_i2c_block_data(self.ADDR, self.ALS_CONF_0, conf_values)
            self.bus.write_i2c_block_data(self.ADDR, self.ALS_WH, interrupt_high)
            self.bus.write_i2c_block_data(self.ADDR, self.ALS_WL, interrupt_low)
            self.bus.write_i2c_block_data(self.ADDR, self.POW_SAV, power_save_mode)
            
            # Wait for sensor to stabilize
            time.sleep(0.04)
            
        except Exception as e:
            raise Exception(f"Failed to initialize VEML7700 sensor: {e}")
    
    def read(self):
        """
        Read the ambient light level from the sensor
        
        Returns:
            VEML7700Result object containing the lux value or error code
        """
        try:
            if self.bus is None:
                self.initialize()
            
            # Wait for measurement to be ready
            time.sleep(0.04)
            
            # Read word data from ALS register
            word = self.bus.read_word_data(self.ADDR, self.ALS)
            
            # Calculate lux value
            val = word * self.gain
            val = round(val, 1)
            
            return VEML7700Result(VEML7700Result.ERR_NO_ERROR, val)
            
        except OSError as e:
            # Sensor not found or connection issue
            return VEML7700Result(VEML7700Result.ERR_NOT_FOUND, 0)
        except Exception as e:
            # Other read errors
            return VEML7700Result(VEML7700Result.ERR_READ_ERROR, 0)
    
    def cleanup(self):
        """Clean up resources"""
        if self.bus is not None:
            try:
                self.bus.close()
            except:
                pass
