"""Authentication router with JWT tokens."""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database import get_db
from backend.models.user import User, UserRole
from backend.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/auth", tags=["Authentication"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


# Schemas
class UserCreate(BaseModel):
    email: str
    username: str
    full_name: str
    password: str
    role: str = "citizen"
    bar_council_id: Optional[str] = None
    court_name: Optional[str] = None
    specialization: Optional[str] = None
    about: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: str
    role: str
    is_active: bool
    specialization: Optional[str] = None
    about: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    bar_council_id: Optional[str] = None
    court_name: Optional[str] = None
    specialization: Optional[str] = None
    about: Optional[str] = None

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check existing
    result = await db.execute(select(User).where(
        (User.email == user_data.email) | (User.username == user_data.username)
    ))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email or username already registered")
    
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=pwd_context.hash(user_data.password),
        role=user_data.role,
        bar_council_id=user_data.bar_council_id,
        court_name=user_data.court_name,
        specialization=user_data.specialization,
        about=user_data.about
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    access_token = create_access_token(data={"sub": user.id})
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id, email=user.email, username=user.username,
            full_name=user.full_name, role=user.role, is_active=user.is_active,
            specialization=user.specialization, about=user.about
        ),
    )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.id})
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id, email=user.email, username=user.username,
            full_name=user.full_name, role=user.role, is_active=user.is_active,
            specialization=user.specialization, about=user.about
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return UserResponse(
        id=current_user.id, email=current_user.email, username=current_user.username,
        full_name=current_user.full_name, role=current_user.role, is_active=current_user.is_active,
        specialization=current_user.specialization, about=current_user.about
    )

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    for field, value in profile_data.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
        
    await db.commit()
    await db.refresh(current_user)
    
    return UserResponse(
        id=current_user.id, email=current_user.email, username=current_user.username,
        full_name=current_user.full_name, role=current_user.role, is_active=current_user.is_active,
        specialization=current_user.specialization, about=current_user.about
    )

@router.get("/lawyers", response_model=list[UserResponse])
async def get_lawyers(db: AsyncSession = Depends(get_db)):
    """Fetch all registered lawyers for the Citizen Directory."""
    result = await db.execute(select(User).where(User.role == UserRole.LAWYER.value))
    lawyers = result.scalars().all()
    
    return [
        UserResponse(
            id=l.id, email=l.email, username=l.username,
            full_name=l.full_name, role=l.role, is_active=l.is_active,
            specialization=l.specialization, about=l.about
        )
        for l in lawyers
    ]
