"""
Sensor modules for Gas Leakage Detection System
Simulates hardware sensors: MQ-2 Gas, Temperature, and Smoke sensors
"""

import random
import time
from abc import ABC, abstractmethod

class BaseSensor(ABC):
    def __init__(self, name, pin):
        self.name = name
        self.pin = pin
        self.baseline = 0
        self.current_value = 0
        self.is_calibrated = False
        
    @abstractmethod
    def read_raw(self):
        pass
    
    def read(self):
        self.current_value = self.read_raw()
        return self.current_value
    
    def calibrate(self, samples=10):
        readings = []
        for _ in range(samples):
            readings.append(self.read_raw())
            time.sleep(0.1)
        self.baseline = sum(readings) / len(readings)
        self.is_calibrated = True
        return self.baseline
    
    def get_status(self):
        return {
            'name': self.name,
            'pin': self.pin,
            'value': self.current_value,
            'baseline': self.baseline,
            'is_calibrated': self.is_calibrated
        }


class GasSensor(BaseSensor):
    """
    MQ-2/MQ-5 Gas Sensor Module
    Detects LPG, propane, hydrogen, methane, and smoke
    """
    def __init__(self, pin=0, sensor_type='MQ-2'):
        super().__init__(f'{sensor_type} Gas Sensor', pin)
        self.sensor_type = sensor_type
        self.gas_type = 'LPG'
        self.last_reading = time.time()
        self.manual_level = None
        
    def read_raw(self):
        if self.manual_level is not None:
            self.last_reading = time.time()
            return self.manual_level
            
        elapsed = time.time() - self.last_reading
        if elapsed < 0.5:
            return self.current_value
            
        base_value = 50
        noise = random.gauss(0, 10)
        drift = random.choice([-1, 0, 1]) * random.uniform(0, 2)
        
        value = max(0, min(1023, base_value + noise + drift))
        self.current_value = int(value)
        self.last_reading = time.time()
        return self.current_value
    
    def set_gas_level(self, level):
        """Set simulated gas level for testing (0-100)"""
        self.manual_level = int(level * 10.23)
        self.current_value = self.manual_level
        return self.manual_level
    
    def reset_manual_level(self):
        """Reset to auto simulation mode"""
        self.manual_level = None
    
    def detect_gas_type(self):
        """Simulate gas type detection"""
        types = ['LPG', 'Methane', 'Propane', 'Hydrogen', 'Smoke']
        return random.choice(types)


class TemperatureSensor(BaseSensor):
    """
    DHT11/DHT22 Temperature and Humidity Sensor
    """
    def __init__(self, pin=1):
        super().__init__('DHT11 Temperature Sensor', pin)
        self.unit = 'Celsius'
        self.last_temp = 25.0
        
    def read_raw(self):
        variation = random.gauss(0, 0.5)
        self.last_temp = max(-40, min(80, 25 + variation))
        return round(self.last_temp, 1)
    
    def read_temperature(self):
        return self.read_raw()
    
    def read_humidity(self):
        base_humidity = 60
        variation = random.gauss(0, 5)
        return max(0, min(100, base_humidity + variation))


class SmokeSensor(BaseSensor):
    """
    Smoke Detection Sensor
    Works alongside gas sensor for comprehensive safety
    """
    def __init__(self, pin=2):
        super().__init__('Smoke Sensor', pin)
        
    def read_raw(self):
        base_value = 30
        noise = random.gauss(0, 5)
        value = max(0, min(1023, base_value + noise))
        self.current_value = int(value)
        return self.current_value
    
    def set_smoke_level(self, level):
        """Set simulated smoke level for testing (0-100)"""
        self.current_value = int(level * 10.23)
        return self.current_value


class SensorArray:
    """
    Manages all sensors in the detection system
    """
    def __init__(self):
        self.gas_sensor = GasSensor(pin=0, sensor_type='MQ-2')
        self.temp_sensor = TemperatureSensor(pin=1)
        self.smoke_sensor = SmokeSensor(pin=2)
        self.sensors = [self.gas_sensor, self.temp_sensor, self.smoke_sensor]
        
    def calibrate_all(self):
        results = {}
        for sensor in self.sensors:
            baseline = sensor.calibrate()
            results[sensor.name] = baseline
        return results
    
    def read_all(self):
        readings = {
            'gas': self.gas_sensor.read(),
            'temperature': self.temp_sensor.read_temperature(),
            'humidity': self.temp_sensor.read_humidity(),
            'smoke': self.smoke_sensor.read()
        }
        return readings
    
    def get_all_status(self):
        return [sensor.get_status() for sensor in self.sensors]
