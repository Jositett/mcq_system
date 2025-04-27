import flet as ft
import cv2
import face_recognition
import numpy as np
import threading
import time
from typing import Callable, Optional
from PIL import Image
import io

class CameraComponent(ft.UserControl):
    def __init__(
        self,
        on_face_detected: Optional[Callable[[bytes], None]] = None,
        width: int = 640,
        height: int = 480
    ):
        super().__init__()
        self.camera_width = width
        self.camera_height = height
        self.on_face_detected = on_face_detected
        self.is_running = False
        self.camera = None
        self.preview = None
        
    def did_mount(self):
        self.start_camera()
        self.update()
        
    def will_unmount(self):
        self.stop_camera()
        
    def build(self):
        self.preview = ft.Image(
            width=self.camera_width,
            height=self.camera_height,
            fit=ft.ImageFit.CONTAIN,
            border_radius=10,
        )
        
        return ft.Container(
            content=self.preview,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=10,
        )
        
    def start_camera(self):
        if not self.is_running:
            self.camera = cv2.VideoCapture(0)
            self.is_running = True
            threading.Thread(target=self._camera_loop, daemon=True).start()
            
    def stop_camera(self):
        self.is_running = False
        if self.camera:
            self.camera.release()
            
    def _camera_loop(self):
        last_detection = 0
        detection_cooldown = 2  # seconds
        
        while self.is_running:
            ret, frame = self.camera.read()
            if not ret:
                continue
                
            # Convert frame for display
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Face detection
            current_time = time.time()
            if current_time - last_detection > detection_cooldown:
                face_locations = face_recognition.face_locations(rgb_frame)
                if face_locations and self.on_face_detected:
                    # Convert frame to bytes for API
                    pil_image = Image.fromarray(rgb_frame)
                    img_byte_arr = io.BytesIO()
                    pil_image.save(img_byte_arr, format='JPEG')
                    img_byte_arr = img_byte_arr.getvalue()
                    
                    # Draw rectangle around face
                    for (top, right, bottom, left) in face_locations:
                        cv2.rectangle(rgb_frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    
                    # Trigger callback
                    self.on_face_detected(img_byte_arr)
                    last_detection = current_time
            
            # Convert frame to image for display
            pil_image = Image.fromarray(rgb_frame)
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Update preview
            self.preview.src_base64 = img_byte_arr
            self.update()
            
            # Control frame rate
            time.sleep(1/30)