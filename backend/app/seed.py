from app.db.session import SessionLocal
from app.db import models
from app.core import security

def seed():
    db = SessionLocal()
    # Create admin user if not exists
    if not db.query(models.User).filter(models.User.username == "admin").first():
        admin = models.User(
            username="admin",
            email="admin@example.com",
            full_name="Admin User",
            hashed_password=security.get_password_hash("adminpass"),
            role="admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print("Admin user created.")
    else:
        print("Admin user already exists.")
    db.close()

if __name__ == "__main__":
    seed()
