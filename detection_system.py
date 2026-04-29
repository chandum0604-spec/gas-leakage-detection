"""
Main Gas Leakage Detection System
Orchestrates all components for comprehensive gas monitoring
"""

import time
from datetime import datetime

from config import GasThresholds, TemperatureThresholds, SmokeThresholds, SystemConfig
from sensors import SensorArray
from alerts import AlertManager, AlertLevel
from display import LCDDisplay, SerialMonitor, MobileApp, ConsoleDisplay


class GasDetectionSystem:
    """
    Main detection system that coordinates all components
    Implements real-time gas leakage monitoring and alerting
    """
    
    def __init__(self, simulation_mode=True):
        self.simulation_mode = simulation_mode
        self.is_running = False
        self.start_time = None
        self.total_readings = 0
        self.total_alerts = 0
        
        self.sensors = SensorArray()
        self.alerts = AlertManager()
        self.lcd = LCDDisplay(SystemConfig.LCD_COLS, SystemConfig.LCD_ROWS)
        self.serial = SerialMonitor()
        self.mobile = MobileApp()
        
        self.current_status = 'SAFE'
        self.gas_history = []
        
    def initialize(self):
        """Initialize the detection system"""
        print("\n" + "=" * 60)
        print("  INITIALIZING GAS LEAKAGE DETECTION SYSTEM")
        print("=" * 60)
        
        print("\n[1/4] Calibrating sensors...")
        calibration = self.sensors.calibrate_all()
        for name, baseline in calibration.items():
            print(f"       {name}: Baseline = {baseline:.1f}")
            
        print("\n[2/4] Testing alert systems...")
        self._test_alerts()
        
        print("\n[3/4] Initializing display modules...")
        self.lcd.show_message("GAS DETECTOR", "System Ready")
        
        print("\n[4/4] System initialization complete!")
        print(f"       Mode: {'SIMULATION' if self.simulation_mode else 'HARDWARE'}")
        print("=" * 60 + "\n")
        
        return True
        
    def _test_alerts(self):
        """Test all alert mechanisms"""
        test_alert = self.alerts.trigger_alert(AlertLevel.SAFE, 100)
        print("       Alert system: OK")
        
    def start(self):
        """Start the detection system"""
        self.is_running = True
        self.start_time = time.time()
        print("\n>> SYSTEM STARTED - Monitoring active\n")
        
    def stop(self):
        """Stop the detection system"""
        self.is_running = False
        elapsed = time.time() - self.start_time if self.start_time else 0
        print(f"\n>> SYSTEM STOPPED")
        print(f"   Total runtime: {elapsed:.1f}s")
        print(f"   Total readings: {self.total_readings}")
        print(f"   Total alerts: {self.total_alerts}\n")
        
    def read_sensors(self):
        """Read all sensors and return data"""
        readings = self.sensors.read_all()
        self.total_readings += 1
        self.gas_history.append(readings['gas'])
        
        if len(self.gas_history) > 100:
            self.gas_history.pop(0)
            
        return readings
        
    def evaluate_status(self, gas_value, temperature=None, smoke_value=None):
        """Evaluate current status based on sensor readings"""
        if gas_value >= GasThresholds.WARNING:
            if gas_value >= GasThresholds.DANGER:
                return 'DANGER'
            return 'WARNING'
        return 'SAFE'
        
    def process_reading(self, readings):
        """Process a single sensor reading"""
        gas = readings['gas']
        temperature = readings['temperature']
        humidity = readings['humidity']
        smoke = readings['smoke']
        
        status = self.evaluate_status(gas, temperature, smoke)
        old_status = self.current_status
        self.current_status = status
        
        alert_level = self._get_alert_level(status)
        
        if status != old_status or status != 'SAFE':
            alert = self.alerts.trigger_alert(
                alert_level, gas, temperature, smoke
            )
            self.total_alerts += 1
            
            if status != 'SAFE':
                self._send_notifications(status, readings)
                
        self._update_displays(readings, status)
        
        return {
            'status': status,
            'gas': gas,
            'temperature': temperature,
            'humidity': humidity,
            'smoke': smoke,
            'alert_triggered': status != 'SAFE'
        }
        
    def _get_alert_level(self, status):
        """Convert status string to alert level"""
        levels = {
            'SAFE': AlertLevel.SAFE,
            'WARNING': AlertLevel.WARNING,
            'DANGER': AlertLevel.DANGER
        }
        return levels.get(status, AlertLevel.SAFE)
        
    def _send_notifications(self, status, readings):
        """Send notifications via all enabled channels"""
        if status == 'DANGER':
            title = "EMERGENCY: Gas Leak Detected!"
            message = f"Gas level: {readings['gas']} ppm - Evacuate immediately!"
            priority = "critical"
        else:
            title = "Warning: Elevated Gas Levels"
            message = f"Gas level: {readings['gas']} ppm - Investigate"
            priority = "normal"
            
        self.mobile.send_notification(title, message, priority)
        
        data_packet = self.serial.format_data(
            readings['gas'],
            readings['temperature'],
            readings['humidity'],
            readings['smoke'],
            status
        )
        self.serial.send_data(data_packet)
        
    def _update_displays(self, readings, status):
        """Update all display outputs"""
        self.lcd.update(readings['gas'], readings['temperature'], status)
        
    def get_system_status(self):
        """Get comprehensive system status"""
        uptime = time.time() - self.start_time if self.start_time else 0
        avg_gas = sum(self.gas_history) / len(self.gas_history) if self.gas_history else 0
        max_gas = max(self.gas_history) if self.gas_history else 0
        
        return {
            'is_running': self.is_running,
            'current_status': self.current_status,
            'uptime': uptime,
            'total_readings': self.total_readings,
            'total_alerts': self.total_alerts,
            'avg_gas_level': avg_gas,
            'max_gas_level': max_gas,
            'sensor_baselines': {
                'gas': self.sensors.gas_sensor.baseline,
                'temperature': self.sensors.temp_sensor.baseline,
                'smoke': self.sensors.smoke_sensor.baseline
            }
        }
        
    def run_simulation(self, duration=60, gas_scenario=None):
        """
        Run a simulation with optional gas scenario
        gas_scenario: list of (time, gas_level) tuples
        """
        self.initialize()
        self.start()
        
        print("\n" + "-" * 60)
        print("  SIMULATION MODE - Press Ctrl+C to stop")
        print("-" * 60 + "\n")
        
        start_time = time.time()
        scenario_index = 0
        
        try:
            while self.is_running and (time.time() - start_time) < duration:
                elapsed = time.time() - start_time
                
                if gas_scenario and scenario_index < len(gas_scenario):
                    target_time, target_gas = gas_scenario[scenario_index]
                    if elapsed >= target_time:
                        self.sensors.gas_sensor.set_gas_level(target_gas)
                        print(f"\n[SCENARIO] Setting gas level to {target_gas * 10.23:.0f} ppm")
                        scenario_index += 1
                        
                readings = self.read_sensors()
                result = self.process_reading(readings)
                
                ConsoleDisplay.print_status(
                    readings['gas'],
                    readings['temperature'],
                    readings['humidity'],
                    readings['smoke'],
                    result['status']
                )
                
                time.sleep(SystemConfig.SENSOR_READ_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n\n[INTERRUPT] Simulation stopped by user")
            
        finally:
            self.stop()
            self._print_summary()
            
    def _print_summary(self):
        """Print simulation summary"""
        status = self.get_system_status()
        
        print("\n" + "=" * 60)
        print("  SIMULATION SUMMARY")
        print("=" * 60)
        print(f"  Runtime:          {status['uptime']:.1f} seconds")
        print(f"  Total Readings:   {status['total_readings']}")
        print(f"  Total Alerts:     {status['total_alerts']}")
        print(f"  Average Gas:      {status['avg_gas_level']:.1f} ppm")
        print(f"  Maximum Gas:      {status['max_gas_level']:.1f} ppm")
        print(f"  Final Status:     {status['current_status']}")
        print("=" * 60)
        

class HardwareInterface:
    """Interface for actual hardware connections"""
    
    def __init__(self, port=SystemConfig.SERIAL_PORT):
        self.port = port
        self.arduino = None
        
    def connect_arduino(self):
        """Connect to Arduino (simulated)"""
        print(f"[HARDWARE] Connecting to Arduino on {self.port}...")
        print("[HARDWARE] Arduino connected successfully")
        return True
        
    def send_command(self, command):
        """Send command to Arduino"""
        print(f"[HARDWARE] Command sent: {command}")
        return True
        
    def read_data(self):
        """Read data from Arduino"""
        return None
