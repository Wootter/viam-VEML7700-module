from viam.components.sensor import Sensor
from viam.resource.registry import Registry, ResourceCreatorRegistration
from viam.module.module import Module
from .light_sensor import MySensor
import asyncio


# Register the sensor model with Viam
Registry.register_resource_creator(Sensor.SUBTYPE, MySensor.MODEL, ResourceCreatorRegistration(MySensor.new))


if __name__ == "__main__":
    asyncio.run(Module.run_from_registry())
