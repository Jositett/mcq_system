import unittest
import asyncio
from unittest.mock import Mock, patch
from src.services.offline_storage import OfflineStorage
from src.services.attendance_sync import AttendanceSync
import os
import httpx
import time

class TestAttendanceSync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.test_db = f"test_sync_storage_{time.time_ns()}.db"  # Unique DB file per test
        self.storage = OfflineStorage(self.test_db)
        self.sync_service = AttendanceSync("http://test-api", self.storage)
    
    async def asyncTearDown(self):
        # Stop any running tasks
        if hasattr(self.sync_service, 'sync_task') and self.sync_service.sync_task:
            self.sync_service.stop_sync()
            try:
                await self.sync_service.sync_task
            except asyncio.CancelledError:
                pass
        
        # Close database connection
        self.storage.close()
        
        # Clean up database file
        for _ in range(3):  # Retry a few times in case of Windows file locking
            try:
                if os.path.exists(self.test_db):
                    os.remove(self.test_db)
                break
            except PermissionError:
                await asyncio.sleep(0.1)
    
    async def test_check_connectivity(self):
        # Mock successful connection
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value.status_code = 200
            is_online = await self.sync_service.check_connectivity()
            self.assertTrue(is_online)
            self.assertTrue(self.sync_service.is_online)

        # Mock failed connection
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = httpx.ConnectError("Connection failed")
            is_online = await self.sync_service.check_connectivity()
            self.assertFalse(is_online)
            self.assertFalse(self.sync_service.is_online)
    
    async def test_submit_attendance_online(self):
        # Force online mode first
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value.status_code = 200
            await self.sync_service.check_connectivity()
        
        # Mock successful online submission
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"success": True}
            
            data = {
                "student_id": 1,
                "date": "2025-04-27",
                "status": "present"
            }
            
            result = await self.sync_service.submit_attendance(data, "test-token")
            self.assertTrue(result["success"])
            
            # Verify no offline storage was used
            records = self.storage.get_pending_attendance()
            self.assertEqual(len(records), 0)
    
    async def test_submit_attendance_offline(self):
        # Force offline mode
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = httpx.ConnectError("Connection failed")
            await self.sync_service.check_connectivity()
            
        data = {
            "student_id": 1,
            "date": "2025-04-27",
            "status": "present"
        }
        
        result = await self.sync_service.submit_attendance(data, "test-token")
        self.assertTrue(result["success"])
        self.assertIn("offline_id", result)
        
        # Verify record was stored offline
        records = self.storage.get_pending_attendance()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["student_id"], 1)
    
    async def test_sync_pending_records(self):
        # Add some offline records
        data1 = {
            "student_id": 1,
            "date": "2025-04-27",
            "status": "present"
        }
        data2 = {
            "student_id": 2,
            "date": "2025-04-27",
            "status": "present"
        }
        
        self.storage.save_attendance(data1)
        self.storage.save_attendance(data2)
        
        # Mock successful sync
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value.status_code = 200
            await self.sync_service.sync_pending_records("test-token")
            
            # Verify all records were synced
            records = self.storage.get_pending_attendance()
            self.assertEqual(len(records), 0)
            
            # Verify API was called for each record
            self.assertEqual(mock_post.call_count, 2)
    
    async def test_start_stop_sync_loop(self):
        # Start sync loop
        await self.sync_service.start_sync_loop("test-token")
        self.assertIsNotNone(self.sync_service.sync_task)
        self.assertFalse(self.sync_service.sync_task.done())
        
        # Let it run briefly
        await asyncio.sleep(0.1)
        
        # Stop sync loop and verify it's cancelled
        self.sync_service.stop_sync()
        for _ in range(5):  # Wait for task to be cancelled with timeout
            if self.sync_service.sync_task.cancelled():
                break
            await asyncio.sleep(0.1)
        
        self.assertTrue(self.sync_service.sync_task.cancelled())

if __name__ == "__main__":
    unittest.main()