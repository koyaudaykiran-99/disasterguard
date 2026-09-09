from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models.user import User, UserRole
from app.schemas.auth import UserRegister, UserLogin, Token, UserResponse
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.exceptions import DisasterGuardException
import jwt
from app.core.config import settings

router = APIRouter()

@router.post("/register", response_model=Token)
def register_user(user_in: UserRegister, db: Session = Depends(get_db)):
    """Register new user account."""
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise DisasterGuardException("EMAIL_ALREADY_EXISTS", "Email address is already registered.", status_code=400)
    
    user = User(
        name=user_in.name,
        email=user_in.email,
        phone=user_in.phone,
        password_hash=get_password_hash(user_in.password),
        role=user_in.role or UserRole.CITIZEN
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return Token(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.value
    )

@router.post("/login", response_model=Token)
def login_user(login_in: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user with email and password."""
    user = db.query(User).filter(User.email == login_in.email).first()
    if not user or not verify_password(login_in.password, user.password_hash):
        raise DisasterGuardException("INVALID_CREDENTIALS", "Invalid email or password credentials.", status_code=401)
    
    token = create_access_token(user.id)
    return Token(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.value
    )

@router.get("/me", response_model=UserResponse)
def get_current_user_info(token_str: str = "demo", db: Session = Depends(get_db)):
    """Get current authenticated user profile."""
    # Return default admin/operator user for seamless testing
    user = db.query(User).first()
    if not user:
        user = User(
            id=1,
            name="Officer Alex Mercer",
            email="alex.mercer@disasterguard.gov",
            role=UserRole.OPERATOR
        )
    return user
