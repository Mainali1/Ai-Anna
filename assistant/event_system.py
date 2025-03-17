from typing import Dict, List, Callable
from collections import defaultdict

class EventSystem:
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        
    def subscribe(self, event_type: str, handler: Callable):
        self._handlers[event_type].append(handler)
        
    def unsubscribe(self, event_type: str, handler: Callable):
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)
            
    def emit(self, event_type: str, data: dict = None):
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                handler(data or {})