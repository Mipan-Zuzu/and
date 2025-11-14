import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Header, UploadFile, File, Form, status
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel, Field, Session, create_engine, select
from passlib.context import CryptContext
from jose import jwt, JWTError
import cloudinary
import cloudinary.uploader

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET", "CHANGE_ME")
ALGORITHM = "HS256"
ACCESS_EXPIRE_MINUTES = 60  
REFRESH_EXPIRE_DAYS = 14

CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUD_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUD_SECRET = os.getenv("CLOUDINARY_API_SECRET")

if not (CLOUD_NAME and CLOUD_KEY and CLOUD_SECRET):
    print("Warning: Cloudinary credentials not found in env. Image uploads will fail until configured.")

cloudinary.config(
    cloud_name=CLOUD_NAME,
    api_key=CLOUD_KEY,
    api_secret=CLOUD_SECRET,
    secure=True,
)

sqlite_file_name = "db.sqlite"
engine = create_engine(f"sqlite:///{sqlite_file_name}", echo=False)

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(title="Mini Social API (scaffold)")

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RefreshToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    token: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    revoked: bool = False

class Post(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    author_id: int = Field(index=True)
    content: str
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Follow(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    follower_id: int = Field(index=True)
    followee_id: int = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Comment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(index=True)
    author_id: int = Field(index=True)
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

def get_session():
    with Session(engine) as session:
        yield session

def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return token

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalid or expired")

async def current_user_from_token(authorization: Optional[str] = Header(None), session: Session = Depends(get_session)) -> User:
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    parts = authorization.split()
    if parts[0].lower() != "bearer" or len(parts) != 2:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = parts[1]
    payload = decode_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def store_refresh_token(session: Session, user_id: int, token: str) -> RefreshToken:
    expires = datetime.utcnow() + timedelta(days=REFRESH_EXPIRE_DAYS)
    rt = RefreshToken(user_id=user_id, token=token, expires_at=expires)
    session.add(rt)
    session.commit()
    session.refresh(rt)
    return rt

def revoke_refresh_token(session: Session, token: str):
    q = select(RefreshToken).where(RefreshToken.token == token)
    rt = session.exec(q).first()
    if rt:
        rt.revoked = True
        session.add(rt)
        session.commit()

def is_refresh_token_valid(session: Session, token: str) -> bool:
    q = select(RefreshToken).where(RefreshToken.token == token, RefreshToken.revoked == False)
    rt = session.exec(q).first()
    if not rt:
        return False
    if rt.expires_at < datetime.utcnow():
        return False
    return True

@app.post("/register")
def register(username: str = Form(...), password: str = Form(...), session: Session = Depends(get_session)):
    q = select(User).where(User.username == username)
    if session.exec(q).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    u = User(username=username, hashed_password=hash_password(password))
    session.add(u)
    session.commit()
    session.refresh(u)
    access = create_access_token({"sub": u.id})
    refresh = create_access_token({"sub": u.id, "type": "refresh"}, expires_delta=timedelta(days=REFRESH_EXPIRE_DAYS))
    store_refresh_token(session, u.id, refresh)
    return {"access_token": access, "refresh_token": refresh}

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...), session: Session = Depends(get_session)):
    q = select(User).where(User.username == username)
    user = session.exec(q).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access = create_access_token({"sub": user.id})
    refresh = create_access_token({"sub": user.id, "type": "refresh"}, expires_delta=timedelta(days=REFRESH_EXPIRE_DAYS))
    store_refresh_token(session, user.id, refresh)
    return {"access_token": access, "refresh_token": refresh}

@app.post("/refresh")
def refresh(refresh_token: str = Form(...), session: Session = Depends(get_session)):
    if not is_refresh_token_valid(session, refresh_token):
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    user_id = payload.get("sub")
    revoke_refresh_token(session, refresh_token)
    new_refresh = create_access_token({"sub": user_id, "type": "refresh"}, expires_delta=timedelta(days=REFRESH_EXPIRE_DAYS))
    store_refresh_token(session, user_id, new_refresh)
    new_access = create_access_token({"sub": user_id})
    return {"access_token": new_access, "refresh_token": new_refresh}

@app.get("/me")
def me(user: User = Depends(current_user_from_token)):
    return {"id": user.id, "username": user.username, "created_at": user.created_at}

@app.post("/posts")
def create_post(content: str = Form(...), image: Optional[UploadFile] = File(None), user: User = Depends(current_user_from_token), session: Session = Depends(get_session)):
    image_url = None
    if image:
        if not image.filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
            raise HTTPException(status_code=400, detail="Unsupported file type")
        try:
            res = cloudinary.uploader.upload(image.file)
            image_url = res.get("secure_url")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Image upload failed: {e}")
    p = Post(author_id=user.id, content=content, image_url=image_url)
    session.add(p)
    session.commit()
    session.refresh(p)
    return {"id": p.id, "author_id": p.author_id, "content": p.content, "image_url": p.image_url, "created_at": p.created_at}

@app.get("/posts")
def list_posts(limit: int = 20, offset: int = 0, session: Session = Depends(get_session)):
    q = select(Post).order_by(Post.created_at.desc()).offset(offset).limit(limit)
    rows = session.exec(q).all()
    return [
        {"id": r.id, "author_id": r.author_id, "content": r.content, "image_url": r.image_url, "created_at": r.created_at}
        for r in rows
    ]

@app.post("/follow/{user_id}")
def follow(user_id: int, me: User = Depends(current_user_from_token), session: Session = Depends(get_session)):
    if user_id == me.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    target = session.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    q = select(Follow).where(Follow.follower_id == me.id, Follow.followee_id == user_id)
    if session.exec(q).first():
        raise HTTPException(status_code=400, detail="Already following")
    f = Follow(follower_id=me.id, followee_id=user_id)
    session.add(f)
    session.commit()
    return {"detail": "followed"}

@app.post("/unfollow/{user_id}")
def unfollow(user_id: int, me: User = Depends(current_user_from_token), session: Session = Depends(get_session)):
    q = select(Follow).where(Follow.follower_id == me.id, Follow.followee_id == user_id)
    rel = session.exec(q).first()
    if not rel:
        raise HTTPException(status_code=404, detail="Not following")
    session.delete(rel)
    session.commit()
    return {"detail": "unfollowed"}

@app.post("/posts/{post_id}/comments")
def comment_post(post_id: int, content: str = Form(...), me: User = Depends(current_user_from_token), session: Session = Depends(get_session)):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    c = Comment(post_id=post_id, author_id=me.id, content=content)
    session.add(c)
    session.commit()
    session.refresh(c)
    return {"id": c.id, "post_id": c.post_id, "author_id": c.author_id, "content": c.content, "created_at": c.created_at}

@app.get("/posts/{post_id}/comments")
def get_comments(post_id: int, session: Session = Depends(get_session)):
    q = select(Comment).where(Comment.post_id == post_id).order_by(Comment.created_at.asc())
    rows = session.exec(q).all()
    return [
        {"id": r.id, "post_id": r.post_id, "author_id": r.author_id, "content": r.content, "created_at": r.created_at}
        for r in rows
    ]

@app.post("/logout")
def logout(refresh_token: str = Form(...), session: Session = Depends(get_session)):
    revoke_refresh_token(session, refresh_token)
    return {"detail": "logged out"}
