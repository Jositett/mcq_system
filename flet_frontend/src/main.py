import flet as ft
import asyncio
from utils.theme import get_theme
from utils.state_manager import StateManager
from components.navigation import NavigationView
from views.login_view import LoginView
from views.register_view import RegisterView
from services.session_service import SessionService
from services.permissions_service import PermissionsService
from components.error import ErrorDisplay
from views.attendance_view import AttendanceView
from views.face_attendance_view import FaceAttendanceView
from utils.network_state import network_state
from services.offline_storage import OfflineStorage
from services.attendance_sync import AttendanceSync

class MCQApp:
    def __init__(self):
        self.state_manager = StateManager()
        self.session_service = SessionService()
        self.permissions_service = PermissionsService()
        self.storage = OfflineStorage()
        self.sync_service = AttendanceSync("http://localhost:8000/api", self.storage)
        
    async def main(self, page: ft.Page):
        # Configure the page
        page.title = "MCQ System"
        page.theme = get_theme(page.dark_mode)
        page.window_width = 1200
        page.window_height = 800
        page.window_resizable = True
        
        # Initialize network monitoring
        await network_state.start_monitoring("http://localhost:8000/api/health")
        
        # Try to restore previous session
        if await self.session_service.restore_session():
            self.state_manager.set_state("user", self.session_service.user_data)
            self.state_manager.set_state("api_client", self.session_service.api_client)
        
        def route_change(e):
            page.views.clear()
            
            # Check authentication
            user = self.state_manager.get_state("user")
            if not user and page.route not in ["/login", "/register"]:
                page.route = "/login"
                
            if page.route == "/login":
                page.views.append(
                    ft.View(
                        route="/login",
                        controls=[LoginView(page, self.state_manager, self.session_service)]
                    )
                )
            elif page.route == "/register":
                page.views.append(
                    ft.View(
                        route="/register",
                        controls=[RegisterView(page, self.state_manager)]
                    )
                )
            else:
                # Check route permissions
                if user and not self.permissions_service.can_access_route(user["role"], page.route):
                    page.views.append(
                        ft.View(
                            route=page.route,
                            controls=[
                                ErrorDisplay(
                                    "You don't have permission to access this page",
                                    on_retry=lambda _: page.go("/")
                                )
                            ]
                        )
                    )
                else:
                    # Initialize navigation for authenticated routes
                    nav_view = NavigationView(
                        page,
                        self.state_manager,
                        self.session_service,
                        self.permissions_service
                    )
                    page.views.append(
                        ft.View(
                            route="/",
                            controls=[nav_view]
                        )
                    )
            page.update()
        
        def theme_changed(e):
            page.theme = get_theme(page.dark_mode)
            page.update()
            
        def view_pop(e):
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)
            
        page.on_route_change = route_change
        page.on_view_pop = view_pop
        page.on_dark_mode_change = theme_changed
        
        # Initial route
        page.go(page.route)
        
        # Create views
        attendance_view = AttendanceView(page)
        face_attendance_view = FaceAttendanceView(page)
        
        # Add views to page
        page.add(
            ft.Tabs(
                selected_index=0,
                tabs=[
                    ft.Tab(
                        text="Standard Attendance",
                        content=attendance_view
                    ),
                    ft.Tab(
                        text="Face Recognition",
                        content=face_attendance_view
                    )
                ]
            )
        )
        
        # Initialize views
        attendance_view.initialize()
        face_attendance_view.initialize()
        
        await page.update_async()

        def page_cleanup():
            """Cleanup when page is closed"""
            network_state.stop_monitoring()
            
        page.on_close = page_cleanup

if __name__ == "__main__":
    app = MCQApp()
    ft.app(target=app.main, assets_dir="assets", view=ft.WEB_BROWSER)