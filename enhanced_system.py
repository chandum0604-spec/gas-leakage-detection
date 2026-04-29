"""
Production-ready Gas Leakage Detection System
Enhanced version with logging, web dashboard, and comprehensive alerts
"""

import sys
import time
from datetime import datetime

from config import GasThresholds, SystemConfig
from sensors import SensorArray
from alerts import AlertManager, AlertLevel
from display import LCDDisplay, ConsoleDisplay
from logger import DataLogger


class EnhancedDetectionSystem:
    """
    Enhanced gas detection system with:
    - Data logging
    - Web dashboard support
    - Comprehensive alerting
    - Statistics tracking
    """
    
    def __init__(self, enable_logging=True, enable_web=False):
        self.enable_logging = enable_logging
        self.enable_web = enable_web
        self.is_running = False
        self.start_time = None
        self.total_readings = 0
        self.total_alerts = 0
        
        self.sensors = SensorArray()
        self.alerts = AlertManager()
        self.lcd = LCDDisplay(SystemConfig.LCD_COLS, SystemConfig.LCD_ROWS)
        
        if enable_logging:
            self.logger = DataLogger()
        else:
            self.logger = None
            
        self.current_status = 'SAFE'
        self.gas_history = []
        self.danger_count = 0
        self.warning_count = 0
        
    def initialize(self):
        """Initialize the detection system"""
        print("\n" + "=" * 60)
        print("  GAS LEAKAGE DETECTION SYSTEM - Enhanced v1.0")
        print("=" * 60)
        
        print("\n[1/5] Calibrating sensors...")
        calibration = self.sensors.calibrate_all()
        for name, baseline in calibration.items():
            print(f"       {name}: Baseline = {baseline:.1f}")
            
        print("\n[2/5] Testing alert systems...")
        self.alerts.trigger_alert(AlertLevel.SAFE, 100)
        print("       Alert system: OK")
        
        print("\n[3/5] Initializing display modules...")
        self.lcd.show_message("GAS DETECTOR", "System Ready")
        
        print("\n[4/5] Initializing data logging...")
        if self.logger:
            print("       Logging: ENABLED")
            stats = self.logger.get_statistics()
            if stats:
                print(f"       Previous readings: {stats['total_readings']}")
        else:
            print("       Logging: DISABLED")
            
        print("\n[5/5] System initialization complete!")
        print(f"       Logging: {'ENABLED' if self.enable_logging else 'DISABLED'}")
        print(f"       Web Dashboard: {'ENABLED' if self.enable_web else 'DISABLED'}")
        print("=" * 60 + "\n")
        
        return True
        
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
        print(f"   Runtime: {elapsed:.1f}s")
        print(f"   Total readings: {self.total_readings}")
        print(f"   Total alerts: {self.total_alerts}")
        print(f"   Danger events: {self.danger_count}")
        print(f"   Warning events: {self.warning_count}\n")
        
    def read_sensors(self):
        """Read all sensors"""
        readings = self.sensors.read_all()
        self.total_readings += 1
        self.gas_history.append(readings['gas'])
        
        if len(self.gas_history) > 1000:
            self.gas_history.pop(0)
            
        return readings
        
    def evaluate_status(self, gas_value):
        """Evaluate status based on gas level"""
        if gas_value >= GasThresholds.WARNING:
            if gas_value >= GasThresholds.DANGER:
                return 'DANGER'
            return 'WARNING'
        return 'SAFE'
        
    def process_reading(self, readings):
        """Process sensor reading"""
        gas = readings['gas']
        temperature = readings['temperature']
        humidity = readings['humidity']
        smoke = readings['smoke']
        
        status = self.evaluate_status(gas)
        old_status = self.current_status
        self.current_status = status
        
        if status == 'DANGER':
            self.danger_count += 1
        elif status == 'WARNING':
            self.warning_count += 1
            
        alert_level = self._get_alert_level(status)
        
        if status != old_status or status != 'SAFE':
            alert = self.alerts.trigger_alert(alert_level, gas, temperature, smoke)
            self.total_alerts += 1
            
            if self.logger and status != 'SAFE':
                self.logger.log_alert(status, gas, temperature, smoke)
                
        if self.logger:
            self.logger.log_reading(gas, temperature, humidity, smoke, status)
            
        self._update_displays(gas, temperature, status)
        
        return {
            'status': status,
            'gas': gas,
            'temperature': temperature,
            'humidity': humidity,
            'smoke': smoke,
            'alert_triggered': status != 'SAFE'
        }
        
    def _get_alert_level(self, status):
        """Convert status to alert level"""
        levels = {'SAFE': AlertLevel.SAFE, 'WARNING': AlertLevel.WARNING, 'DANGER': AlertLevel.DANGER}
        return levels.get(status, AlertLevel.SAFE)
        
    def _update_displays(self, gas, temperature, status):
        """Update display outputs"""
        self.lcd.update(gas, temperature, status)
        
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
            'danger_count': self.danger_count,
            'warning_count': self.warning_count,
            'avg_gas_level': avg_gas,
            'max_gas_level': max_gas,
            'status_class': self.current_status.lower()
        }
        
    def run_monitoring(self, duration=60):
        """Run continuous monitoring"""
        self.initialize()
        self.start()
        
        start_time = time.time()
        
        try:
            while self.is_running and (time.time() - start_time) < duration:
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
            print("\n\n[INTERRUPT] Monitoring stopped by user")
            
        finally:
            self.stop()
            self._print_statistics()
            
    def _print_statistics(self):
        """Print monitoring statistics"""
        if not self.logger:
            return
            
        stats = self.logger.get_statistics()
        
        print("\n" + "=" * 60)
        print("  MONITORING STATISTICS")
        print("=" * 60)
        print(f"  Total Readings:   {self.total_readings}")
        print(f"  Average Gas:     {stats['avg_gas']:.1f} ppm" if stats else "  Average Gas: N/A")
        print(f"  Maximum Gas:     {stats['max_gas']:.0f} ppm" if stats else "  Maximum Gas: N/A")
        print(f"  Danger Events:   {self.danger_count}")
        print(f"  Warning Events:  {self.warning_count}")
        print("=" * 60)


def main():
    """Main entry point for enhanced system"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gas Leakage Detection System')
    parser.add_argument('--no-log', action='store_true', help='Disable data logging')
    parser.add_argument('--web', action='store_true', help='Enable web dashboard')
    parser.add_argument('--duration', type=int, default=60, help='Monitoring duration (seconds)')
    parser.add_argument('--safe', action='store_true', help='Run in safe mode')
    parser.add_argument('--warning', action='store_true', help='Run in warning mode')
    parser.add_argument('--danger', action='store_true', help='Run in danger mode')
    
    args = parser.parse_args()
    
    system = EnhancedDetectionSystem(
        enable_logging=not args.no_log,
        enable_web=args.web
    )
    
    if args.web:
        print("[INFO] Starting web dashboard on http://localhost:5000")
        from web_dashboard import run_dashboard
        import threading
        threading.Thread(target=run_dashboard, daemon=True).start()
        time.sleep(2)
        
    system.initialize()
    system.start()
    
    if args.safe:
        system.sensors.gas_sensor.set_gas_level(5)
    elif args.warning:
        system.sensors.gas_sensor.set_gas_level(40)
    elif args.danger:
        system.sensors.gas_sensor.set_gas_level(85)
        
    system.run_monitoring(duration=args.duration)


if __name__ == "__main__":
    main()
