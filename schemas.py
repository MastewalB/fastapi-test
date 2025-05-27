from pydantic import BaseModel, EmailStr, constr

class UserBase(BaseModel):
    name: constr(strip_whitespace=True, min_length=1, max_length=100)
    email: EmailStr
    password: constr(strip_whitespace=True, min_length=8, max_length=128)

    class Config:
        from_attributes = True

class UserCreate(UserBase):
    name: constr(strip_whitespace=True, min_length=1, max_length=100)
    email: EmailStr
    password: constr(strip_whitespace=True, min_length=8, max_length=128)

class Token(BaseModel):
    access_token: str

class UserLogin(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=128)

class UserResponse(UserBase):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class PostCreate(BaseModel):
    text: constr(strip_whitespace=True, min_length=1, max_length=1_000_000)

class PostResponse(PostCreate):
    id: int
    text: str
    user_id: int

    class Config:
        from_attributes = True
