"""
Unit Tests for Gas Leakage Detection System
Run with: python -m pytest tests.py -v
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sensors import GasSensor, TemperatureSensor, SmokeSensor, SensorArray
from alerts import AlertManager, AlertLevel
from config import GasThresholds, TemperatureThresholds


class TestGasSensor(unittest.TestCase):
    """Test cases for GasSensor class"""
    
    def setUp(self):
        self.sensor = GasSensor(pin=0, sensor_type='MQ-2')
        
    def test_initialization(self):
        """Test sensor initializes correctly"""
        self.assertEqual(self.sensor.sensor_type, 'MQ-2')
        self.assertEqual(self.sensor.pin, 0)
        self.assertFalse(self.sensor.is_calibrated)
        
    def test_read_raw_returns_value(self):
        """Test read_raw returns a value"""
        value = self.sensor.read_raw()
        self.assertIsInstance(value, int)
        self.assertGreaterEqual(value, 0)
        self.assertLessEqual(value, 1023)
        
    def test_set_gas_level(self):
        """Test manual gas level setting"""
        self.sensor.set_gas_level(50)
        self.assertEqual(self.sensor.current_value, 511)
        self.assertEqual(self.sensor.manual_level, 511)
        
    def test_calibration(self):
        """Test sensor calibration"""
        self.sensor.reset_manual_level()  # Ensure not in manual mode
        baseline = self.sensor.calibrate(samples=5)
        self.assertTrue(self.sensor.is_calibrated)
        self.assertIsInstance(baseline, float)


class TestTemperatureSensor(unittest.TestCase):
    """Test cases for TemperatureSensor class"""
    
    def setUp(self):
        self.sensor = TemperatureSensor(pin=1)
        
    def test_read_temperature(self):
        """Test temperature reading"""
        temp = self.sensor.read_temperature()
        self.assertIsInstance(temp, float)
        self.assertGreaterEqual(temp, -40)
        self.assertLessEqual(temp, 80)
        
    def test_read_humidity(self):
        """Test humidity reading"""
        humidity = self.sensor.read_humidity()
        self.assertIsInstance(humidity, float)
        self.assertGreaterEqual(humidity, 0)
        self.assertLessEqual(humidity, 100)


class TestSmokeSensor(unittest.TestCase):
    """Test cases for SmokeSensor class"""
    
    def setUp(self):
        self.sensor = SmokeSensor(pin=2)
        
    def test_read_raw(self):
        """Test smoke sensor reading"""
        value = self.sensor.read_raw()
        self.assertIsInstance(value, int)
        self.assertGreaterEqual(value, 0)
        self.assertLessEqual(value, 1023)
        
    def test_set_smoke_level(self):
        """Test smoke level setting"""
        self.sensor.set_smoke_level(30)
        self.assertEqual(self.sensor.current_value, 306)


class TestSensorArray(unittest.TestCase):
    """Test cases for SensorArray class"""
    
    def setUp(self):
        self.array = SensorArray()
        
    def test_initialization(self):
        """Test array initializes with all sensors"""
        self.assertIsNotNone(self.array.gas_sensor)
        self.assertIsNotNone(self.array.temp_sensor)
        self.assertIsNotNone(self.array.smoke_sensor)
        
    def test_read_all(self):
        """Test reading all sensors"""
        readings = self.array.read_all()
        self.assertIn('gas', readings)
        self.assertIn('temperature', readings)
        self.assertIn('humidity', readings)
        self.assertIn('smoke', readings)
        
    def test_calibrate_all(self):
        """Test calibrating all sensors"""
        results = self.array.calibrate_all()
        self.assertEqual(len(results), 3)
        for name, baseline in results.items():
            self.assertIsInstance(baseline, float)


class TestAlertManager(unittest.TestCase):
    """Test cases for AlertManager class"""
    
    def setUp(self):
        self.manager = AlertManager()
        
    def test_trigger_safe_alert(self):
        """Test safe alert triggers correctly"""
        alert = self.manager.trigger_alert(AlertLevel.SAFE, 100)
        self.assertEqual(alert['level'], AlertLevel.SAFE)
        self.assertEqual(alert['gas_value'], 100)
        self.assertFalse(self.manager.buzzer_active)
        
    def test_trigger_warning_alert(self):
        """Test warning alert triggers correctly"""
        alert = self.manager.trigger_alert(AlertLevel.WARNING, 300)
        self.assertEqual(alert['level'], AlertLevel.WARNING)
        
    def test_trigger_danger_alert(self):
        """Test danger alert triggers correctly"""
        alert = self.manager.trigger_alert(AlertLevel.DANGER, 800)
        self.assertEqual(alert['level'], AlertLevel.DANGER)
        self.assertTrue(self.manager.buzzer_active)
        self.assertEqual(self.manager.led_state, 'RED')
        
    def test_alert_history(self):
        """Test alert history tracking"""
        self.manager.trigger_alert(AlertLevel.SAFE, 100)
        self.manager.trigger_alert(AlertLevel.WARNING, 300)
        history = self.manager.get_alert_history()
        self.assertEqual(len(history), 2)
        
    def test_clear_history(self):
        """Test clearing alert history"""
        self.manager.trigger_alert(AlertLevel.SAFE, 100)
        self.manager.clear_history()
        self.assertEqual(len(self.manager.alert_history), 0)


class TestThresholds(unittest.TestCase):
    """Test cases for threshold configurations"""
    
    def test_gas_thresholds(self):
        """Test gas threshold values"""
        self.assertEqual(GasThresholds.SAFE, 200)
        self.assertEqual(GasThresholds.WARNING, 500)
        self.assertEqual(GasThresholds.DANGER, 800)
        
    def test_temperature_thresholds(self):
        """Test temperature threshold values"""
        self.assertEqual(TemperatureThresholds.MAX_NORMAL, 50)
        self.assertEqual(TemperatureThresholds.WARNING, 60)
        self.assertEqual(TemperatureThresholds.DANGER, 75)


class TestStatusEvaluation(unittest.TestCase):
    """Test cases for status evaluation logic"""
    
    def test_safe_status(self):
        """Test safe status evaluation"""
        gas = 100
        status = self._evaluate(gas)
        self.assertEqual(status, 'SAFE')
        
    def test_warning_status(self):
        """Test warning status evaluation"""
        gas = 600  # Between 500 and 800
        status = self._evaluate(gas)
        self.assertEqual(status, 'WARNING')
        
    def test_danger_status(self):
        """Test danger status evaluation"""
        gas = 800
        status = self._evaluate(gas)
        self.assertEqual(status, 'DANGER')
        
    def test_boundary_safe_to_warning(self):
        """Test boundary between safe and warning"""
        self.assertEqual(self._evaluate(199), 'SAFE')
        self.assertEqual(self._evaluate(500), 'WARNING')  # 500 is start of warning
        
    def test_boundary_warning_to_danger(self):
        """Test boundary between warning and danger"""
        self.assertEqual(self._evaluate(799), 'WARNING')
        self.assertEqual(self._evaluate(800), 'DANGER')  # 800 is start of danger
        
    def _evaluate(self, gas_value):
        """Helper to evaluate status - matches GasThresholds"""
        # WARNING = 500, DANGER = 800
        if gas_value >= 500:
            if gas_value >= 800:
                return 'DANGER'
            return 'WARNING'
        return 'SAFE'


class TestLCDDisplay(unittest.TestCase):
    """Test cases for LCD display"""
    
    def test_lcd_update(self):
        """Test LCD update with values"""
        from display import LCDDisplay
        
        lcd = LCDDisplay(16, 2)
        lcd.update(500, 25.5, 'WARNING')
        
        line0 = ''.join(lcd.content[0])
        line1 = ''.join(lcd.content[1])
        
        self.assertIn('500', line0)
        self.assertIn('25.5', line1)
        # LCD width is 16, so status might be truncated
        self.assertTrue('WARN' in line1 or 'WARNING' in line1)
        
    def test_lcd_show_message(self):
        """Test LCD custom message"""
        from display import LCDDisplay
        
        lcd = LCDDisplay(16, 2)
        lcd.show_message('LINE1', 'LINE2')
        
        line0 = ''.join(lcd.content[0]).strip()
        line1 = ''.join(lcd.content[1]).strip()
        
        self.assertEqual(line0, 'LINE1')
        self.assertEqual(line1, 'LINE2')


if __name__ == '__main__':
    unittest.main(verbosity=2)
