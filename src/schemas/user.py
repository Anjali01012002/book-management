from pydantic import BaseModel

class UserSchema(BaseModel):
    username: str
    password: str
    role: str = "member"

    class Config:
        schema_extra = {
            "example": {
                "username": "user1",
                "password": "password123",
                "role": "member"
            }
        }