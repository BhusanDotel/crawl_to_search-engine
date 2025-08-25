from typing import List, Optional
from pydantic import BaseModel

class Author(BaseModel):
    name: Optional[str] = None
    link: Optional[str] = None

class Report_Body(BaseModel):
    link: Optional[str] = None
    title: Optional[str] = None
    authors: Optional[List[Author]] = []  # default to empty list
    abstract: Optional[str] = None
    published: Optional[str] = None
    score: Optional[float] = 0.0

class Response_Body(BaseModel):
    results: Optional[List[Report_Body]] = []
    total: Optional[int] = 0