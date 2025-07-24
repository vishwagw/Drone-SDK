class SimulatorAdapter:
    """Adapter for testing SDK with simulators."""
    
    def __init__(self, simulator_type: str = "ardupilot_sitl"):
        self.simulator_type = simulator_type
        self.connected = False
        self.armed = False
        self.mode = "STABILIZE"
        self.position = {"lat": 37.7749, "lon": -122.4194, "alt": 0}
        self.battery_level = 100.0
        self.velocity = {"vx": 0, "vy": 0, "vz": 0}
        self.attitude = {"roll": 0, "pitch": 0, "yaw": 0}
        
        # Simulation parameters
        self.noise_level = 0.1
        self.battery_drain_rate = 0.1  # %/minute
        self.last_update = time.time()
        
    async def connect(self, connection_string: str = "tcp:127.0.0.1:5760") -> bool:
        """Connect to simulator."""
        print(f"Connecting to {self.simulator_type} simulator at {connection_string}")
        await asyncio.sleep(1)  # Simulate connection time
        self.connected = True
        print("Simulator connection established")
        return True
        
    async def disconnect(self):
        """Disconnect from simulator."""
        self.connected = False
        self.armed = False
        print("Disconnected from simulator")
        
    async def arm(self) -> bool:
        """Arm the simulated drone."""
        if not self.connected:
            raise Exception("Not connected to simulator")
            
        if self.battery_level < 20:
            raise Exception("Battery too low for arming")
            
        await asyncio.sleep(0.5)
        self.armed = True
        print("Drone armed in simulator")
        return True
        
    async def disarm(self) -> bool:
        """Disarm the simulated drone."""
        self.armed = False
        print("Drone disarmed in simulator")
        return True
        
    async def takeoff(self, altitude: float) -> bool:
        """Simulate takeoff."""
        if not self.armed:
            raise Exception("Drone not armed")
            
        print(f"Taking off to {altitude}m in simulator")
        
        # Simulate gradual altitude increase
        target_alt = altitude
        while self.position["alt"] < target_alt - 0.5:
            self.position["alt"] += 0.5  # Simulate climbing
            await asyncio.sleep(0.5)
        
        self.position["alt"] = target_alt
        self.mode = "GUIDED"
        print(f"Takeoff complete - altitude: {self.position['alt']}m")
        return True
        
    async def land(self) -> bool:
        """Simulate landing."""
        print("Landing in simulator")
        
        # Simulate gradual altitude decrease
        while self.position["alt"] > 0.5:
            self.position["alt"] -= 0.5  # Simulate descending
            await asyncio.sleep(0.5)
        
        self.position["alt"] = 0
        self.mode = "LAND"
        await asyncio.sleep(1)
        await self.disarm()
        print("Landing complete")
        return True
        
    async def goto_location(self, lat: float, lon: float, alt: float):
        """Simulate movement to location."""
        if not self.armed:
            raise Exception("Drone not armed")
        
        print(f"Flying to ({lat}, {lon}, {alt}) in simulator")
        
        start_lat, start_lon, start_alt = self.position["lat"], self.position["lon"], self.position["alt"]
        
        # Simulate gradual movement
        steps = 20
        for i in range(steps + 1):
            self.position["lat"] = start_lat + (lat - start_lat) * (i / steps)
            self.position["lon"] = start_lon + (lon - start_lon) * (i / steps)
            self.position["alt"] = start_alt + (alt - start_alt) * (i / steps)
            await asyncio.sleep(0.5)
        
        print(f"Reached destination: ({self.position['lat']:.6f}, {self.position['lon']:.6f}, {self.position['alt']:.1f})")
        
    async def set_velocity(self, vx: float, vy: float, vz: float):
        """Set the velocity of the simulated drone."""
        self.velocity = {"vx": vx, "vy": vy, "vz": vz}
        print(f"Velocity set to: {self.velocity}")
        
    def get_telemetry(self) -> Dict[str, Any]:
        """Get current telemetry data."""
        return {
            "position": self.position,
            "battery_level": self.battery_level,
            "velocity": self.velocity,
            "attitude": self.attitude,
            "mode": self.mode,
            "armed": self.armed
        }
    
    def _add_noise(self):
        """Add noise to the telemetry data for realism."""
        self.position["lat"] += random.uniform(-self.noise_level, self.noise_level)
        self.position["lon"] += random.uniform(-self.noise_level, self.noise_level)
        self.battery_level -= self.battery_drain_rate * (time.time() - self.last_update) / 60
        self.last_update = time.time()