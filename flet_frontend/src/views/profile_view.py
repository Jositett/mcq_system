import flet as ft
from utils.state_manager import StateManager

class ProfileView(ft.UserControl):
    def __init__(self, page: ft.Page, state_manager: StateManager):
        super().__init__()
        self.page = page
        self.state_manager = state_manager
        self.api_client = self.state_manager.get_state("api_client")
        self.user_data = self.state_manager.get_state("user")
        
    def build(self):
        # Profile fields
        self.name_field = ft.TextField(
            label="Full Name",
            value=self.user_data.get("full_name", ""),
            width=300
        )
        
        self.email_field = ft.TextField(
            label="Email",
            value=self.user_data.get("email", ""),
            width=300
        )
        
        self.student_id_field = ft.TextField(
            label="Student ID",
            value=self.user_data.get("student_id", ""),
            width=300,
            disabled=True  # Student ID should not be editable
        )
        
        # Password change fields
        self.current_password = ft.TextField(
            label="Current Password",
            password=True,
            can_reveal_password=True,
            width=300
        )
        
        self.new_password = ft.TextField(
            label="New Password",
            password=True,
            can_reveal_password=True,
            width=300
        )
        
        self.confirm_password = ft.TextField(
            label="Confirm New Password",
            password=True,
            can_reveal_password=True,
            width=300
        )
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Profile Settings", size=32, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Text("Personal Information", size=20, weight=ft.FontWeight.W_500),
                    self.name_field,
                    self.email_field,
                    self.student_id_field,
                    ft.ElevatedButton(
                        "Update Profile",
                        icon=ft.icons.SAVE,
                        on_click=self.update_profile
                    ),
                    ft.Divider(height=40),
                    ft.Text("Change Password", size=20, weight=ft.FontWeight.W_500),
                    self.current_password,
                    self.new_password,
                    self.confirm_password,
                    ft.ElevatedButton(
                        "Change Password",
                        icon=ft.icons.LOCK_RESET,
                        on_click=self.change_password
                    ),
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=40,
        )
    
    async def update_profile(self, e):
        try:
            updated_data = {
                "full_name": self.name_field.value,
                "email": self.email_field.value,
            }
            
            result = await self.api_client.update_profile(updated_data)
            self.state_manager.set_state("user", result)
            
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Profile updated successfully"))
            )
        except Exception as ex:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Error updating profile"))
            )
    
    async def change_password(self, e):
        if self.new_password.value != self.confirm_password.value:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("New passwords don't match"))
            )
            return
            
        try:
            await self.api_client.change_password(
                self.current_password.value,
                self.new_password.value
            )
            
            # Clear password fields
            self.current_password.value = ""
            self.new_password.value = ""
            self.confirm_password.value = ""
            self.update()
            
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Password changed successfully"))
            )
        except Exception as ex:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Error changing password"))
            )