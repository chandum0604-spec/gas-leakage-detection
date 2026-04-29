"""
Gas Leakage Detection System - Main Entry Point
===============================================
A comprehensive simulation of a gas leakage detection system
using MQ-2/MQ-5 gas sensors with real-time monitoring and alerts.
"""

from enhanced_system import EnhancedDetectionSystem
from display import ConsoleDisplay
import sys
import os


def demo_normal_operation():
    """Demonstrate system in normal (safe) operation"""
    print("\n" + "=" * 60)
    print("  DEMO 1: Normal Safe Operation")
    print("=" * 60 + "\n")
    
    system = EnhancedDetectionSystem(enable_logging=False)
    system.initialize()
    system.sensors.gas_sensor.set_gas_level(5)
    system.start()
    
    print("Running monitoring for 15 seconds with normal gas levels...\n")
    
    for i in range(15):
        readings = system.read_sensors()
        result = system.process_reading(readings)
        ConsoleDisplay.print_status(
            readings['gas'],
            readings['temperature'],
            readings['humidity'],
            readings['smoke'],
            result['status']
        )
        import time
        time.sleep(1)
        
    system.stop()


def demo_warning_scenario():
    """Demonstrate warning level detection"""
    print("\n" + "=" * 60)
    print("  DEMO 2: Warning Level Detection")
    print("=" * 60 + "\n")
    
    system = EnhancedDetectionSystem(enable_logging=False)
    system.initialize()
    system.sensors.gas_sensor.set_gas_level(40)
    system.start()
    
    print("Simulating moderate gas leak (400 ppm)...\n")
    
    for i in range(10):
        readings = system.read_sensors()
        result = system.process_reading(readings)
        ConsoleDisplay.print_status(
            readings['gas'],
            readings['temperature'],
            readings['humidity'],
            readings['smoke'],
            result['status']
        )
        import time
        time.sleep(1)
        
    system.stop()


def demo_danger_scenario():
    """Demonstrate danger level detection with full alerts"""
    print("\n" + "=" * 60)
    print("  DEMO 3: DANGER - High Gas Leakage")
    print("=" * 60 + "\n")
    
    system = EnhancedDetectionSystem(enable_logging=False)
    system.initialize()
    system.sensors.gas_sensor.set_gas_level(85)
    system.start()
    
    print(">>> CRITICAL: Simulating severe gas leak (850 ppm) <<<\n")
    
    for i in range(8):
        readings = system.read_sensors()
        result = system.process_reading(readings)
        ConsoleDisplay.print_status(
            readings['gas'],
            readings['temperature'],
            readings['humidity'],
            readings['smoke'],
            result['status']
        )
        import time
        time.sleep(1)
        
    system.stop()


def demo_full_scenario():
    """Run complete scenario from safe to danger"""
    print("\n" + "=" * 60)
    print("  DEMO 4: Complete Safety Scenario")
    print("=" * 60)
    print("  Simulates a gas leak progression from safe to danger\n")
    
    import time
    
    scenario = [
        (0, 5, "Normal operation"),
        (5, 30, "Gas leak starting"),
        (10, 50, "Warning level"),
        (15, 80, "Danger level"),
        (20, 90, "Critical - Evacuate!"),
        (25, 5, "Gas valve closed - Recovery"),
    ]
    
    system = EnhancedDetectionSystem(enable_logging=True)
    system.initialize()
    system.start()
    
    start_time = time.time()
    current_step = 0
    
    try:
        while system.is_running and (time.time() - start_time) < 30:
            elapsed = time.time() - start_time
            
            if current_step < len(scenario):
                target_time, target_level, description = scenario[current_step]
                if elapsed >= target_time:
                    system.sensors.gas_sensor.set_gas_level(target_level)
                    print(f"\n>>> {description} - Gas level: {target_level * 10.23:.0f} ppm")
                    current_step += 1
                    
            readings = system.read_sensors()
            result = system.process_reading(readings)
            
            ConsoleDisplay.print_status(
                readings['gas'],
                readings['temperature'],
                readings['humidity'],
                readings['smoke'],
                result['status']
            )
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n[INTERRUPT] Simulation stopped by user")
        
    finally:
        system.stop()
        

def demo_web_dashboard():
    """Demonstrate web dashboard"""
    print("\n" + "=" * 60)
    print("  DEMO 5: Web Dashboard")
    print("=" * 60 + "\n")
    
    print("[INFO] Starting web dashboard server...")
    print("[INFO] Dashboard will be available at: http://localhost:5000")
    print("[INFO] Press Ctrl+C to stop the server\n")
    
    from web_dashboard import run_dashboard
    import threading
    
    server_thread = threading.Thread(target=run_dashboard, daemon=True)
    server_thread.start()
    
    print("[INFO] Server started successfully!")
    print("[INFO] Open http://localhost:5000 in your browser\n")
    
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped")


def demo_unit_tests():
    """Run unit tests"""
    print("\n" + "=" * 60)
    print("  Running Unit Tests")
    print("=" * 60 + "\n")
    
    import unittest
    import tests
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("  ALL TESTS PASSED")
    else:
        print("  SOME TESTS FAILED")
    print("=" * 60)
    

