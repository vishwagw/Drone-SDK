from typing import Dict, Any, AsyncGenerator
from dataclasses import dataclass
from datetime import datetime
import asyncio
import math

@dataclass
class GPSData:
    lat: float
    lon: float
    alt: float
    timestamp: datetime
    hdop: float = 0.0
    vdop: float = 0.0

@dataclass
class AttitudeData:
    roll: float
    pitch: float
    yaw: float
    timestamp: datetime

@dataclass
class BatteryData:
    voltage: float
    current: float
    remaining: float
    timestamp: datetime

@dataclass
class IMUData:
    accel_x: float
    accel_y: float
    accel_z: float
    gyro_x: float
    gyro_y: float
    gyro_z: float
    timestamp: datetime

class TelemetryStream:
    """Handles real-time data collection and processing from the drone."""
    
    def __init__(self, connection_manager):
        self.connection_manager = connection_manager
        self._streams = {}
        self._running = False
        
    async def start(self):
        """Start telemetry data collection."""
        self._running = True
        
    async def stop(self):
        """Stop telemetry data collection."""
        self._running = False
        
    async def get_gps(self) -> AsyncGenerator[GPSData, None]:
        """Stream GPS data."""
        while self._running:
            try:
                raw_data = await self.connection_manager.get_message("GPS")
                if raw_data:
                    gps_data = GPSData(
                        lat=raw_data.get('lat', 0.0),
                        lon=raw_data.get('lon', 0.0),
                        alt=raw_data.get('alt', 0.0),
                        timestamp=datetime.now(),
                        hdop=raw_data.get('hdop', 0.0),
                        vdop=raw_data.get('vdop', 0.0)
                    )
                    yield gps_data
                await asyncio.sleep(0.1)  # 10Hz update rate
            except Exception as e:
                print(f"GPS telemetry error: {e}")
                await asyncio.sleep(1)
                
    async def get_attitude(self) -> AsyncGenerator[AttitudeData, None]:
        """Stream attitude data."""
        while self._running:
            try:
                raw_data = await self.connection_manager.get_message("ATTITUDE")
                if raw_data:
                    attitude_data = AttitudeData(
                        roll=raw_data.get('roll', 0.0),
                        pitch=raw_data.get('pitch', 0.0),
                        yaw=raw_data.get('yaw', 0.0),
                        timestamp=datetime.now()
                    )
                    yield attitude_data
                await asyncio.sleep(0.02)  # 50Hz update rate
            except Exception as e:
                print(f"Attitude telemetry error: {e}")
                await asyncio.sleep(1)
                
    async def get_battery(self) -> AsyncGenerator[BatteryData, None]:
        """Stream battery data."""
        while self._running:
            try:
                raw_data = await self.connection_manager.get_message("BATTERY")
                if raw_data:
                    battery_data = BatteryData(
                        voltage=raw_data.get('voltage', 0.0),
                        current=raw_data.get('current', 0.0),
                        remaining=raw_data.get('remaining', 0.0),
                        timestamp=datetime.now()
                    )
                    yield battery_data
                await asyncio.sleep(0.5)  # 2Hz update rate
            except Exception as e:
                print(f"Battery telemetry error: {e}")
                await asyncio.sleep(1)
                
    async def get_imu(self) -> AsyncGenerator[IMUData, None]:
        """Stream IMU data."""
        while self._running:
            try:
                raw_data = await self.connection_manager.get_message("IMU")
                if raw_data:
                    imu_data = IMUData(
                        accel_x=raw_data.get('accel_x', 0.0),
                        accel_y=raw_data.get('accel_y', 0.0),
                        accel_z=raw_data.get('accel_z', 0.0),
                        gyro_x=raw_data.get('gyro_x', 0.0),
                        gyro_y=raw_data.get('gyro_y', 0.0),
                        gyro_z=raw_data.get('gyro_z', 0.0),
                        timestamp=datetime.now()
                    )
                    yield imu_data
                await asyncio.sleep(0.01)  # 100Hz update rate
            except Exception as e:
                print(f"IMU telemetry error: {e}")
                await asyncio.sleep(1)