import flet as ft
import base64
from datetime import datetime
from ..services.offline_storage import OfflineStorage
from ..services.attendance_sync import AttendanceSync
from ..utils.network_state import network_state
import face_recognition
import asyncio
import io
from PIL import Image

class FaceAttendanceView(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.storage = OfflineStorage()
        self.sync_service = AttendanceSync("http://localhost:8000/api", self.storage)
        
        # Camera components
        self.camera = ft.Image(
            width=400,
            height=300,
            fit=ft.ImageFit.CONTAIN,
            border_radius=10
        )
        self.capture_button = ft.ElevatedButton(
            "Capture",
            on_click=self.handle_capture
        )
        
        # Status components
        self.status_text = ft.Text()
        self.connection_status = ft.Text(
            "Online" if network_state.is_online else "Offline",
            color=ft.colors.GREEN if network_state.is_online else ft.colors.RED,
            weight=ft.FontWeight.BOLD
        )
        self.pending_count = ft.Text("0 pending sync")
        
        # Register network state callback
        network_state.add_listener(self.on_network_state_change)
    
    def did_mount(self):
        """Component mounted - start background tasks"""
        asyncio.create_task(self.start_sync())
        asyncio.create_task(self.update_status_loop())
        asyncio.create_task(network_state.start_monitoring("http://localhost:8000/api/health"))
    
    def will_unmount(self):
        """Component will unmount - cleanup"""
        network_state.remove_listener(self.on_network_state_change)
        network_state.stop_monitoring()
        self.sync_service.stop_sync()
    
    async def start_sync(self):
        """Start sync service with current token"""
        token = self.page.client_storage.get("token")
        if token:
            await self.sync_service.start_sync_loop(token)
    
    async def update_status_loop(self):
        """Update UI with pending sync count"""
        while True:
            pending = self.storage.get_pending_attendance()
            self.pending_count.value = f"{len(pending)} pending sync"
            await self.update_async()
            await asyncio.sleep(60)
    
    def on_network_state_change(self, online: bool):
        """Handle network state changes"""
        self.connection_status.value = "Online" if online else "Offline"
        self.connection_status.color = ft.colors.GREEN if online else ft.colors.RED
        asyncio.create_task(self.update_async())
    
    async def process_face_image(self, image_data: bytes) -> str:
        """Process captured face image and extract embedding"""
        # Load image
        image = face_recognition.load_image_file(io.BytesIO(image_data))
        
        # Detect faces
        face_locations = face_recognition.face_locations(image)
        if not face_locations:
            raise ValueError("No face detected in image")
        if len(face_locations) > 1:
            raise ValueError("Multiple faces detected. Please capture only one face.")
            
        # Generate face embedding
        face_encoding = face_recognition.face_encodings(image, face_locations)[0]
        return ",".join(str(x) for x in face_encoding)
    
    async def handle_capture(self, e):
        """Handle face capture and attendance submission"""
        try:
            student_id = self.page.client_storage.get("student_id")
            token = self.page.client_storage.get("token")
            
            if not student_id or not token:
                self.status_text.value = "Please log in again"
                self.status_text.color = ft.colors.RED
                await self.update_async()
                return
            
            # Get camera image data
            image_data = self.camera.get_image_data()
            if not image_data:
                raise ValueError("Failed to capture image")
            
            # Process face and get embedding
            embedding = await self.process_face_image(base64.b64decode(image_data))
            
            # Prepare attendance data
            data = {
                "student_id": student_id,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "status": "present",
                "embedding": embedding
            }
            
            # Try to submit attendance
            result = await self.sync_service.submit_attendance(data, token)
            
            if result.get("offline_id"):
                self.status_text.value = "✓ Face attendance saved offline (will sync when online)"
                self.status_text.color = ft.colors.ORANGE
            else:
                self.status_text.value = "✓ Face attendance marked successfully"
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
                    ft.Text("Face Recognition Attendance", size=20, weight=ft.FontWeight.BOLD),
                    self.connection_status,
                    self.pending_count
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                # Status message
                self.status_text,
                
                # Camera preview
                ft.Container(
                    content=self.camera,
                    bgcolor=ft.colors.BLACK,
                    border_radius=10,
                    padding=10
                ),
                
                # Capture button
                self.capture_button,
                
                # Instructions
                ft.Container(
                    content=ft.Column([
                        ft.Text("Instructions:", weight=ft.FontWeight.BOLD),
                        ft.Text("1. Position your face clearly in the camera"),
                        ft.Text("2. Ensure good lighting"),
                        ft.Text("3. Click 'Capture' to mark attendance"),
                        ft.Text("4. Attendance will be saved offline when not connected")
                    ]),
                    padding=10,
                    bgcolor=ft.colors.BLUE_50,
                    border_radius=5
                )
            ], spacing=20),
            padding=20
        )