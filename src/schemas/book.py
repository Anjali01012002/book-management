from pydantic import BaseModel

class BookSchema(BaseModel):
    title: str
    author: str
    isbn: str
    quantity: int

    class Config:
        schema_extra = {
            "example": {
                "title": "Sample Book",
                "author": "John Doe",
                "isbn": "1234567890123",
                "quantity": 5
            }
        }