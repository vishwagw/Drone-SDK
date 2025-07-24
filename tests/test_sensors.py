import unittest
from dronesdk.sensors.camera_interface import CameraInterface
from dronesdk.sensors.sensor_drivers import LIDARSensor, UltrasonicSensor
from dronesdk.sensors.data_fusion import DataFusion

class TestCameraInterface(unittest.TestCase):
    def setUp(self):
        self.camera = CameraInterface(camera_id=0)
        self.camera.initialize()

    def test_capture_frame(self):
        frame = self.camera.capture_frame()
        self.assertIsNotNone(frame)

    def test_detect_objects(self):
        frame = self.camera.capture_frame()
        objects = self.camera.detect_objects(frame)
        self.assertIsInstance(objects, list)

    def tearDown(self):
        self.camera.close()

class TestLIDARSensor(unittest.TestCase):
    def setUp(self):
        self.lidar = LIDARSensor(port="/dev/ttyUSB1", baudrate=115200)
        self.lidar.connect()

    def test_read_distance(self):
        distance = self.lidar.read_distance()
        self.assertIsInstance(distance, float)

    def tearDown(self):
        self.lidar.disconnect()

class TestUltrasonicSensor(unittest.TestCase):
    def setUp(self):
        self.ultrasonic = UltrasonicSensor(trigger_pin=18, echo_pin=24)

    def test_read_distance(self):
        distance = self.ultrasonic.read_distance()
        self.assertIsInstance(distance, float)

class TestDataFusion(unittest.TestCase):
    def setUp(self):
        self.data_fusion = DataFusion()

    def test_fuse_gps_imu(self):
        lat, lon = self.data_fusion.fuse_gps_imu(37.7749, -122.4194, 0.1, 0.1)
        self.assertIsInstance(lat, float)
        self.assertIsInstance(lon, float)

    def test_fuse_altitude_sensors(self):
        altitude = self.data_fusion.fuse_altitude_sensors(100.0, 95.0)
        self.assertIsInstance(altitude, float)

if __name__ == '__main__':
    unittest.main()