import flet as ft
from datetime import datetime
from ..services.offline_storage import OfflineStorage
from ..services.attendance_sync import AttendanceSync
import asyncio

class AttendanceView(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.storage = OfflineStorage()
        self.sync_service = AttendanceSync("http://localhost:8000/api", self.storage)
        
        # UI components
        self.status_text = ft.Text()
        self.connection_status = ft.Text(
            "Online",
            color=ft.colors.GREEN,
            weight=ft.FontWeight.BOLD
        )
        self.pending_count = ft.Text("0 pending sync")
        
    def initialize(self):
        """Start background tasks"""
        asyncio.create_task(self.start_sync())
        asyncio.create_task(self.update_status_loop())
    
    async def start_sync(self):
        """Start sync service with current token"""
        token = self.page.client_storage.get("token")
        if token:
            await self.sync_service.start_sync_loop(token)
    
    async def update_status_loop(self):
        """Update UI with connection status and pending count"""
        while True:
            is_online = await self.sync_service.check_connectivity()
            self.connection_status.value = "Online" if is_online else "Offline"
            self.connection_status.color = ft.colors.GREEN if is_online else ft.colors.RED
            
            pending = self.storage.get_pending_attendance()
            self.pending_count.value = f"{len(pending)} pending sync"
            
            await self.update_async()
            await asyncio.sleep(60)  # Update every minute
    
    async def handle_check_in(self, e):
        """Handle attendance check-in with offline support"""
        try:
            student_id = self.page.client_storage.get("student_id")
            token = self.page.client_storage.get("token")
            
            if not student_id or not token:
                self.status_text.value = "Please log in again"
                self.status_text.color = ft.colors.RED
                await self.update_async()
                return
            
            # Prepare attendance data
            data = {
                "student_id": student_id,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "status": "present"
            }
            
            # Try to submit attendance
            result = await self.sync_service.submit_attendance(data, token)
            
            if result.get("offline_id"):
                self.status_text.value = "✓ Attendance saved offline (will sync when online)"
                self.status_text.color = ft.colors.ORANGE
            else:
                self.status_text.value = "✓ Attendance marked successfully"
                self.status_text.color = ft.colors.GREEN
                
        except Exception as e:
            self.status_text.value = f"Error: {str(e)}"
            self.status_text.color = ft.colors.RED
            
        await self.update_async()
    
    def build(self):
        return ft.Container(
            content=ft.Column([
                # Header with connection status
                ft.Row([
                    ft.Text("Attendance", size=20, weight=ft.FontWeight.BOLD),
                    self.connection_status,
                    self.pending_count
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                # Status message
                self.status_text,
                
                # Check-in button
                ft.ElevatedButton(
                    "Mark Attendance",
                    on_click=self.handle_check_in,
                    style=ft.ButtonStyle(
                        color={
                            ft.MaterialState.DEFAULT: ft.colors.WHITE,
                            ft.MaterialState.HOVERED: ft.colors.WHITE,
                        },
                        bgcolor={
                            ft.MaterialState.DEFAULT: ft.colors.BLUE,
                            ft.MaterialState.HOVERED: ft.colors.BLUE_700,
                        }
                    )
                ),
                
                # Instructions
                ft.Container(
                    content=ft.Column([
                        ft.Text("Note:", weight=ft.FontWeight.BOLD),
                        ft.Text("• Attendance will be saved offline if you're not connected"),
                        ft.Text("• Pending records will sync automatically when online"),
                        ft.Text("• Check the connection status above")
                    ]),
                    padding=10,
                    bgcolor=ft.colors.BLUE_50,
                    border_radius=5
                )
            ], spacing=20),
            padding=20
        )