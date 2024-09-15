# app/users_db.py
from security import hash_password

fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "email": "admin@example.com",
        "hashed_password": hash_password("admin"),
        "role": "admin",
    },
    "manager_user": {
        "username": "manager_user",
        "full_name": "Manager User",
        "email": "manager@example.com",
        "hashed_password": hash_password("manager123"),
        "role": "manager",
    },
    "normal_user": {
        "username": "normal_user",
        "full_name": "Normal User",
        "email": "user@example.com",
        "hashed_password": hash_password("user123"),
        "role": "user",
    },
}
