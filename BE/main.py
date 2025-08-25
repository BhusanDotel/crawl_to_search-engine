from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from schema.search_report_schema import Response_Body

from service.search_report import search_reports

# ----------------- FastAPI App -----------------
app = FastAPI(title="Report Search API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

@app.get("/")
def root_path():
    return {"message": "Welcome to the Report Search API"}

@app.get("/search", response_model=Response_Body)
async def search(q: str = Query(..., description="Search query"),
           page: int = Query(1, ge=1),
           per_page: int = Query(10, ge=1, le=100)):

    _data = await search_reports(q)

    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated = _data[start:end]

    return Response_Body(results=paginated, total=len(_data))
