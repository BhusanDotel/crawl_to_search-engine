from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, Query
from sklearn.metrics.pairwise import cosine_similarity
from fastapi.middleware.cors import CORSMiddleware
from sklearn.feature_extraction.text import TfidfVectorizer

from persists_data import get_all_reports

# ----------------- Load Data -----------------
data=get_all_reports()

# Prepare documents for TF-IDF (title + abstract + authors)
documents = []
for report in data:
    title = report.get("title", "")
    abstract = report.get("abstract", "")
    authors = " ".join([author.get("name", "") for author in report.get("authors", [])])
    documents.append(f"{title} {abstract} {authors}")

# Create TF-IDF vectors
vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix = vectorizer.fit_transform(documents)

# ----------------- FastAPI App -----------------
app = FastAPI(title="Report Search API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

class Author(BaseModel):
    name: Optional[str] = None
    link: Optional[str] = None

class Report(BaseModel):
    link: Optional[str] = None
    title: Optional[str] = None
    authors: Optional[List[Author]] = []  # default to empty list
    abstract: Optional[str] = None
    published: Optional[str] = None
    score: Optional[float] = 0.0

class Response(BaseModel):
    results: Optional[List[Report]] = []
    total: Optional[int] = 0

@app.get("/")
def root_path():
    return {"message": "Welcome to the Report Search API"}

def search_reports(query: str):
    query_vec = vectorizer.transform([query])
    similarity = cosine_similarity(query_vec, tfidf_matrix).flatten()

    results = []
    for idx, score in enumerate(similarity):
        if score > 0:
            report = data[idx]
            results.append({
                "link": report.get("link"),
                "title": report.get("title"),
                "authors": report.get("authors"),
                "abstract": report.get("abstract"),
                "published": report.get("published"),
                "score": float(score)
            })
    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results

@app.get("/search", response_model=Response)
def search(q: str = Query(..., description="Search query"),
           page: int = Query(1, ge=1),
           per_page: int = Query(10, ge=1, le=100)):
    
    all_results = search_reports(q)
    
    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated = all_results[start:end]

    return Response(results=paginated, total=len(data))
