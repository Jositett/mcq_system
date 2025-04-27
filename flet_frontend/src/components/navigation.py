import flet as ft
from utils.state_manager import StateManager
from services.session_service import SessionService
from services.permissions_service import PermissionsService
from views.home_view import HomeView
from views.tests_view import TestsView
from views.test_view import TestView
from views.attendance_view import AttendanceView
from views.profile_view import ProfileView
from views.results_view import TestResultsView
from views.analytics_view import AnalyticsView
from views.users_view import UsersView
from views.reports_view import ReportsView
import re

class NavigationView(ft.UserControl):
    def __init__(
        self,
        page: ft.Page,
        state_manager: StateManager,
        session_service: SessionService,
        permissions_service: PermissionsService
    ):
        super().__init__()
        self.page = page
        self.state_manager = state_manager
        self.session_service = session_service
        self.permissions_service = permissions_service
        self.current_route = "/"
        self.user_data = self.state_manager.get_state("user", {})
        
    def build(self):
        def route_change(e):
            self.current_route = e.data
            self._update_view()
            self.update()
        
        self.page.on_route_change = route_change
        
        # Build navigation items based on user role
        nav_items = self._get_navigation_items()
        
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            destinations=nav_items,
            on_change=self.nav_change,
            visible=True,
        )
        
        # User menu items based on permissions
        menu_items = [
            ft.PopupMenuItem(
                text="Profile",
                icon=ft.icons.PERSON,
                on_click=lambda _: self.page.go("/profile")
            ),
        ]
        
        # Add Results menu item if user can view results
        if self.permissions_service.has_permission(
            self.user_data.get("role", ""), "view_results"
        ) or self.permissions_service.has_permission(
            self.user_data.get("role", ""), "view_own_results"
        ):
            menu_items.append(
                ft.PopupMenuItem(
                    text="Test Results",
                    icon=ft.icons.ASSESSMENT,
                    on_click=lambda _: self.page.go("/results")
                )
            )
        
        # Add logout item
        menu_items.append(
            ft.PopupMenuItem(
                text="Logout",
                icon=ft.icons.LOGOUT,
                on_click=self.handle_logout
            )
        )
        
        # User menu
        user_menu = ft.PopupMenuButton(
            items=menu_items,
            content=ft.Row(
                [
                    ft.CircleAvatar(
                        content=ft.Text(
                            self.user_data.get("full_name", "U")[0].upper(),
                            size=16,
                            weight=ft.FontWeight.BOLD
                        ),
                    ),
                    ft.Text(self.user_data.get("full_name", "User")),
                    ft.Icon(ft.icons.ARROW_DROP_DOWN),
                ],
                spacing=5,
            ),
        )
        
        # Role indicator
        role_badge = ft.Container(
            content=ft.Text(
                self.user_data.get("role", "").title(),
                size=12,
                color=ft.colors.WHITE,
            ),
            bgcolor=self._get_role_color(self.user_data.get("role", "")),
            padding=ft.padding.all(5),
            border_radius=ft.border_radius.all(15),
        )
        
        # Top app bar
        app_bar = ft.AppBar(
            title=ft.Text("MCQ System"),
            center_title=False,
            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=[
                role_badge,
                user_menu,
            ],
        )
        
        # Main content area
        self.content_area = ft.Container(
            content=HomeView(self.page, self.state_manager),
            expand=True,
        )
        
        return ft.Column(
            [
                app_bar,
                ft.Row(
                    [
                        self.nav_rail,
                        ft.VerticalDivider(width=1, visible=True),
                        self.content_area,
                    ],
                    expand=True,
                ),
            ],
            expand=True,
        )
    
    def _get_navigation_items(self) -> list:
        """Build navigation items based on user permissions."""
        items = [
            ft.NavigationRailDestination(
                icon=ft.icons.HOME_OUTLINED,
                selected_icon=ft.icons.HOME,
                label="Home"
            ),
        ]
        
        role = self.user_data.get("role", "")
        
        # Tests navigation
        if self.permissions_service.has_permission(role, "view_tests") or \
           self.permissions_service.has_permission(role, "view_available_tests"):
            items.append(
                ft.NavigationRailDestination(
                    icon=ft.icons.QUIZ_OUTLINED,
                    selected_icon=ft.icons.QUIZ,
                    label="Tests"
                )
            )
        
        # Attendance navigation
        if self.permissions_service.has_permission(role, "view_attendance") or \
           self.permissions_service.has_permission(role, "mark_attendance"):
            items.append(
                ft.NavigationRailDestination(
                    icon=ft.icons.PEOPLE_OUTLINED,
                    selected_icon=ft.icons.PEOPLE,
                    label="Attendance"
                )
            )
        
        # Analytics navigation (instructors and admins only)
        if self.permissions_service.has_permission(role, "view_analytics"):
            items.append(
                ft.NavigationRailDestination(
                    icon=ft.icons.ANALYTICS_OUTLINED,
                    selected_icon=ft.icons.ANALYTICS,
                    label="Analytics"
                )
            )
        
        # Users management (admin only)
        if self.permissions_service.has_permission(role, "manage_users"):
            items.append(
                ft.NavigationRailDestination(
                    icon=ft.icons.ADMIN_PANEL_SETTINGS_OUTLINED,
                    selected_icon=ft.icons.ADMIN_PANEL_SETTINGS,
                    label="Users"
                )
            )
        
        # Reports (instructors and admins)
        if self.permissions_service.has_permission(role, "generate_reports"):
            items.append(
                ft.NavigationRailDestination(
                    icon=ft.icons.SUMMARIZE_OUTLINED,
                    selected_icon=ft.icons.SUMMARIZE,
                    label="Reports"
                )
            )
            
        return items
    
    def _get_role_color(self, role: str) -> str:
        """Get color for role badge."""
        return {
            "admin": ft.colors.RED,
            "instructor": ft.colors.BLUE,
            "student": ft.colors.GREEN,
        }.get(role.lower(), ft.colors.GREY)
    
    async def handle_logout(self, e):
        try:
            # End the session
            self.session_service.end_session()
            
            # Clear application state
            self.state_manager.set_state("user", None)
            self.state_manager.set_state("api_client", None)
            
            # Navigate to login
            self.page.go("/login")
        except Exception as ex:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Error during logout"))
            )
    
    def nav_change(self, e):
        # Map index to routes based on visible navigation items
        visible_routes = []
        role = self.user_data.get("role", "")
        
        # Always include home
        visible_routes.append("/")
        
        # Add routes based on permissions
        if self.permissions_service.has_permission(role, "view_tests") or \
           self.permissions_service.has_permission(role, "view_available_tests"):
            visible_routes.append("/tests")
            
        if self.permissions_service.has_permission(role, "view_attendance") or \
           self.permissions_service.has_permission(role, "mark_attendance"):
            visible_routes.append("/attendance")
            
        if self.permissions_service.has_permission(role, "view_analytics"):
            visible_routes.append("/analytics")
            
        if self.permissions_service.has_permission(role, "manage_users"):
            visible_routes.append("/users")
            
        if self.permissions_service.has_permission(role, "generate_reports"):
            visible_routes.append("/reports")
            
        self.page.go(visible_routes[e.control.selected_index])
        
    def _update_view(self):
        # Check for test-taking route
        test_match = re.match(r"/test/([^/]+)", self.current_route)
        if test_match:
            test_id = test_match.group(1)
            self.nav_rail.visible = False
            self.content_area.content = TestView(
                self.page,
                self.state_manager,
                test_id,
                self.permissions_service
            )
            return
            
        # Regular routes
        route_views = {
            "/": HomeView,
            "/tests": TestsView,
            "/attendance": AttendanceView,
            "/profile": ProfileView,
            "/results": TestResultsView,
            "/analytics": AnalyticsView,
            "/users": UsersView,
            "/reports": ReportsView,
        }
        
        self.nav_rail.visible = True
        view_class = route_views.get(self.current_route, HomeView)
        
        # Create view instance with permissions service
        view_instance = view_class(
            self.page,
            self.state_manager,
            permissions_service=self.permissions_service
        )
        self.content_area.content = view_instance
        
        # Update navigation rail selected index
        try:
            visible_routes = []
            role = self.user_data.get("role", "")
            
            visible_routes.append("/")
            if self.permissions_service.has_permission(role, "view_tests") or \
               self.permissions_service.has_permission(role, "view_available_tests"):
                visible_routes.append("/tests")
            if self.permissions_service.has_permission(role, "view_attendance") or \
               self.permissions_service.has_permission(role, "mark_attendance"):
                visible_routes.append("/attendance")
            if self.permissions_service.has_permission(role, "view_analytics"):
                visible_routes.append("/analytics")
            if self.permissions_service.has_permission(role, "manage_users"):
                visible_routes.append("/users")
            if self.permissions_service.has_permission(role, "generate_reports"):
                visible_routes.append("/reports")
                
            self.nav_rail.selected_index = visible_routes.index(self.current_route)
        except ValueError:
            self.nav_rail.selected_index = 0
            
        self.content_area.update()