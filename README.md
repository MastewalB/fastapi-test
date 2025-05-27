# FastAPI User & Post Management App

A simple FastAPI application with JWT authentication, user registration/login, and basic post creation, retrieval, and deletion. Uses SQLAlchemy ORM and SQLite.

---

## Features

- User Signup & Login with email/password
- JWT-based Authentication
- Posts (1MB limit)
- Get Posts (JWT-protected, 5-min response cache per user)
- Delete Your Posts
- SQLite or MySQL database support

---

## Endpoints

```
POST /signup
POST /login
POST /add-post
GET /posts
DELETE /posts/{post_id}
```

## Tech Stack

- **FastAPI**
- **SQLAlchemy**
- **Pydantic**
- **JWT (via `python-jose`)**
- **SQLite**
- **fastapi-cache2** (response caching)

---

## Install Requirements

```bash
pip install -r requirements.txt

```
## Run app
```
uvicorn main:app --reload
```