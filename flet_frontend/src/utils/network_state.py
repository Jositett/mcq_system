import asyncio
from typing import Callable, List
import httpx

class NetworkState:
    def __init__(self):
        self._online = True
        self._listeners: List[Callable[[bool], None]] = []
        self._check_task = None
        self._stop_monitoring = False
    
    @property
    def is_online(self) -> bool:
        return self._online
    
    def add_listener(self, callback: Callable[[bool], None]):
        """Add a callback to be notified of network state changes"""
        if callback not in self._listeners:
            self._listeners.append(callback)
    
    def remove_listener(self, callback: Callable[[bool], None]):
        """Remove a network state change callback"""
        if callback in self._listeners:
            self._listeners.remove(callback)
    
    def _notify_listeners(self, online: bool):
        """Notify all listeners of network state change"""
        for callback in self._listeners:
            try:
                callback(online)
            except:
                continue
    
    async def check_connection(self, url: str) -> bool:
        """Check if we can reach a given URL"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5.0)
                online = response.status_code == 200
                if online != self._online:
                    self._online = online
                    self._notify_listeners(online)
                return online
        except:
            if self._online:
                self._online = False
                self._notify_listeners(False)
            return False
    
    async def start_monitoring(self, url: str, interval: float = 30.0):
        """Start periodic connection monitoring"""
        if self._check_task and not self._check_task.done():
            return
        
        self._stop_monitoring = False
        
        async def monitor_loop():
            while not self._stop_monitoring:
                try:
                    await self.check_connection(url)
                except asyncio.CancelledError:
                    break
                except:
                    pass
                    
                try:
                    await asyncio.sleep(interval)
                except asyncio.CancelledError:
                    break
        
        self._check_task = asyncio.create_task(monitor_loop())
        await asyncio.sleep(0)  # Let the task start
    
    def stop_monitoring(self):
        """Stop periodic connection monitoring"""
        if not self._check_task:
            return
            
        self._stop_monitoring = True
        if not self._check_task.done():
            self._check_task.cancel()
            # Don't set _check_task to None - let the test verify cancellation

# Global instance
network_state = NetworkState()