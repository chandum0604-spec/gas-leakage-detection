"""
Web Dashboard for Gas Leakage Detection System
Provides browser-based monitoring interface
"""

from flask import Flask, render_template_string, jsonify, request
from datetime import datetime
import threading
import time

app = Flask(__name__)

system_state = {
    'is_running': False,
    'current_status': 'SAFE',
    'gas_level': 0,
    'temperature': 25.0,
    'humidity': 60.0,
    'smoke_level': 0,
    'total_alerts': 0,
    'last_update': datetime.now().isoformat()
}

dashboard_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Gas Leak Detection Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        
        h1 { 
            text-align: center; 
            margin-bottom: 30px;
            color: #00d9ff;
            text-shadow: 0 0 20px rgba(0,217,255,0.5);
        }
        
        .status-banner {
            text-align: center;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            transition: all 0.3s ease;
        }
        .status-banner.safe { background: linear-gradient(135deg, #00c853, #00e676); }
        .status-banner.warning { background: linear-gradient(135deg, #ffab00, #ffd600); }
        .status-banner.danger { background: linear-gradient(135deg, #d50000, #ff1744); animation: pulse 1s infinite; }
        
        @keyframes pulse {
            0%, 100% { box-shadow: 0 0 20px rgba(213,0,0,0.7); }
            50% { box-shadow: 0 0 40px rgba(213,0,0,1); }
        }
        
        .status-text { font-size: 3em; font-weight: bold; text-transform: uppercase; }
        .status-gas { font-size: 1.5em; margin-top: 10px; }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
        }
        
        .card h3 { color: #00d9ff; margin-bottom: 15px; font-size: 0.9em; text-transform: uppercase; }
        .card .value { font-size: 2.5em; font-weight: bold; }
        .card .unit { font-size: 0.5em; color: #aaa; }
        
        .thresholds {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
        }
        .thresholds h3 { color: #00d9ff; margin-bottom: 15px; }
        .threshold-bar {
            height: 30px;
            background: linear-gradient(90deg, #00c853 0%, #00c853 25%, #ffd600 25%, #ffd600 50%, #ff1744 50%, #ff1744 100%);
            border-radius: 15px;
            position: relative;
            margin: 20px 0;
        }
        .threshold-marker {
            position: absolute;
            width: 4px;
            height: 40px;
            background: #fff;
            top: -5px;
            border-radius: 2px;
            transition: left 0.5s ease;
        }
        
        .controls {
            text-align: center;
            margin-bottom: 30px;
        }
        .btn {
            padding: 15px 40px;
            border: none;
            border-radius: 25px;
            font-size: 1.1em;
            cursor: pointer;
            margin: 5px;
            transition: all 0.3s ease;
        }
        .btn-start { background: #00c853; color: #fff; }
        .btn-stop { background: #d50000; color: #fff; }
        .btn-danger { background: #ff1744; color: #fff; }
        .btn:hover { transform: scale(1.05); box-shadow: 0 5px 20px rgba(0,0,0,0.3); }
        
        .footer {
            text-align: center;
            color: #666;
            margin-top: 30px;
            font-size: 0.8em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Gas Leakage Detection System</h1>
        
        <div class="status-banner {{ status_class }}" id="statusBanner">
            <div class="status-text" id="statusText">{{ current_status }}</div>
            <div class="status-gas" id="gasDisplay">Gas Level: {{ gas_level }} ppm</div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>Temperature</h3>
                <div class="value" id="tempValue">{{ "%.1f"|format(temperature) }}</div>
                <div class="unit">Celsius</div>
            </div>
            <div class="card">
                <h3>Humidity</h3>
                <div class="value" id="humidityValue">{{ "%.1f"|format(humidity) }}</div>
                <div class="unit">Percent</div>
            </div>
            <div class="card">
                <h3>Smoke Level</h3>
                <div class="value" id="smokeValue">{{ smoke_level }}</div>
                <div class="unit">ppm</div>
            </div>
            <div class="card">
                <h3>Total Alerts</h3>
                <div class="value" id="alertCount">{{ total_alerts }}</div>
                <div class="unit">Events</div>
            </div>
        </div>
        
        <div class="thresholds">
            <h3>Gas Level Indicator</h3>
            <div style="display: flex; justify-content: space-between; font-size: 0.8em;">
                <span>SAFE</span><span>WARNING</span><span>DANGER</span>
            </div>
            <div class="threshold-bar">
                <div class="threshold-marker" id="thresholdMarker" style="left: {{ gas_percent }}%;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.7em; color: #888;">
                <span>0</span><span>200</span><span>500</span><span>800</span><span>1023</span>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn btn-start" onclick="setGasLevel('safe')">Safe Mode</button>
            <button class="btn btn-warning" onclick="setGasLevel('warning')">Warning Mode</button>
            <button class="btn btn-danger" onclick="setGasLevel('danger')">Danger Mode</button>
        </div>
        
        <div class="footer">
            Last Update: <span id="lastUpdate">{{ last_update }}</span>
        </div>
    </div>
    
    <script>
        function updateData() {
            fetch('/api/status')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('statusText').textContent = data.current_status;
                    document.getElementById('gasDisplay').textContent = 'Gas Level: ' + data.gas_level + ' ppm';
                    document.getElementById('tempValue').textContent = data.temperature.toFixed(1);
                    document.getElementById('humidityValue').textContent = data.humidity.toFixed(1);
                    document.getElementById('smokeValue').textContent = data.smoke_level;
                    document.getElementById('alertCount').textContent = data.total_alerts;
                    document.getElementById('lastUpdate').textContent = data.last_update;
                    document.getElementById('thresholdMarker').style.left = (data.gas_level / 1023 * 100) + '%';
                    
                    const banner = document.getElementById('statusBanner');
                    banner.className = 'status-banner ' + data.status_class;
                });
        }
        
        function setGasLevel(mode) {
            fetch('/api/set_level', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({mode: mode})
            });
        }
        
        setInterval(updateData, 1000);
        updateData();
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(dashboard_html, 
        status_class=system_state.get('status_class', 'safe'),
        current_status=system_state['current_status'],
        gas_level=system_state['gas_level'],
        gas_percent=system_state['gas_level'] / 1023 * 100,
        temperature=system_state['temperature'],
        humidity=system_state['humidity'],
        smoke_level=system_state['smoke_level'],
        total_alerts=system_state['total_alerts'],
        last_update=system_state['last_update']
    )


@app.route('/api/status')
def get_status():
    return jsonify(system_state)


@app.route('/api/set_level', methods=['POST'])
def set_level():
    from sensors import SensorArray
    
    mode = request.json.get('mode', 'safe')
    sensors = SensorArray()
    
    if mode == 'safe':
        sensors.gas_sensor.set_gas_level(5)
    elif mode == 'warning':
        sensors.gas_sensor.set_gas_level(40)
    elif mode == 'danger':
        sensors.gas_sensor.set_gas_level(85)
        
    readings = sensors.read_all()
    
    system_state['gas_level'] = readings['gas']
    system_state['temperature'] = readings['temperature']
    system_state['humidity'] = readings['humidity']
    system_state['smoke_level'] = readings['smoke']
    system_state['last_update'] = datetime.now().isoformat()
    
    return jsonify({'status': 'ok'})


def run_dashboard(host='0.0.0.0', port=5000):
    app.run(host=host, port=port, debug=False, threaded=True)
