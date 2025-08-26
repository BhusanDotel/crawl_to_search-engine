import re
import nltk
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from persists_data import get_all_reports

# ----------------- Download required NLTK resources -----------------
nltk.download("punkt_tab")
nltk.download("wordnet")
nltk.download("stopwords")

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer, PorterStemmer

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()

# ----------------- Preprocessing Function -----------------
def preprocess(text, use_stemming=False):
    # Lowercase
    text = text.lower()
    # Remove non-alphabetic chars
    text = re.sub(r"[^a-z\s]", "", text)
    # Tokenize
    tokens = nltk.word_tokenize(text)
    # Remove stopwords
    tokens = [t for t in tokens if t not in stop_words]

    if use_stemming:
        tokens = [stemmer.stem(t) for t in tokens]
    else:
        tokens = [lemmatizer.lemmatize(t) for t in tokens]

    return " ".join(tokens)

# Wrap for TfidfVectorizer
def custom_tokenizer(text):
    return preprocess(text).split()

# ----------------- Load Data -----------------
data = get_all_reports()

# Prepare documents for TF-IDF (title + abstract + authors)
documents = []
for report in data:
    title = report.get("title", "")
    abstract = report.get("abstract", "")
    authors = " ".join([author.get("name", "") for author in report.get("authors", [])])
    combined_text = f"{title} {abstract} {authors}"
    documents.append(preprocess(combined_text))  # preprocess before vectorizing

# Create TF-IDF vectors
vectorizer = TfidfVectorizer(tokenizer=custom_tokenizer, stop_words=None)
tfidf_matrix = vectorizer.fit_transform(documents)

# ----------------- Search Function -----------------
async def search_reports(query: str, use_stemming=False):
    # Preprocess query the same way as documents
    query_processed = preprocess(query, use_stemming=use_stemming)
    query_vec = vectorizer.transform([query_processed])
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
