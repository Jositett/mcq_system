import unittest
import os
from datetime import datetime
from src.services.offline_storage import OfflineStorage

class TestOfflineStorage(unittest.TestCase):
    def setUp(self):
        self.test_db = "test_offline_storage.db"
        self.storage = OfflineStorage(self.test_db)
    
    def tearDown(self):
        # Close the database connection before removing the file
        self.storage.close()
        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except PermissionError:
                pass  # File might be locked by Windows, will be cleaned up next time
    
    def test_save_attendance(self):
        # Clean database for this test
        self.storage.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.storage = OfflineStorage(self.test_db)
        
        data = {
            "student_id": 1,
            "date": "2025-04-27",
            "status": "present",
            "embedding": "0.1,0.2,0.3"
        }
        
        record_id = self.storage.save_attendance(data)
        self.assertGreater(record_id, 0)
        
        # Verify record was saved
        records = self.storage.get_pending_attendance()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["student_id"], 1)
        self.assertEqual(records[0]["status"], "present")
    
    def test_mark_synced(self):
        # Clean database for this test
        self.storage.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.storage = OfflineStorage(self.test_db)
        
        data = {
            "student_id": 1,
            "date": "2025-04-27",
            "status": "present"
        }
        record_id = self.storage.save_attendance(data)
        
        # Mark as synced
        self.storage.mark_synced(record_id)
        
        # Verify no pending records
        records = self.storage.get_pending_attendance()
        self.assertEqual(len(records), 0)
    
    def test_clear_synced_records(self):
        # Clean database for this test
        self.storage.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.storage = OfflineStorage(self.test_db)
        
        # Save test records
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
        
        id1 = self.storage.save_attendance(data1)
        id2 = self.storage.save_attendance(data2)
        
        # Mark one as synced
        self.storage.mark_synced(id1)
        
        # Clear synced records
        self.storage.clear_synced_records(days_old=0)
        
        # Verify only unsynced record remains
        records = self.storage.get_pending_attendance()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["id"], id2)

if __name__ == "__main__":
    unittest.main()