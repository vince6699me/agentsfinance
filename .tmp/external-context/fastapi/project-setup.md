---
source: Official Docs (fastapi.tiangolo.com)
library: FastAPI
package: fastapi
topic: project setup, routing, dependencies, SQLite
fetched: 2026-04-29
official_docs: https://fastapi.tiangolo.com/tutorial/
---

# FastAPI Documentation

## Installation

```bash
pip install "fastapi[standard]" ---> 100%
```

Note: When you install with `pip install "fastapi[standard]"` it comes with default optional standard dependencies including Uvicorn (ASGI server).

Alternative: `pip install fastapi` (without standard dependencies)

## Project Structure & Basic Patterns

### First Steps - Creating a FastAPI App

Create a file `main.py` with:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

### Running the Server

```bash
$ fastapi dev
```

This starts the development server at `http://127.0.0.1:8000`

Documentation available at `http://127.0.0.1:8000/docs`

## Path Parameters

```python
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
```

## Query Parameters

```python
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    return {"items": items[skip : skip + limit]}
```

## Request Body

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

@app.post("/items/")
async def create_item(item: Item):
    return item
```

## Dependencies

FastAPI's dependency injection system declares dependencies in path operation functions:

```python
from fastapi import Depends

async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
async def read_items(commons: dict = Depends(common_parameters)):
    return commons
```

### Classes as Dependencies

```python
class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit

@app.get("/items/")
async def read_items(commons: CommonQueryParams = Depends(CommonQueryParams)):
    return commons
```

### Dependencies with yield

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db():
    db = DatabaseSession()
    try:
        yield db
    finally:
        db.close()

@app.get("/items/")
async def read_items(db: DatabaseSession = Depends(get_db)):
    return db.query(Item).all()
```

## SQL (Relational) Databases

FastAPI supports any SQL database (SQLAlchemy is commonly used):

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)

Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Middleware

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Background Tasks

```python
from fastapi import BackgroundTasks

def write_notification(email: str, message: str):
    with open("log.txt", mode="a") as email_file:
        content = f"notification for {email}: {message}\n"
        email_file.write(content)

@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="some notification")
    return {"message": "Notification sent"}
```

## Testing

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
```

Run tests with: `pytest`

## Key Features Summary

- **Automatic docs**: Swagger UI at `/docs`, ReDoc at `/redoc`
- **Type validation**: Pydantic models for request/response validation
- **Dependency Injection**: Clean separation of concerns
- **Async support**: Native async/await support
- **OAuth2/JWT**: Built-in security utilities
- **WebSockets**: Full support