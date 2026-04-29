"""
Alert System for Gas Leakage Detection
Handles buzzer, LED indicators, SMS, and email notifications
"""

import time
from enum import Enum
from config import AlertConfig


class AlertLevel(Enum):
    SAFE = 0
    WARNING = 1
    DANGER = 2


class AlertManager:
    def __init__(self):
        self.buzzer_active = False
        self.led_state = 'OFF'
        self.alert_history = []
        self.last_sms_time = 0
        self.last_email_time = 0
        
    def trigger_alert(self, level, gas_value, temperature=None, smoke_value=None):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        
        alert = {
            'timestamp': timestamp,
            'level': level,
            'gas_value': gas_value,
            'temperature': temperature,
            'smoke_value': smoke_value
        }
        
        self.alert_history.append(alert)
        
        if level == AlertLevel.DANGER:
            self._danger_alert(alert)
        elif level == AlertLevel.WARNING:
            self._warning_alert(alert)
        else:
            self._safe_status()
            
        return alert
    
    def _danger_alert(self, alert):
        """Critical danger alert sequence"""
        if AlertConfig.ENABLE_BUZZER:
            self._activate_buzzer(danger=True)
        
        if AlertConfig.ENABLE_LED:
            self.led_state = 'RED'
            print(f"  [{alert['timestamp']}] [DANGER] LED: RED - CRITICAL GAS LEAKAGE!")
        
        if AlertConfig.ENABLE_SMS:
            self._send_sms(alert)
            
        self._log_alert("CRITICAL: Immediate evacuation recommended!", "DANGER")
        
    def _warning_alert(self, alert):
        """Warning alert for moderate gas levels"""
        if AlertConfig.ENABLE_BUZZER:
            self._activate_buzzer(danger=False)
            
        if AlertConfig.ENABLE_LED:
            self.led_state = 'YELLOW'
            print(f"  [{alert['timestamp']}] [WARNING] LED: YELLOW - Moderate gas detected")
            
        self._log_alert("CAUTION: Gas levels elevated, investigate source", "WARNING")
        
    def _safe_status(self):
        """Safe status indication"""
        if AlertConfig.ENABLE_BUZZER:
            self._deactivate_buzzer()
            
        if AlertConfig.ENABLE_LED:
            self.led_state = 'GREEN'
            
    def _activate_buzzer(self, danger=True):
        """Activate buzzer alarm"""
        self.buzzer_active = True
        pattern = "RAPID BEEPING" if danger else "SLOW BEEPING"
        print(f"  [BUZZER] Active - {pattern} pattern")
        
    def _deactivate_buzzer(self):
        """Deactivate buzzer alarm"""
        self.buzzer_active = False
        print("  [BUZZER] Inactive - System Safe")
        
    def _send_sms(self, alert):
        """Send SMS notification (simulated)"""
        current_time = time.time()
        if current_time - self.last_sms_time > AlertConfig.SMS_INTERVAL:
            print(f"  [SMS] Sending emergency notification...")
            print(f"        EMERGENCY: Gas leak detected!")
            print(f"        Gas Level: {alert['gas_value']} ppm")
            print(f"        Location: Kitchen/Sensor Unit")
            print(f"        Time: {alert['timestamp']}")
            self.last_sms_time = current_time
            
    def _log_alert(self, message, level):
        """Log alert to history"""
        print(f"  [LOG] {level}: {message}")
        
    def get_alert_history(self, limit=10):
        """Get recent alert history"""
        return self.alert_history[-limit:]
    
    def clear_history(self):
        """Clear alert history"""
        self.alert_history = []


class BuzzerController:
    """Direct buzzer control for fine-tuned alerting"""
    
    def __init__(self, pin=8):
        self.pin = pin
        self.is_on = False
        self.frequency = AlertConfig.BUZZER_FREQUENCY
        
    def beep(self, duration=0.5):
        """Single beep"""
        self.is_on = True
        time.sleep(duration)
        self.is_on = False
        
    def beep_pattern(self, count=3, interval=0.3):
        """Multiple beeps"""
        for _ in range(count):
            self.beep(0.2)
            time.sleep(interval)
            
    def continuous_alarm(self):
        """Start continuous alarm"""
        self.is_on = True
        return self.is_on
        
    def stop_alarm(self):
        """Stop continuous alarm"""
        self.is_on = False
        return self.is_on


class LEDController:
    """LED indicator control"""
    
    def __init__(self, green_pin=2, yellow_pin=3, red_pin=4):
        self.green_pin = green_pin
        self.yellow_pin = yellow_pin
        self.red_pin = red_pin
        self.current_color = 'OFF'
        
    def set_color(self, color):
        """Set LED color"""
        colors = ['GREEN', 'YELLOW', 'RED', 'OFF']
        if color.upper() in colors:
            self.current_color = color.upper()
            print(f"  [LED] Color set to: {self.current_color}")
            
    def blink(self, color, times=5, interval=0.5):
        """Blink LED"""
        for _ in range(times):
            self.set_color(color)
            time.sleep(interval)
            self.set_color('OFF')
            time.sleep(interval)
            
    def get_status(self):
        """Get current LED status"""
        return self.current_color
