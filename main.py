import uvicorn
from fastapi import FastAPI
from src.api import books, users  # assuming you have both
from src.db.database import Base, engine

app = FastAPI()

# Create DB tables at startup
@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)

# Register routers
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(books.router, prefix="/api/books", tags=["Books"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
