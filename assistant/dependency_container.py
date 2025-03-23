from typing import Dict, Any, Optional, Type
from functools import lru_cache
import logging

class DependencyContainer:
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, callable] = {}
        self._logger = logging.getLogger(__name__)
        
    def register_service(self, name: str, service: Any):
        """Register a service instance with the container"""
        self._services[name] = service
        self._logger.debug(f"Registered service: {name}")
        
    def register_factory(self, name: str, factory: callable):
        """Register a factory function that creates a service"""
        self._factories[name] = factory
        self._logger.debug(f"Registered factory: {name}")
        
    @lru_cache(maxsize=None)
    def get_service(self, name: str) -> Any:
        """Get a service by name, creating it if necessary"""
        if name in self._services:
            return self._services[name]
        if name in self._factories:
            try:
                service = self._factories[name]()
                self._services[name] = service
                self._logger.debug(f"Created service from factory: {name}")
                return service
            except Exception as e:
                self._logger.error(f"Error creating service {name}: {str(e)}")
                raise
        raise KeyError(f"Service {name} not found")
        
    def has_service(self, name: str) -> bool:
        """Check if a service is registered"""
        return name in self._services or name in self._factories
        
    def get_service_names(self) -> list:
        """Get a list of all registered service names"""
        return list(set(list(self._services.keys()) + list(self._factories.keys())))
        
    def clear(self):
        """Clear all registered services and factories"""
        self._services.clear()
        self._factories.clear()
        # Clear the LRU cache
        self.get_service.cache_clear()