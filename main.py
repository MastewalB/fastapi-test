from typing import List
from fastapi import FastAPI, Depends, HTTPException, status, Request, Path
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from contextlib import asynccontextmanager

from models import User, Post
from schemas import UserCreate, Token, UserLogin, PostCreate, PostResponse
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from auth import hash_password, verify_password, create_access_token ,get_user


Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    yield

app = FastAPI(lifespan=lifespan)

"""
Signup endpoint registers a new user.
It returns a token upon successful registration.
"""
@app.post("/signup", response_model=Token)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    new_user = User(
        email=user.email,
        password=hash_password(user.password),
        name=user.name
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": str(new_user.id)})
    return {"access_token": token}

"""
Login endpoint authenticates a user and returns a token.
"""
@app.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token}

"""
Add Post endpoint allows a user to create a new post.
It checks the size of the post text and raises an error if it exceeds 1 MB.
"""
@app.post("/add-post")
def add_post(post: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_user)):
    if len(post.text.encode("utf-8")) > 1_000_000:
        raise HTTPException(status_code=400, detail="Post too large (max 1 MB)")

    new_post = Post(text=post.text, user_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"postID": new_post.id}

"""
Get Posts endpoint retrieves all posts made by the current user.
It caches the response for 5 minutes in memory.
"""
@app.get("/posts", response_model=List[PostResponse])
@cache(expire=300) 
def get_posts(current_user: User = Depends(get_user), db: Session = Depends(get_db), request: Request = None):
    return db.query(Post).filter(Post.user_id == current_user.id).all()

"""
Delete Post endpoint allows a user to delete their own post.
"""
@app.delete("/posts/{post_id}")
def delete_post(
    post_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")

    db.delete(post)
    db.commit()
    return {"message": "Post deleted successfully"}