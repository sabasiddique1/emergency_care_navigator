"""Authentication utilities for EmergencyCareNavigator."""
import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from app.models import User, LoginRequest, RegisterRequest

# JWT Configuration
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# User storage (in production, use a database)
USERS_FILE = "users.json"


def load_users() -> Dict[str, User]:
    """Load users from JSON file."""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                data = json.load(f)
                return {email: User(**user) for email, user in data.items()}
        except Exception:
            return {}
    return {}


def save_users(users: Dict[str, User]) -> None:
    """Save users to JSON file."""
    data = {
        email: {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "facility_name": user.facility_name,
            "password_hash": user.password_hash
        }
        for email, user in users.items()
    }
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def hash_password(password: str) -> str:
    """Hash password using SHA256 (simple hashing for demo)."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash."""
    return hash_password(password) == password_hash


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email."""
    users = load_users()
    return users.get(email.lower())


def create_user(email: str, password: str, name: str, role: str, facility_name: Optional[str] = None) -> User:
    """Create a new user."""
    users = load_users()
    
    if email.lower() in users:
        raise ValueError("User already exists")
    
    if role == "hospital_staff" and not facility_name:
        raise ValueError("facility_name is required for hospital staff")
    
    user = User(
        id=secrets.token_urlsafe(16),
        email=email.lower(),
        name=name,
        role=role,
        facility_name=facility_name,
        password_hash=hash_password(password)
    )
    
    users[email.lower()] = user
    save_users(users)
    return user


def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate user and return User if valid."""
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


# Initialize with demo users if file doesn't exist
def init_demo_users():
    """Initialize demo users for testing."""
    users = load_users()
    if not users:
        # Demo patient
        create_user("patient@demo.com", "patient123", "Demo Patient", "patient")
        # Demo hospital staff
        create_user("hospital@demo.com", "hospital123", "Hospital Staff", "hospital_staff", "Aga Khan University Hospital")
        create_user("staff@demo.com", "staff123", "Receptionist", "hospital_staff", "Jinnah Hospital")


# Initialize on import
init_demo_users()





