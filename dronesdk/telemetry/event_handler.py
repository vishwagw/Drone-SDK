from typing import Callable, Dict, List
import asyncio

class EventHandler:
    """Triggers callbacks for specific events."""
    
    def __init__(self):
        self._callbacks: Dict[str, List[Callable]] = {}
        self._monitoring = False
        
    def on(self, event_name: str, callback: Callable):
        """Register a callback for an event."""
        if event_name not in self._callbacks:
            self._callbacks[event_name] = []
        self._callbacks[event_name].append(callback)
        
    def off(self, event_name: str, callback: Callable = None):
        """Remove a callback for an event."""
        if event_name in self._callbacks:
            if callback:
                if callback in self._callbacks[event_name]:
                    self._callbacks[event_name].remove(callback)
            else:
                self._callbacks[event_name].clear()
                
    async def trigger(self, event_name: str, *args, **kwargs):
        """Trigger all callbacks for an event."""
        if event_name in self._callbacks:
            for callback in self._callbacks[event_name]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(*args, **kwargs)
                    else:
                        callback(*args, **kwargs)
                except Exception as e:
                    print(f"Error in event callback for {event_name}: {e}")
                    
    async def start_monitoring(self, telemetry_stream, data_processor):
        """Start monitoring telemetry for events."""
        self._monitoring = True
        
        # Monitor battery level
        asyncio.create_task(self._monitor_battery(telemetry_stream))
        # Monitor GPS signal
        asyncio.create_task(self._monitor_gps_signal(telemetry_stream))
        # Monitor vibration
        asyncio.create_task(self._monitor_vibration(data_processor))
        
    def stop_monitoring(self):
        """Stop monitoring telemetry for events."""
        self._monitoring = False
        
    async def _monitor_battery(self, telemetry_stream):
        """Monitor battery level for low battery events."""
        async for battery_data in telemetry_stream.get_battery():
            if not self._monitoring:
                break
                
            if battery_data.remaining < 20.0:
                await self.trigger("low_battery", battery_data)
            elif battery_data.remaining < 10.0:
                await self.trigger("critical_battery", battery_data)
                
    async def _monitor_gps_signal(self, telemetry_stream):
        """Monitor GPS signal quality."""
        async for gps_data in telemetry_stream.get_gps():
            if not self._monitoring:
                break
                
            if gps_data.hdop > 5.0:  # Poor GPS signal
                await self.trigger("poor_gps_signal", gps_data)
                
    async def _monitor_vibration(self, data_processor):
        """Monitor for excessive vibration."""
        while self._monitoring:
            if data_processor.detect_vibration():
                await self.trigger("excessive_vibration")
            await asyncio.sleep(1)