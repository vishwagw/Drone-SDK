from typing import Tuple, Optional
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise
import numpy as np

class DataFusion:
    """Combines data from multiple sensors for improved accuracy."""
    
    def __init__(self):
        self.gps_kf = self._create_gps_kalman_filter()
        self.altitude_kf = self._create_altitude_kalman_filter()
        
    def _create_gps_kalman_filter(self) -> KalmanFilter:
        """Create Kalman filter for GPS position estimation."""
        kf = KalmanFilter(dim_x=6, dim_z=2)  # 6 states, 2 measurements
        
        # State vector: [x, y, vx, vy, ax, ay]
        kf.x = np.array([0., 0., 0., 0., 0., 0.])
        
        # State transition matrix (constant acceleration model)
        dt = 0.1  # Time step
        kf.F = np.array([[1, 0, dt, 0, 0.5*dt**2, 0],
                        [0, 1, 0, dt, 0, 0.5*dt**2],
                        [0, 0, 1, 0, dt, 0],
                        [0, 0, 0, 1, 0, dt],
                        [0, 0, 0, 0, 1, 0],
                        [0, 0, 0, 0, 0, 1]])
        
        # Measurement function (observe position only)
        kf.H = np.array([[1, 0, 0, 0, 0, 0],
                        [0, 1, 0, 0, 0, 0]])
        
        # Measurement noise
        kf.R *= 5.0  # GPS noise
        
        # Process noise
        kf.Q = Q_discrete_white_noise(3, dt, 0.1, block_size=2)
        
        # Initial covariance
        kf.P *= 100
        
        return kf
        
    def _create_altitude_kalman_filter(self) -> KalmanFilter:
        """Create Kalman filter for altitude estimation."""
        kf = KalmanFilter(dim_x=3, dim_z=1)  # 3 states, 1 measurement
        
        # State vector: [altitude, velocity, acceleration]
        kf.x = np.array([0., 0., 0.])
        
        dt = 0.1
        kf.F = np.array([[1, dt, 0.5*dt**2],
                        [0, 1, dt],
                        [0, 0, 1]])
        
        kf.H = np.array([[1, 0, 0]])  # Observe altitude only
        kf.R *= 2.0  # Altitude sensor noise
        kf.Q = Q_discrete_white_noise(3, dt, 0.02)
        kf.P *= 10
        
        return kf
        
    def fuse_gps_imu(self, gps_lat: float, gps_lon: float, 
                     imu_accel_x: float, imu_accel_y: float) -> Tuple[float, float]:
        """Fuse GPS and IMU data for improved position estimate."""
        
        # Convert GPS to local coordinates (simplified)
        # In practice, you'd use proper coordinate transformations
        x = gps_lat * 111000  # Approximate meters per degree latitude
        y = gps_lon * 111000 * np.cos(np.radians(gps_lat))
        
        # Predict step
        self.gps_kf.predict()
        
        # Update with GPS measurement
        self.gps_kf.update([x, y])
        
        # Use IMU acceleration as additional input (simplified)
        # In practice, you'd integrate this into the process model
        self.gps_kf.x[4] = imu_accel_x
        self.gps_kf.x[5] = imu_accel_y
        
        # Return filtered position
        filtered_x = self.gps_kf.x[0]
        filtered_y = self.gps_kf.x[1]
        
        # Convert back to GPS coordinates
        filtered_lat = filtered_x / 111000
        filtered_lon = filtered_y / (111000 * np.cos(np.radians(filtered_lat)))
        
        return filtered_lat, filtered_lon
        
    def fuse_altitude_sensors(self, gps_alt: float, baro_alt: float, 
                             lidar_distance: Optional[float] = None) -> float:
        """Fuse altitude data from multiple sensors."""
        
        # Use barometric altitude as primary measurement
        measurement = baro_alt
        
        # If LIDAR is available and reliable, use ground-relative altitude
        if lidar_distance is not None and lidar_distance < 50:  # Within 50m of ground
            # Assume terrain altitude from GPS
            terrain_alt = gps_alt - lidar_distance
            measurement = terrain_alt + lidar_distance
            
        # Predict and update Kalman filter
        self.altitude_kf.predict()
        self.altitude_kf.update([measurement])
        
        return self.altitude_kf.x[0]
        
    def estimate_velocity(self, positions: list) -> Tuple[float, float]:
        """Estimate velocity from position history."""
        if len(positions) < 2:
            return 0.0, 0.0
            
        # Simple finite difference for velocity estimation
        dt = 0.1  # Assume 10Hz updates
        dx = positions[-1][0] - positions[-2][0]
        dy = positions[-1][1] - positions[-2][1]
        
        vx = dx / dt
        vy = dy / dt
        
        return vx, vy