from datetime import datetime
import json
import os
import sqlite3
from typing import List, Dict, Any
import asyncio
from pathlib import Path

class OfflineStorage:
    def __init__(self, db_path: str = "offline_storage.db"):
        self.db_path = db_path
        self._conn = None
        self._init_db()
    
    def _get_connection(self):
        """Get a SQLite connection, creating a new one if needed"""
        if not self._conn:
            self._conn = sqlite3.connect(self.db_path)
        return self._conn
    
    def close(self):
        """Close the database connection"""
        if self._conn:
            self._conn.close()
            self._conn = None
    
    def _init_db(self):
        """Initialize SQLite database for offline storage"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pending_attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            embedding TEXT,
            created_at TEXT NOT NULL,
            synced INTEGER DEFAULT 0
        )
        """)
        
        conn.commit()
    
    def save_attendance(self, data: Dict[str, Any]) -> int:
        """Save attendance check-in for offline storage"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO pending_attendance 
        (student_id, date, status, embedding, created_at)
        VALUES (?, ?, ?, ?, ?)
        """, (
            data["student_id"],
            data["date"],
            data["status"],
            data.get("embedding"),
            datetime.now().isoformat()
        ))
        
        record_id = cursor.lastrowid
        conn.commit()
        return record_id
    
    def get_pending_attendance(self) -> List[Dict[str, Any]]:
        """Get all pending (unsynced) attendance records"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM pending_attendance WHERE synced = 0")
        records = cursor.fetchall()
        
        # Convert to list of dicts
        columns = ["id", "student_id", "date", "status", "embedding", "created_at", "synced"]
        result = [dict(zip(columns, record)) for record in records]
        
        return result
    
    def mark_synced(self, record_id: int):
        """Mark an attendance record as synced"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE pending_attendance SET synced = 1 WHERE id = ?",
            (record_id,)
        )
        
        conn.commit()
    
    def clear_synced_records(self, days_old: int = 30):
        """Clear old synced records to prevent DB bloat"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            DELETE FROM pending_attendance 
            WHERE synced = 1 
            AND datetime(created_at) < datetime('now', '-' || ? || ' days')
            """,
            (days_old,)
        )
        
        conn.commit()