from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from pydantic import BaseModel
from datetime import datetime, timedelta

from src.db.database import SessionLocal
from src.models.user import User
from src.core.config import Config
# from src.core.auth import hash_password, verify_password, create_access_token

router = APIRouter()

# Pydantic Schema
class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "member"

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# JWT decode and current user getter
async def get_current_user(token: str = Depends(configure_oauth := lambda: OAuth2PasswordBearer(tokenUrl="/api/users/login")),
                           db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# ✅ Register Route
@router.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_pw = hash_password(user.password)
    new_user = User(username=user.username, password=hashed_pw, role=user.role)
    db.add(new_user)
    db.commit()
    return {"msg": "User registered successfully"}

# ✅ Login Route
@router.post("/login")
async def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token({"sub": db_user.username, "role": db_user.role})
    return {"access_token": access_token, "token_type": "bearer"}

# ✅ Refresh Token
@router.post("/refresh")
async def refresh(current_user: User = Depends(get_current_user)):
    new_token = create_access_token({"sub": current_user.username, "role": current_user.role})
    return {"access_token": new_token}
