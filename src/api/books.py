from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from src.models.book import Book
from src.models.user import User
from src.db.database import SessionLocal
from src.api.users import get_current_user
from src.deps.auth_deps import check_role  # make sure this is implemented correctly

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Schema
class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str
    quantity: int

class BookOut(BookCreate):
    id: int
    class Config:
        from_attributes = True

# 📘 Create Book (Librarian/Admin)
@router.post("/books", response_model=BookOut)
def create_book(
    book: BookCreate,
    db: Session = Depends(get_db),
    user: User = Depends(check_role("librarian"))
):
    new_book = Book(**book.dict())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

# 📘 Get All Books (Everyone)
@router.get("/books", response_model=List[BookOut])
def get_books(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    books = db.query(Book).all()
    return books

# 📘 Update Book (Librarian/Admin)
@router.put("/books/{id}", response_model=BookOut)
def update_book(
    id: int,
    book: BookCreate,
    db: Session = Depends(get_db),
    user: User = Depends(check_role("librarian"))
):
    db_book = db.query(Book).filter(Book.id == id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in book.dict().items():
        setattr(db_book, key, value)
    db.commit()
    db.refresh(db_book)
    return db_book

# 📘 Delete Book (Admin only)
@router.delete("/books/{id}")
def delete_book(
    id: int,
    db: Session = Depends(get_db),
    user: User = Depends(check_role("admin"))
):
    db_book = db.query(Book).filter(Book.id == id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(db_book)
    db.commit()
    return {"msg": "Book deleted"}
