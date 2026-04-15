# app/models/user.py
from datetime import datetime, timedelta
import uuid
from typing import Optional, Dict, Any

from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError

Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Move to config
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<User(name={self.first_name} {self.last_name}, email={self.email})>"

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str) -> bool:
        """Verify a plain password against the hashed password."""
        return pwd_context.verify(plain_password, self.password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT refresh token with a longer expiry."""
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(days=7))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> Optional[UUID]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            return uuid.UUID(user_id) if user_id else None
        except (InvalidTokenError, ValueError):
            return None

    @classmethod
    def register(cls, db, user_data: Dict[str, Any]) -> "User":
        """Register a new user."""
        password = user_data.get('password', '')
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")

        existing_user = db.query(cls).filter(
            (cls.email == user_data.get('email')) |
            (cls.username == user_data.get('username'))
        ).first()

        if existing_user:
            raise ValueError("Username or email already exists")

        new_user = cls(
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            email=user_data['email'],
            username=user_data['username'],
            password=cls.hash_password(password),
            is_active=True,
            is_verified=False
        )

        db.add(new_user)
        db.flush()
        return new_user

    @classmethod
    def authenticate(cls, db, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return tokens with user ORM object."""
        user = db.query(cls).filter(
            (cls.username == username) | (cls.email == username)
        ).first()

        if not user or not user.verify_password(password):
            return None

        user.last_login = datetime.utcnow()
        db.flush()

        expires_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        return {
            "access_token": cls.create_access_token({"sub": str(user.id)}),
            "refresh_token": cls.create_refresh_token({"sub": str(user.id)}),
            "token_type": "bearer",
            "expires_at": expires_at,
            "user": user
        }
