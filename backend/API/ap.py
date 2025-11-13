import os
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import (
    Depends,
    FastAPI,
    File,
    HTTPException,
    UploadFile,
    status,
    Form,
)
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, select
from jose import JWTError, jwt

SECRET_KEY = os.environ.get("JWT_SECRET", "CHANGE_THIS_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  

BASE_DIR = os.path.dirname(__file__)
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Follow(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    follower_id: int = Field(index=True)
    followee_id: int = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Post(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    author_id: int = Field(index=True)
    content: str
    image_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Comment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(index=True)
    author_id: int = Field(index=True)
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PostOut(BaseModel):
    id: int
    author_id: int
    content: str
    image_url: Optional[str]
    created_at: datetime


class CommentOut(BaseModel):
    id: int
    post_id: int
    author_id: int
    content: str
    created_at: datetime

sqlite_file_name = "db.sqlite"
engine = create_engine(f"sqlite:///{sqlite_file_name}", echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def save_upload_file(upload_file: UploadFile) -> str:
    ext = os.path.splitext(upload_file.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        f.write(upload_file.file.read())
    return filename

app = FastAPI(title="Mini Threads API (Contoh)")

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

def get_session():
    with Session(engine) as session:
        yield session


async def get_current_user(token: str = Depends(lambda: None), session: Session = Depends(get_session)):
    from fastapi import Header

    def _inner(authorization: Optional[str] = Header(None)):
        if authorization is None:
            raise HTTPException(status_code=401, detail="Missing authorization header")
        parts = authorization.split()
        if parts[0].lower() != "bearer" or len(parts) != 2:
            raise HTTPException(status_code=401, detail="Invalid auth header")
        return parts[1]

    token_str = _inner  
    raise HTTPException(status_code=500, detail="Internal use only")

def current_user_from_token(authorization: Optional[str] = None, session: Session = Depends(get_session)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    parts = authorization.split()
    if parts[0].lower() != "bearer" or len(parts) != 2:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = parts[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalid or expired")
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.post("/register", response_model=Token)
def register(data: UserCreate, session: Session = Depends(get_session)):
    q = select(User).where(User.username == data.username)
    exists = session.exec(q).first()
    if exists:
        raise HTTPException(status_code=400, detail="Username already taken")
    u = User(username=data.username, hashed_password=hash_password(data.password))
    session.add(u)
    session.commit()
    session.refresh(u)
    token = create_access_token({"sub": u.id})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/login", response_model=Token)
def login(data: UserCreate, session: Session = Depends(get_session)):
    q = select(User).where(User.username == data.username)
    user = session.exec(q).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token({"sub": user.id})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me")
def me(current_user: User = Depends(current_user_from_token)):
    return {"id": current_user.id, "username": current_user.username, "created_at": current_user.created_at}


@app.get("/users")
def list_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return [{"id": u.id, "username": u.username} for u in users]

@app.post("/follow/{user_id}")
def follow(user_id: int, current_user: User = Depends(current_user_from_token), session: Session = Depends(get_session)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Can't follow yourself")
    target = session.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    q = select(Follow).where(Follow.follower_id == current_user.id, Follow.followee_id == user_id)
    if session.exec(q).first():
        raise HTTPException(status_code=400, detail="Already following")
    f = Follow(follower_id=current_user.id, followee_id=user_id)
    session.add(f)
    session.commit()
    return {"detail": "followed"}


@app.post("/unfollow/{user_id}")
def unfollow(user_id: int, current_user: User = Depends(current_user_from_token), session: Session = Depends(get_session)):
    q = select(Follow).where(Follow.follower_id == current_user.id, Follow.followee_id == user_id)
    rel = session.exec(q).first()
    if not rel:
        raise HTTPException(status_code=404, detail="Not following")
    session.delete(rel)
    session.commit()
    return {"detail": "unfollowed"}


@app.get("/followers/{user_id}")
def followers(user_id: int, session: Session = Depends(get_session)):
    q = select(Follow).where(Follow.followee_id == user_id)
    rows = session.exec(q).all()
    return [{"follower_id": r.follower_id, "created_at": r.created_at} for r in rows]

@app.post("/posts", response_model=PostOut)
async def create_post(
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(current_user_from_token),
    session: Session = Depends(get_session),
):
    filename = None
    if image:
        if not image.filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
            raise HTTPException(status_code=400, detail="File not supported")
        filename = save_upload_file(image)
    p = Post(author_id=current_user.id, content=content, image_path=filename)
    session.add(p)
    session.commit()
    session.refresh(p)
    image_url = f"/uploads/{p.image_path}" if p.image_path else None
    return PostOut(
        id=p.id,
        author_id=p.author_id,
        content=p.content,
        image_url=image_url,
        created_at=p.created_at,
    )


@app.get("/posts/{post_id}", response_model=PostOut)
def get_post(post_id: int, session: Session = Depends(get_session)):
    p = session.get(Post, post_id)
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")
    image_url = f"/uploads/{p.image_path}" if p.image_path else None
    return PostOut(id=p.id, author_id=p.author_id, content=p.content, image_url=image_url, created_at=p.created_at)


@app.get("/posts")
def list_posts(limit: int = 20, offset: int = 0, session: Session = Depends(get_session)):
    q = select(Post).order_by(Post.created_at.desc()).offset(offset).limit(limit)
    rows = session.exec(q).all()
    result = []
    for p in rows:
        result.append(
            {
                "id": p.id,
                "author_id": p.author_id,
                "content": p.content,
                "image_url": f"/uploads/{p.image_path}" if p.image_path else None,
                "created_at": p.created_at,
            }
        )
    return result

@app.post("/posts/{post_id}/comments", response_model=CommentOut)
def comment_post(post_id: int, content: str = Form(...), current_user: User = Depends(current_user_from_token), session: Session = Depends(get_session)):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    c = Comment(post_id=post_id, author_id=current_user.id, content=content)
    session.add(c)
    session.commit()
    session.refresh(c)
    return CommentOut(id=c.id, post_id=c.post_id, author_id=c.author_id, content=c.content, created_at=c.created_at)


@app.get("/posts/{post_id}/comments", response_model=List[CommentOut])
def get_comments(post_id: int, session: Session = Depends(get_session)):
    q = select(Comment).where(Comment.post_id == post_id).order_by(Comment.created_at.asc())
    rows = session.exec(q).all()
    return [CommentOut(id=r.id, post_id=r.post_id, author_id=r.author_id, content=r.content, created_at=r.created_at) for r in rows]

@app.get("/feed")
def feed(limit: int = 30, offset: int = 0, current_user: User = Depends(current_user_from_token), session: Session = Depends(get_session)):
    q = select(Follow.followee_id).where(Follow.follower_id == current_user.id)
    followee_ids = [r for (r,) in session.exec(q).all()]
    ids = followee_ids + [current_user.id]
    if not ids:
        return []
    q2 = select(Post).where(Post.author_id.in_(ids)).order_by(Post.created_at.desc()).offset(offset).limit(limit)
    rows = session.exec(q2).all()
    result = []
    for p in rows:
        result.append(
            {
                "id": p.id,
                "author_id": p.author_id,
                "content": p.content,
                "image_url": f"/uploads/{p.image_path}" if p.image_path else None,
                "created_at": p.created_at,
            }
        )
    return result
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
