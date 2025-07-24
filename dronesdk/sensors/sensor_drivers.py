from typing import Optional, Dict, Any

class LIDARSensor:
    """Interface for LIDAR sensor readings."""
    
    def __init__(self, port: str = "/dev/ttyUSB1", baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        
    def connect(self) -> bool:
        """Connect to LIDAR sensor."""
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            return True
        except Exception as e:
            print(f"LIDAR connection error: {e}")
            return False
            
    def read_distance(self) -> Optional[float]:
        """Read distance measurement from LIDAR."""
        if not self.serial_conn:
            return None
            
        try:
            self.serial_conn.write(b'M')
            data = self.serial_conn.read(4)
            if len(data) == 4:
                distance = struct.unpack('<f', data)[0]
                return distance
        except Exception as e:
            print(f"LIDAR read error: {e}")
            
        return None
        
    def read_scan(self, num_points: int = 360) -> list:
        """Read a full 360-degree scan."""
        scan_data = []
        for angle in range(num_points):
            distance = self.read_distance()
            if distance is not None:
                scan_data.append({
                    'angle': angle,
                    'distance': distance,
                    'timestamp': time.time()
                })
            time.sleep(0.01)
            
        return scan_data
        
    def disconnect(self):
        """Disconnect from LIDAR sensor."""
        if self.serial_conn:
            self.serial_conn.close()
            self.serial_conn = None

class UltrasonicSensor:
    """Interface for ultrasonic distance sensor."""
    
    def __init__(self, trigger_pin: int = 18, echo_pin: int = 24):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.initialized = False
        
        try:
            self.GPIO = GPIO
            self._setup_gpio()
        except ImportError:
            print("RPi.GPIO not available - using simulated readings")
            self.GPIO = None
            
    def _setup_gpio(self):
        """Setup GPIO pins for ultrasonic sensor."""
        if self.GPIO:
            self.GPIO.setmode(self.GPIO.BCM)
            self.GPIO.setup(self.trigger_pin, self.GPIO.OUT)
            self.GPIO.setup(self.echo_pin, self.GPIO.IN)
            self.initialized = True
            
    def read_distance(self) -> Optional[float]:
        """Read distance measurement from ultrasonic sensor."""
        if not self.initialized or not self.GPIO:
            return random.uniform(0.1, 4.0)
            
        try:
            self.GPIO.output(self.trigger_pin, True)
            time.sleep(0.00001)
            self.GPIO.output(self.trigger_pin, False)
            
            start_time = time.time()
            while self.GPIO.input(self.echo_pin) == 0:
                start_time = time.time()
                
            while self.GPIO.input(self.echo_pin) == 1:
                end_time = time.time()
                
            pulse_duration = end_time - start_time
            distance = (pulse_duration * 34300) / 2
            
            return distance / 100
            
        except Exception as e:
            print(f"Ultrasonic sensor error: {e}")
            return None
            
    def cleanup(self):
        """Cleanup GPIO resources."""
        if self.GPIO and self.initialized:
            self.GPIO.cleanup()