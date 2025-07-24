import pytest
from dronesdk.telemetry.telemetry_stream import TelemetryStream
from dronesdk.telemetry.data_processor import DataProcessor
from dronesdk.telemetry.event_handler import EventHandler
from unittest.mock import AsyncMock

@pytest.fixture
def mock_connection_manager():
    class MockConnectionManager:
        async def get_message(self, message_type):
            if message_type == "GPS":
                return {'lat': 37.7749, 'lon': -122.4194, 'alt': 10.0, 'hdop': 1.0, 'vdop': 1.0}
            elif message_type == "ATTITUDE":
                return {'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}
            elif message_type == "BATTERY":
                return {'voltage': 12.0, 'current': 5.0, 'remaining': 50.0}
            elif message_type == "IMU":
                return {'accel_x': 0.0, 'accel_y': 0.0, 'accel_z': 9.81, 'gyro_x': 0.0, 'gyro_y': 0.0, 'gyro_z': 0.0}
            return None

    return MockConnectionManager()

@pytest.mark.asyncio
async def test_telemetry_stream(mock_connection_manager):
    telemetry_stream = TelemetryStream(mock_connection_manager)
    
    await telemetry_stream.start()
    
    gps_data = await telemetry_stream.get_gps().__anext__()
    assert gps_data.lat == 37.7749
    assert gps_data.lon == -122.4194
    assert gps_data.alt == 10.0
    
    attitude_data = await telemetry_stream.get_attitude().__anext__()
    assert attitude_data.roll == 0.0
    assert attitude_data.pitch == 0.0
    assert attitude_data.yaw == 0.0
    
    battery_data = await telemetry_stream.get_battery().__anext__()
    assert battery_data.voltage == 12.0
    assert battery_data.current == 5.0
    assert battery_data.remaining == 50.0
    
    imu_data = await telemetry_stream.get_imu().__anext__()
    assert imu_data.accel_z == 9.81
    
    await telemetry_stream.stop()

def test_data_processor():
    data_processor = DataProcessor(buffer_size=5)
    
    gps_data = GPSData(lat=37.7749, lon=-122.4194, alt=10.0, timestamp=datetime.now())
    data_processor.add_gps_data(gps_data)
    
    assert len(data_processor.gps_buffer) == 1
    
    distance = data_processor.calculate_distance_traveled()
    assert distance == 0.0  # Only one point, so distance should be 0
    
    # Add more GPS data and test distance calculation
    gps_data2 = GPSData(lat=37.7750, lon=-122.4195, alt=10.0, timestamp=datetime.now())
    data_processor.add_gps_data(gps_data2)
    
    distance = data_processor.calculate_distance_traveled()
    assert distance > 0.0  # Should calculate some distance

def test_event_handler():
    event_handler = EventHandler()
    event_triggered = False

    async def callback(data):
        nonlocal event_triggered
        event_triggered = True

    event_handler.on("test_event", callback)
    
    # Trigger the event
    await event_handler.trigger("test_event", {"test": "data"})
    
    assert event_triggered is True