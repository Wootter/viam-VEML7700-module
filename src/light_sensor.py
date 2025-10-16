import asyncio
from typing import Any, ClassVar, Dict, Mapping, Optional
from viam.components.sensor import Sensor
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.types import Model, ModelFamily
from .veml7700 import VEML7700, VEML7700Result


class MySensor(Sensor):
    """
    VEML7700 Ambient Light Sensor for Raspberry Pi
    This sensor module reads ambient light data from a VEML7700 sensor
    connected via I2C bus.
    """
    
    # Define the model of the sensor
    MODEL: ClassVar[Model] = Model(ModelFamily("wootter", "veml7700-sensor"), "linux")

    def __init__(self, name: str, bus_number: int = 1):
        """
        Initialize the VEML7700 sensor with the name and I2C bus number.
        
        Args:
            name: The name of the sensor component
            bus_number: The I2C bus number (default 1 for Raspberry Pi)
        """
        super().__init__(name)
        self.bus_number = bus_number
        # Create VEML7700 sensor instance
        self.sensor = VEML7700(bus_number)
        # Initialize the sensor
        try:
            self.sensor.initialize()
        except Exception as e:
            print(f"Warning: Failed to initialize VEML7700 sensor: {e}")

    @classmethod
    def new(cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> "MySensor":
        """
        Create a new instance of the sensor using the configuration.
        
        Args:
            config: Component configuration containing the I2C bus number (optional)
            dependencies: Component dependencies (not used for this sensor)
            
        Returns:
            A new MySensor instance
        """
        # Extract the bus number from the configuration attributes (optional, defaults to 1)
        bus_number = 1  # Default I2C bus for Raspberry Pi
        
        if "bus_number" in config.attributes.fields:
            bus_number = int(config.attributes.fields["bus_number"].number_value)
        
        sensor = cls(config.name, bus_number)
        return sensor

    async def get_readings(self, extra: Optional[Dict[str, Any]] = None, **kwargs) -> Mapping[str, Any]:
        """
        Read the ambient light level from the VEML7700 sensor.
        
        Args:
            extra: Optional extra parameters
            **kwargs: Additional keyword arguments
            
        Returns:
            A dictionary containing lux value,
            or an error message if reading fails
        """
        # Read from the VEML7700 sensor
        result = self.sensor.read()
        
        if result.is_valid():
            lux = result.lux
            return {
                "lux": round(lux, 1),
                "bus_number": self.bus_number
            }
        else:
            error_messages = {
                VEML7700Result.ERR_NOT_FOUND: "VEML7700 sensor not found on I2C bus",
                VEML7700Result.ERR_READ_ERROR: "Error reading from VEML7700 sensor"
            }
            error_msg = error_messages.get(result.error_code, "Unknown error from VEML7700 sensor")
            return {
                "error": error_msg,
                "error_code": result.error_code,
                "bus_number": self.bus_number
            }


async def main():
    """
    Test function to verify sensor readings.
    This will be called when the module is run standalone.
    """
    # Create a new sensor object and get readings (using I2C bus 1 as default)
    my_sensor = MySensor(name="veml7700_sensor", bus_number=1)
    readings = await my_sensor.get_readings()
    print("VEML7700 Sensor Readings:")
    print(readings)


# Run the main function when the script is executed directly
if __name__ == '__main__':
    asyncio.run(main())
