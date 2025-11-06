from typing import ClassVar, Mapping, Any, Optional
from typing_extensions import Self

from viam.module.types import Reconfigurable
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.types import Model, ModelFamily

from viam.components.sensor import Sensor
from viam.logging import getLogger
import asyncio
import time
import smbus2 as smbus

LOGGER = getLogger(__name__)


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


class VEML7700Sensor:
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


class VEML7700(Sensor, Reconfigurable):
    """
    VEML7700 represents a light sensor that measures ambient light in lux.
    """
    
    MODEL: ClassVar[Model] = Model(ModelFamily("wootter", "sensor"), "veml7700")
    
    def __init__(self, name: str):
        super().__init__(name)
        self.sensor = None
        self.bus_number = 1
        LOGGER.info(f"{self.__class__.__name__} initialized.")

    @classmethod
    def new(cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> Self:
        instance = cls(config.name)
        instance.reconfigure(config, dependencies)
        return instance

    @classmethod
    def validate(cls, config: ComponentConfig):
        # Bus number is optional, defaults to 1
        return ([], [])

    def reconfigure(self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]):
        # Optional: allow custom I2C bus number
        if "bus" in config.attributes.fields:
            self.bus_number = int(config.attributes.fields["bus"].number_value)
        
        # Initialize sensor
        self.sensor = VEML7700Sensor(self.bus_number)
        try:
            self.sensor.initialize()
            LOGGER.info(f"VEML7700 sensor initialized on I2C bus {self.bus_number}")
        except Exception as e:
            LOGGER.error(f"Failed to initialize VEML7700: {e}")
            raise

    async def get_readings(self, extra: Optional[Mapping[str, Any]] = None, **kwargs) -> Mapping[str, Any]:
        """
        Obtain the measurements from the VEML7700 sensor.
        
        Returns:
            Mapping[str, Any]: Light level readings in lux.
        """
        # Retry logic: VEML7700 sensors may need multiple attempts
        max_retries = 3
        retry_delay = 0.1  # 100ms between retries
        
        for attempt in range(max_retries):
            result = await asyncio.to_thread(self.sensor.read)

            if result.is_valid():
                lux = result.lux
                
                LOGGER.info(f"Light level: {lux} lux (attempt {attempt + 1})")
                
                return {
                    "lux": lux,
                    "light_level": lux
                }
            else:
                error_messages = {
                    VEML7700Result.ERR_NOT_FOUND: "VEML7700 sensor not found on I2C bus",
                    VEML7700Result.ERR_READ_ERROR: "Error reading from VEML7700 sensor"
                }
                error_msg = error_messages.get(result.error_code, "Unknown error")
                
                if attempt < max_retries - 1:
                    LOGGER.warning(f"VEML7700 error on attempt {attempt + 1}/{max_retries}: {error_msg}. Retrying...")
                    await asyncio.sleep(retry_delay)
                else:
                    LOGGER.error(f"VEML7700 error after {max_retries} attempts: {error_msg}")
                    return {
                        "error": error_msg,
                        "error_code": result.error_code
                    }

    async def close(self):
        """
        Clean up resources when the module is shut down.
        """
        if self.sensor:
            await asyncio.to_thread(self.sensor.cleanup)
            LOGGER.info("VEML7700 sensor closed")
