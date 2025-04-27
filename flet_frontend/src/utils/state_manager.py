from typing import Any, Callable, Dict, List

class StateManager:
    def __init__(self):
        self._state = {}
        self._subscribers: Dict[str, List[Callable]] = {}
        
    def set_state(self, key: str, value: Any):
        self._state[key] = value
        if key in self._subscribers:
            for callback in self._subscribers[key]:
                callback(value)
                
    def get_state(self, key: str, default: Any = None) -> Any:
        return self._state.get(key, default)
    
    def subscribe(self, key: str, callback: Callable):
        if key not in self._subscribers:
            self._subscribers[key] = []
        self._subscribers[key].append(callback)
        
    def unsubscribe(self, key: str, callback: Callable):
        if key in self._subscribers and callback in self._subscribers[key]:
            self._subscribers[key].remove(callback)