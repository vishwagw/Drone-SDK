from typing import Dict, Any, List
from abc import ABC, abstractmethod

class Plugin(ABC):
    @abstractmethod
    def initialize(self, drone_instance):
        pass
        
    @abstractmethod
    def get_name(self) -> str:
        pass
        
    @abstractmethod
    def get_version(self) -> str:
        pass

class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.drone_instance = None
        
    def set_drone_instance(self, drone):
        self.drone_instance = drone
        
    def load_plugin(self, plugin_path: str) -> bool:
        try:
            module = importlib.import_module(plugin_path)
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, Plugin) and 
                    obj != Plugin):
                    plugin_instance = obj()
                    plugin_name = plugin_instance.get_name()
                    if self.drone_instance:
                        plugin_instance.initialize(self.drone_instance)
                    self.plugins[plugin_name] = plugin_instance
                    print(f"Loaded plugin: {plugin_name} v{plugin_instance.get_version()}")
                    return True
        except Exception as e:
            print(f"Failed to load plugin {plugin_path}: {e}")
        return False
        
    def get_plugin(self, name: str) -> Plugin:
        return self.plugins.get(name)
        
    def list_plugins(self) -> List[str]:
        return list(self.plugins.keys())
        
    def unload_plugin(self, name: str) -> bool:
        if name in self.plugins:
            del self.plugins[name]
            return True
        return False