"""
Gas Leakage Detection System - Logging Module
Records sensor data and alerts for analysis and compliance
"""

import json
import csv
from datetime import datetime
from pathlib import Path


class DataLogger:
    """Handles logging of sensor readings and alerts"""
    
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.csv_file = self.log_dir / "sensor_data.csv"
        self.alert_file = self.log_dir / "alerts.json"
        self._init_csv()
        
    def _init_csv(self):
        """Initialize CSV file with headers"""
        if not self.csv_file.exists():
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'gas_ppm', 'temperature_c', 
                    'humidity_pct', 'smoke_ppm', 'status'
                ])
                
    def log_reading(self, gas, temperature, humidity, smoke, status):
        """Log a sensor reading"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(self.csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp, gas, temperature, humidity, smoke, status
            ])
            
    def log_alert(self, level, gas_value, temperature, smoke_value):
        """Log an alert event"""
        alerts = self._load_alerts()
        
        alert = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'level': level,
            'gas_value': gas_value,
            'temperature': temperature,
            'smoke_value': smoke_value
        }
        
        alerts.append(alert)
        
        with open(self.alert_file, 'w') as f:
            json.dump(alerts[-1000:], f, indent=2)
            
    def _load_alerts(self):
        """Load existing alerts"""
        if self.alert_file.exists():
            with open(self.alert_file, 'r') as f:
                return json.load(f)
        return []
        
    def get_recent_readings(self, limit=100):
        """Get recent sensor readings"""
        readings = []
        
        if self.csv_file.exists():
            with open(self.csv_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    readings.append(row)
                    
        return readings[-limit:]
        
    def get_statistics(self):
        """Calculate statistics from logged data"""
        readings = self.get_recent_readings(1000)
        
        if not readings:
            return None
            
        gas_values = [int(r['gas_ppm']) for r in readings]
        
        return {
            'total_readings': len(readings),
            'avg_gas': sum(gas_values) / len(gas_values),
            'max_gas': max(gas_values),
            'min_gas': min(gas_values),
            'danger_count': sum(1 for r in readings if r['status'] == 'DANGER'),
            'warning_count': sum(1 for r in readings if r['status'] == 'WARNING')
        }
