
from pydantic import BaseModel, Field, EmailStr


class PostSchema(BaseModel):
    id: int = Field(default=None)
    title: str = Field(...)
    content: str = Field(...)
    email: str = None

    class Config:
        schema_extra = {
            "example": {
                "title": "Securing FastAPI applications with JWT.",
                "content": "Test!"
            }
        }
        
class UserSchema(BaseModel):
    fullname: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "fullname": "Name Surname",
                "email": "test@test.com",
                "password": "password123"
            }
        }

class UserLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "email": "test@test.com",
                "password": "password123"
            }
        }
        
class UpdatePostSchema(BaseModel):
    title: str = Field(default=None)
    content: str = Field(default=None)
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Updated title",
                "content": "updated content"
            }
        }