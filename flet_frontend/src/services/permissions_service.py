from typing import Dict, List, Set

class PermissionsService:
    def __init__(self):
        self._role_permissions: Dict[str, Set[str]] = {
            "admin": {
                "view_tests",
                "create_test",
                "edit_test",
                "delete_test",
                "view_results",
                "view_attendance",
                "manage_users",
                "view_analytics",
                "generate_reports",
            },
            "instructor": {
                "view_tests",
                "create_test",
                "edit_test",
                "delete_test",
                "view_results",
                "view_attendance",
                "view_analytics",
            },
            "student": {
                "view_available_tests",
                "take_test",
                "view_own_results",
                "mark_attendance",
            }
        }
        
        self._route_permissions: Dict[str, Set[str]] = {
            "/": {"view_tests", "view_available_tests"},  # Home route - all authenticated users
            "/tests": {"view_tests", "view_available_tests"},
            "/test/create": {"create_test"},
            "/test/edit": {"edit_test"},
            "/attendance": {"view_attendance", "mark_attendance"},
            "/results": {"view_results", "view_own_results"},
            "/analytics": {"view_analytics"},
            "/users": {"manage_users"},
            "/reports": {"generate_reports"},
        }
        
        # Views that should be hidden from navigation if user doesn't have permission
        self._nav_items: Dict[str, str] = {
            "Tests": "view_tests",
            "Attendance": "view_attendance",
            "Results": "view_results",
            "Analytics": "view_analytics",
            "Users": "manage_users",
            "Reports": "generate_reports",
        }
    
    def get_permitted_routes(self, role: str) -> Set[str]:
        """Get all routes that the user role has permission to access."""
        user_permissions = self._role_permissions.get(role, set())
        permitted_routes = set()
        
        for route, required_permissions in self._route_permissions.items():
            if any(perm in user_permissions for perm in required_permissions):
                permitted_routes.add(route)
                
        return permitted_routes
    
    def can_access_route(self, role: str, route: str) -> bool:
        """Check if the user role can access a specific route."""
        if route in ["/login", "/register"]:
            return True
            
        user_permissions = self._role_permissions.get(role, set())
        required_permissions = self._route_permissions.get(route, set())
        
        return any(perm in user_permissions for perm in required_permissions)
    
    def get_visible_nav_items(self, role: str) -> List[str]:
        """Get navigation items that should be visible to the user role."""
        user_permissions = self._role_permissions.get(role, set())
        return [
            item for item, required_perm in self._nav_items.items()
            if required_perm in user_permissions
        ]
    
    def has_permission(self, role: str, permission: str) -> bool:
        """Check if the user role has a specific permission."""
        user_permissions = self._role_permissions.get(role, set())
        return permission in user_permissions