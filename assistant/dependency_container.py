from typing import Dict, Any
from functools import lru_cache

class DependencyContainer:
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, callable] = {}
        
    def register_service(self, name: str, service: Any):
        self._services[name] = service
        
    def register_factory(self, name: str, factory: callable):
        self._factories[name] = factory
        
    @lru_cache(maxsize=None)
    def get_service(self, name: str) -> Any:
        if name in self._services:
            return self._services[name]
        if name in self._factories:
            service = self._factories[name]()
            self._services[name] = service
            return service
        raise KeyError(f"Service {name} not found")