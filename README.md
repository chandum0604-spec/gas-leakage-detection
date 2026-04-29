# Gas Leakage Detection System

A comprehensive simulation of a real-time gas leakage detection system using MQ-2/MQ-5 gas sensors with multi-level alerting capabilities.

## Features

- **Real-time Gas Monitoring**: Continuous monitoring of gas levels using MQ-2/MQ-5 sensors
- **Multi-level Alert System**: SAFE, WARNING, and DANGER states
- **Multiple Alert Mechanisms**: Buzzer, LED indicators, SMS notifications
- **LCD Display**: 16x2 LCD showing real-time readings
- **Mobile App Interface**: Push notifications for remote monitoring
- **Sensor Calibration**: Automatic baseline calibration
- **Temperature & Smoke Integration**: Additional safety sensors

## Hardware Requirements

| Component | Cost | Purpose |
|-----------|------|---------|
| MQ-2/MQ-5 Gas Sensor | $3-5 | Gas detection |
| Arduino Uno/Nano | $5-7 | Main controller |
| Buzzer (5V) | $1-2 | Audible alarm |
| LED Array | $1 | Visual indicators |
| LCD 16x2 | $3-5 | Display output |
| GSM Module | $10-15 | SMS alerts (optional) |

**Total Cost**: ~$15-35

## Threshold Configuration

| Status | Gas Level | LED Color | Alert |
|--------|-----------|-----------|-------|
| SAFE | < 200 ppm | Green | None |
| WARNING | 200-500 ppm | Yellow | Slow beep |
| DANGER | > 500 ppm | Red | Fast beep + SMS |

## Installation

```bash
cd GasLeakDetectionSystem
python main.py
```

## Usage

1. Run `python main.py`
2. Select demo mode or interactive testing
3. System will display real-time sensor readings and alerts

## Project Structure

```
GasLeakDetectionSystem/
├── config.py           # Configuration settings
├── sensors.py          # Sensor modules (Gas, Temp, Smoke)
├── alerts.py           # Alert management system
├── display.py          # LCD and console display
├── detection_system.py # Main detection logic
├── main.py            # Entry point
└── README.md          # This file
```

## System Architecture

```
MQ-2 Gas Sensor ──► Arduino ──► Alert System
                              ├── Buzzer
                              ├── LED Array
                              ├── LCD Display
                              └── GSM Module (SMS)
```

## License

MIT License - Educational Project
