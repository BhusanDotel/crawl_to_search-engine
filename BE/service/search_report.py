from persists_data import get_all_reports
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


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

async def search_reports(query: str):
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