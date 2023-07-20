from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI()
data = [
   {"id": 1, "title": "python programming", "author": "James", "publisher": "Goodread"},
   {"id": 2, "title": "Java complete Guide", "author": "David", "publisher": "Kindle"},
   {"id": 3, "title": "Azure developer", "author": "Peter", "publisher": "Microsoft press"},
]

class Book(BaseModel):
   id: int
   title: str
   author: str
   publisher: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/book")
def add_book(book: Book):
   data.append(book.dict())
   return data

@app.get("/list")
def get_books():
   return data

@app.get("/book/{id}")
def get_book(id: int):
   id = id - 1
   return data[id]

@app.put("/book/{id}")
def add_book(id: int, book: Book):
   data[id-1] = book
   return data

@app.delete("/book/{id}")
def delete_book(id: int):
   data.pop(id-1)
   return data
