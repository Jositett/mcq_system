import asyncio
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime
from .offline_storage import OfflineStorage

class AttendanceSync:
    def __init__(self, api_url: str, storage: OfflineStorage):
        self.api_url = api_url
        self.storage = storage
        self.is_online = True
        self.sync_task: Optional[asyncio.Task] = None
        self._stop_sync = False
    
    async def check_connectivity(self) -> bool:
        """Check if we can reach the API server"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_url}/health")
                self.is_online = response.status_code == 200
                return self.is_online
        except:
            self.is_online = False
            return False
    
    async def submit_attendance(self, data: Dict[str, Any], token: str) -> Dict[str, Any]:
        """Submit attendance, handling offline case"""
        if not await self.check_connectivity():
            # Store offline and return temporary success response
            record_id = self.storage.save_attendance(data)
            return {
                "success": True,
                "message": "Attendance stored offline. Will sync when online.",
                "offline_id": record_id
            }
        
        # We're online, try immediate submission
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {token}"}
                response = await client.post(
                    f"{self.api_url}/attendance/check-in",
                    json=data,
                    headers=headers
                )
                return response.json()
                
        except Exception as e:
            # On any error, store offline
            record_id = self.storage.save_attendance(data)
            return {
                "success": True,
                "message": f"Stored offline due to error: {str(e)}",
                "offline_id": record_id
            }
    
    async def start_sync_loop(self, token: str):
        """Start background sync loop"""
        if self.sync_task and not self.sync_task.done():
            return
        
        self._stop_sync = False
        
        async def sync_loop():
            while not self._stop_sync:
                try:
                    if await self.check_connectivity():
                        await self.sync_pending_records(token)
                except asyncio.CancelledError:
                    break
                except Exception:
                    pass
                    
                try:
                    await asyncio.sleep(300)  # Check every 5 minutes
                except asyncio.CancelledError:
                    break
        
        self.sync_task = asyncio.create_task(sync_loop())
        await asyncio.sleep(0)  # Let the task start
    
    async def sync_pending_records(self, token: str):
        """Sync all pending offline records"""
        if not self.is_online:
            return
            
        pending = self.storage.get_pending_attendance()
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            
            for record in pending:
                try:
                    response = await client.post(
                        f"{self.api_url}/attendance/check-in",
                        json={
                            "student_id": record["student_id"],
                            "date": record["date"],
                            "status": record["status"],
                            "embedding": record["embedding"]
                        },
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        self.storage.mark_synced(record["id"])
                except:
                    continue  # Will try again next sync cycle
        
        # Clean up old synced records
        self.storage.clear_synced_records()
    
    def stop_sync(self):
        """Stop the background sync task"""
        self._stop_sync = True
        if self.sync_task and not self.sync_task.done():
            self.sync_task.cancel()
            # Task will be cleaned up by its own exception handler