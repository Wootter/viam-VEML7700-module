"""
This file registers the model with the Python SDK.
"""

from viam.components.sensor import Sensor
from viam.resource.registry import Registry, ResourceCreatorRegistration

from .veml7700 import VEML7700

Registry.register_resource_creator(Sensor.API, VEML7700.MODEL, ResourceCreatorRegistration(VEML7700.new, VEML7700.validate))
