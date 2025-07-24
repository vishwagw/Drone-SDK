from flask import Flask, request, jsonify
from typing import Dict, Any

class ExternalAPI:
    """Exposes SDK functionality via REST API."""
    
    def __init__(self, drone_instance, host: str = "0.0.0.0", port: int = 5000):
        self.drone = drone_instance
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.server_thread = None
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup REST API routes."""
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """Get drone status."""
            try:
                return jsonify({
                    'armed': self.drone.armed if hasattr(self.drone, 'armed') else False,
                    'mode': getattr(self.drone, 'mode', 'unknown'),
                    'battery': getattr(self.drone, 'battery_level', 0),
                    'connected': getattr(self.drone, 'connected', False)
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/arm', methods=['POST'])
        def arm_drone():
            """Arm the drone."""
            try:
                result = self.drone.arm()
                return jsonify({'success': True, 'result': result})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/disarm', methods=['POST'])
        def disarm_drone():
            """Disarm the drone."""
            try:
                result = self.drone.disarm()
                return jsonify({'success': True, 'result': result})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/takeoff', methods=['POST'])
        def takeoff():
            """Takeoff command."""
            try:
                data = request.get_json()
                altitude = data.get('altitude', 10)
                result = self.drone.takeoff(altitude)
                return jsonify({'success': True, 'result': result})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/land', methods=['POST'])
        def land():
            """Land command."""
            try:
                result = self.drone.land()
                return jsonify({'success': True, 'result': result})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/goto', methods=['POST'])
        def goto_location():
            """Go to specific location."""
            try:
                data = request.get_json()
                lat = data.get('latitude')
                lon = data.get('longitude')
                alt = data.get('altitude', 10)
                
                if lat is None or lon is None:
                    return jsonify({'error': 'Latitude and longitude are required'}), 400
                
                result = self.drone.goto_location(lat, lon, alt)
                return jsonify({'success': True, 'result': result})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/mission', methods=['POST'])
        def upload_mission():
            """Upload and start mission."""
            try:
                data = request.get_json()
                waypoints = data.get('waypoints', [])
                
                if not waypoints:
                    return jsonify({'error': 'Waypoints are required'}), 400
                
                # Convert waypoints to expected format
                mission_waypoints = []
                for wp in waypoints:
                    mission_waypoints.append((wp['latitude'], wp['longitude'], wp.get('altitude', 10)))
                
                self.drone.upload_mission(mission_waypoints)
                result = self.drone.start_mission()
                return jsonify({'success': True, 'result': result})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/telemetry/<data_type>', methods=['GET'])
        def get_telemetry(data_type):
            """Get telemetry data."""
            try:
                # This would need to be implemented with proper async handling
                # For now, return mock data
                return jsonify({'data': 'Telemetry data not implemented yet'}), 501
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def start_server(self):
        """Start the API server in a separate thread."""
        if self.server_thread is None or not self.server_thread.is_alive():
            self.server_thread = threading.Thread(
                target=lambda: self.app.run(host=self.host, port=self.port, debug=False)
            )
            self.server_thread.daemon = True
            self.server_thread.start()
            print(f"API server started on http://{self.host}:{self.port}")
    
    def stop_server(self):
        """Stop the API server."""
        # Flask doesn't have a built-in way to stop the server
        # In production, you'd use a proper WSGI server like Gunicorn
        print("API server stop requested")