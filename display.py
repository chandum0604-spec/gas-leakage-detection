"""
Display Module for Gas Leakage Detection System
Simulates LCD display and mobile app interface
"""

import time
from config import SystemConfig


class LCDDisplay:
    """
    16x2 LCD Display Simulation
    Shows gas level, temperature, and system status
    """
    
    def __init__(self, rows=16, cols=2):
        self.rows = rows
        self.cols = cols
        self.content = [[' ' for _ in range(rows)] for _ in range(cols)]
        self.backlight = True
        
    def clear(self):
        """Clear LCD screen"""
        self.content = [[' ' for _ in range(self.rows)] for _ in range(self.cols)]
        
    def print_line(self, line_num, text):
        """Print text on specific line"""
        if 0 <= line_num < self.cols:
            self.content[line_num] = list(text.ljust(self.rows)[:self.rows])
            
    def update(self, gas_value, temperature, status):
        """Update LCD with current readings"""
        self.clear()
        
        gas_text = f"GAS:{gas_value:4d} PPM"
        self.print_line(0, gas_text)
        
        temp_text = f"TEMP:{temperature:5.1f}C {status}"
        self.print_line(1, temp_text)
        
    def show_message(self, line1, line2=""):
        """Display custom message"""
        self.clear()
        self.print_line(0, line1)
        if line2:
            self.print_line(1, line2)
            
    def render(self):
        """Render LCD content to console"""
        if not self.backlight:
            return "LCD OFF"
            
        border = "+" + "-" * self.rows + "+"
        lines = []
        lines.append(border)
        for row in self.content:
            lines.append("|" + "".join(row) + "|")
        lines.append(border)
        return "\n".join(lines)


class SerialMonitor:
    """Serial output for Arduino/microcontroller communication"""
    
    def __init__(self, port=SystemConfig.SERIAL_PORT, baudrate=SystemConfig.BAUD_RATE):
        self.port = port
        self.baudrate = baudrate
        self.connected = False
        self.buffer = []
        
    def connect(self):
        """Simulate serial connection"""
        self.connected = True
        print(f"  [SERIAL] Connected to {self.port} @ {self.baudrate} baud")
        
    def send_data(self, data):
        """Send data via serial"""
        if self.connected:
            self.buffer.append(data)
            return True
        return False
        
    def format_data(self, gas, temp, humidity, smoke, status):
        """Format sensor data for transmission"""
        return f"G:{gas},T:{temp},H:{humidity},S:{smoke},ST:{status}"
        
    def read_buffer(self):
        """Read and clear buffer"""
        data = self.buffer.copy()
        self.buffer.clear()
        return data


class MobileApp:
    """Mobile application interface simulation"""
    
    def __init__(self):
        self.notifications = []
        self.last_update = None
        
    def send_notification(self, title, message, priority="normal"):
        """Send mobile notification"""
        notification = {
            'title': title,
            'message': message,
            'priority': priority,
            'timestamp': time.strftime('%H:%M:%S')
        }
        self.notifications.append(notification)
        self.last_update = time.time()
        return notification
        
    def update_dashboard(self, gas_value, temperature, smoke_value, status):
        """Update mobile dashboard"""
        dashboard = {
            'gas_level': gas_value,
            'temperature': temperature,
            'smoke_level': smoke_value,
            'status': status,
            'last_update': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        return dashboard
        
    def get_notifications(self, limit=5):
        """Get recent notifications"""
        return self.notifications[-limit:]
    
    def clear_notifications(self):
        """Clear notification history"""
        self.notifications = []


class ConsoleDisplay:
    """Console-based display for simulation"""
    
    ANSI_COLORS = {
        'RED': '\033[91m',
        'GREEN': '\033[92m',
        'YELLOW': '\033[93m',
        'BLUE': '\033[94m',
        'RESET': '\033[0m'
    }
    
    @classmethod
    def clear_screen(cls):
        """Clear console screen"""
        print('\033[2J\033[H', end='')
        
    @classmethod
    def print_header(cls):
        """Print system header"""
        header = f"""
{cls.ANSI_COLORS['BLUE']}+====================================================================+
|     GAS LEAKAGE DETECTION SYSTEM - Real-time Monitor         |
+====================================================================+{cls.ANSI_COLORS['RESET']}
"""
        print(header)
        
    @classmethod
    def print_status(cls, gas_value, temperature, humidity, smoke, status):
        """Print current status"""
        color = cls._get_status_color(status)
        
        status_display = f"""
+-----------------------------------------------------------------+
|  SENSOR READINGS                                                |
+-----------------------------------------------------------------+
|  Gas Level:    {cls.ANSI_COLORS[color]}{gas_value:>6} ppm{cls.ANSI_COLORS['RESET']}     Status: {cls.ANSI_COLORS[color]}[{status}]{cls.ANSI_COLORS['RESET']}
|  Temperature:  {temperature:>6.1f} C                                      
|  Humidity:     {humidity:>6.1f} %                                      
|  Smoke Level:  {smoke:>6} ppm                                      
+-----------------------------------------------------------------+
|  Thresholds: Safe<200 | Warning 200-500 | Danger >500          |
+-----------------------------------------------------------------+
"""
        print(status_display)
        
    @classmethod
    def print_sensor_info(cls, sensor_data):
        """Print detailed sensor information"""
        print("\n[ SENSOR MODULES ]")
        for sensor in sensor_data:
            calibrated = "Yes" if sensor['is_calibrated'] else "No"
            print(f"  {sensor['name']}")
            print(f"    Pin: A{sensor['pin']} | Baseline: {sensor['baseline']:.1f} | Calibrated: {calibrated}")
            
    @classmethod
    def print_system_info(cls, uptime, total_alerts):
        """Print system information"""
        print(f"\n[ SYSTEM INFO ]")
        print(f"  Uptime: {uptime}s | Total Alerts: {total_alerts}")
        
    @classmethod
    def _get_status_color(cls, status):
        """Get color for status"""
        colors = {
            'SAFE': 'GREEN',
            'WARNING': 'YELLOW',
            'DANGER': 'RED'
        }
        return colors.get(status, 'BLUE')
        
    @classmethod
    def print_progress_bar(cls, value, max_value, width=40):
        """Print progress bar"""
        filled = int(width * value / max_value)
        bar = '=' * filled + '-' * (width - filled)
        percentage = int(100 * value / max_value)
        return f"[{bar}] {percentage}%"
