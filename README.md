# VEML7700 Ambient Light Sensor Module for Viam

This is a Viam module for the VEML7700 ambient light sensor on Raspberry Pi. The VEML7700 is a high-accuracy ambient light sensor with I2C interface.

## Features

- Reads ambient light levels in lux
- I2C interface (default bus 1)
- Automatic sensor initialization
- Error handling and reporting

## Configuration

Add the sensor to your robot configuration:

```json
{
  "name": "light-sensor",
  "model": "wootter:veml7700-sensor:linux",
  "type": "sensor",
  "namespace": "rdk",
  "attributes": {
    "bus_number": 1
  }
}
```

### Attributes

- `bus_number` (optional): I2C bus number (default: 1)

## Hardware Setup

1. Connect the VEML7700 sensor to your Raspberry Pi:
   - VCC → 3.3V
   - GND → Ground
   - SDA → GPIO 2 (SDA)
   - SCL → GPIO 3 (SCL)

2. Enable I2C on your Raspberry Pi:
   ```bash
   sudo raspi-config
   # Navigate to: Interface Options → I2C → Enable
   ```

## Readings

The sensor returns the following readings:

```json
{
  "lux": 234.5,
  "bus_number": 1
}
```

## Building

To build the module:

```bash
make module.tar.gz
```

## License

Apache-2.0
