from typing import List, Tuple
from collections import deque
import math
import numpy as np

class DataProcessor:
    """Processes raw sensor data for use in applications."""
    
    def __init__(self, buffer_size: int = 100):
        self.gps_buffer = deque(maxlen=buffer_size)
        self.attitude_buffer = deque(maxlen=buffer_size)
        self.battery_buffer = deque(maxlen=buffer_size)
        self.imu_buffer = deque(maxlen=buffer_size)
        
    def add_gps_data(self, gps_data):
        """Add GPS data to buffer."""
        self.gps_buffer.append(gps_data)
        
    def add_attitude_data(self, attitude_data):
        """Add attitude data to buffer."""
        self.attitude_buffer.append(attitude_data)
        
    def add_battery_data(self, battery_data):
        """Add battery data to buffer."""
        self.battery_buffer.append(battery_data)
        
    def add_imu_data(self, imu_data):
        """Add IMU data to buffer."""
        self.imu_buffer.append(imu_data)
        
    def calculate_distance_traveled(self) -> float:
        """Calculate total distance traveled from GPS coordinates."""
        if len(self.gps_buffer) < 2:
            return 0.0
            
        total_distance = 0.0
        for i in range(1, len(self.gps_buffer)):
            prev_point = self.gps_buffer[i-1]
            curr_point = self.gps_buffer[i]
            
            # Haversine formula for distance between GPS coordinates
            lat1, lon1 = math.radians(prev_point.lat), math.radians(prev_point.lon)
            lat2, lon2 = math.radians(curr_point.lat), math.radians(curr_point.lon)
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            r = 6371000  # Earth's radius in meters
            
            total_distance += c * r
            
        return total_distance
        
    def get_average_battery_consumption(self, window_size: int = 10) -> float:
        """Calculate average battery consumption rate."""
        if len(self.battery_buffer) < window_size:
            return 0.0
            
        recent_data = list(self.battery_buffer)[-window_size:]
        if len(recent_data) < 2:
            return 0.0
            
        start_level = recent_data[0].remaining
        end_level = recent_data[-1].remaining
        time_diff = (recent_data[-1].timestamp - recent_data[0].timestamp).total_seconds()
        
        if time_diff > 0:
            return (start_level - end_level) / time_diff * 60  # %/minute
        return 0.0
        
    def detect_vibration(self, threshold: float = 2.0) -> bool:
        """Detect excessive vibration from IMU data."""
        if len(self.imu_buffer) < 10:
            return False
            
        recent_imu = list(self.imu_buffer)[-10:]
        accelerations = np.array([[data.accel_x, data.accel_y, data.accel_z] 
                                for data in recent_imu])
        
        # Calculate standard deviation of acceleration magnitude
        magnitudes = np.linalg.norm(accelerations, axis=1)
        std_dev = np.std(magnitudes)
        
        return std_dev > threshold