def show_system_info():
    """Display system architecture and component information"""
    info = """
================================================================================
                    GAS LEAKAGE DETECTION SYSTEM
                         SYSTEM ARCHITECTURE
================================================================================

  HARDWARE COMPONENTS:
  +-------------------+              +-------------------+
  |  MQ-2/MQ-5 Gas   | ============>|   Arduino/MCU    |
  |    Sensor        |              |  (Processing)    |
  +-------------------+              +---------+--------+
                                                |
                                                v
                                        +-------------------+
                                        | Alert Modules:   |
                                        |  * Buzzer        |
                                        |  * LED Array     |
                                        |  * GSM Module    |
                                        |  * LCD Display   |
                                        +-------------------+

================================================================================
  THRESHOLD CONFIGURATION:
  +------------------------------------------------------------------+
  |  SAFE     : Gas < 200 ppm     | Green LED                        |
  |  WARNING  : Gas 200-500 ppm    | Yellow LED + Slow beep           |
  |  DANGER   : Gas > 500 ppm      | Red LED + Fast beep + SMS        |
  +------------------------------------------------------------------+

================================================================================
  FEATURES:
    [x] Real-time gas level monitoring
    [x] Multi-level alert system
    [x] Temperature and smoke integration
    [x] SMS/Email notifications
    [x] LCD and mobile app display
    [x] Sensor calibration
    [x] Data logging and history
    [x] Web dashboard interface
    [x] Unit tests

================================================================================
  COST ESTIMATE:
    - MQ-2 Gas Sensor:    $3-5
    - Arduino Uno:         $5-7
    - Buzzer (5V):        $1-2
    - LED + Resistors:    $1
    - LCD 16x2:          $3-5
    - GSM Module:         $10-15 (optional)
    - Total:              ~$15-35

================================================================================
"""
    print(info)


def interactive_mode():
    """Interactive mode for custom testing"""
    print("\n" + "=" * 60)
    print("  INTERACTIVE MODE")
    print("=" * 60)
    print("  Commands:")
    print("    safe    - Set safe gas level")
    print("    warning - Set warning gas level")
    print("    danger  - Set danger gas level")
    print("    smoke   - Add smoke detection")
    print("    status  - Show system status")
    print("    quit    - Exit program")
    print("=" * 60 + "\n")
    
    system = EnhancedDetectionSystem(enable_logging=False)
    system.initialize()
    system.start()
    
    commands = {
        'safe': lambda: system.sensors.gas_sensor.set_gas_level(5),
        'warning': lambda: system.sensors.gas_sensor.set_gas_level(40),
        'danger': lambda: system.sensors.gas_sensor.set_gas_level(85),
        'smoke': lambda: system.sensors.smoke_sensor.set_smoke_level(70),
    }
    
    try:
        while True:
            cmd = input("\nCommand> ").strip().lower()
            
            if cmd == 'quit':
                break
            elif cmd == 'status':
                status = system.get_system_status()
                print(f"\nStatus: {status['current_status']}")
                print(f"Readings: {status['total_readings']}")
                print(f"Alerts: {status['total_alerts']}")
            elif cmd in commands:
                commands[cmd]()
                readings = system.read_sensors()
                result = system.process_reading(readings)
                ConsoleDisplay.print_status(
                    readings['gas'],
                    readings['temperature'],
                    readings['humidity'],
                    readings['smoke'],
                    result['status']
                )
            else:
                print("Unknown command. Type 'help' for available commands.")
                
    except KeyboardInterrupt:
        pass
    finally:
        system.stop()


def show_project_structure():
    """Show project file structure"""
    structure = """
================================================================================
                    PROJECT FILE STRUCTURE
================================================================================

GasLeakDetectionSystem/
|
+-- config.py                  Configuration settings and thresholds
+-- sensors.py                  Sensor classes (Gas, Temp, Smoke)
+-- alerts.py                   Alert management system
+-- display.py                  Display interfaces (LCD, Console, Mobile)
+-- logger.py                   Data logging module
+-- detection_system.py         Main detection system
+-- enhanced_system.py          Enhanced version with logging
+-- web_dashboard.py            Flask web dashboard
+-- main.py                     Entry point (this file)
+-- tests.py                    Unit tests
+-- requirements.txt            Python dependencies
|
+-- arduino_sketch/
|   +-- gas_detector/
|       +-- gas_detector.ino   Arduino code
|
+-- logs/                       Data logs directory
|   +-- sensor_data.csv         Historical sensor readings
|   +-- alerts.json             Alert events log
|
+-- DOCUMENTATION.txt           Technical documentation
+-- QUICK_REFERENCE.txt         Quick reference guide
+-- CIRCUIT_DIAGRAM.txt         Wiring diagrams
+-- README.md                   Project readme

================================================================================
"""
    print(structure)


def main():
    """Main entry point"""
    print("""
+=======================================================================+
|              GAS LEAKAGE DETECTION SYSTEM v1.0                       |
|                 Real-time Monitoring & Alerting                      |
+=======================================================================+
""")
    
    menu = """
Select an option:

  [1] System Information & Architecture
  [2] Demo: Normal Safe Operation
  [3] Demo: Warning Level Detection
  [4] Demo: Danger Level Detection
  [5] Demo: Complete Safety Scenario
  [6] Demo: Web Dashboard
  [7] Interactive Mode
  [8] Run Unit Tests
  [9] Show Project Structure

  [0] Exit

"""
    while True:
        print(menu)
        choice = input("Select option: ").strip()
        
        if choice == '0':
            print("\nExiting...")
            break
        elif choice == '1':
            show_system_info()
        elif choice == '2':
            demo_normal_operation()
        elif choice == '3':
            demo_warning_scenario()
        elif choice == '4':
            demo_danger_scenario()
        elif choice == '5':
            demo_full_scenario()
        elif choice == '6':
            demo_web_dashboard()
        elif choice == '7':
            interactive_mode()
        elif choice == '8':
            demo_unit_tests()
        elif choice == '9':
            show_project_structure()
        else:
            print("Invalid option. Please select 0-9.")


if __name__ == "__main__":
    main()
