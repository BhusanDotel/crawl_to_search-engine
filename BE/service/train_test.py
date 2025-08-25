import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# ---------------------------
# 1. Load dataset
# ---------------------------
with open("data/task_two_data.json", "r") as f:
    data = json.load(f)

texts = [d["text"] for d in data]
labels = [d["category"] for d in data]

# ---------------------------
# 2. Features
# ---------------------------
vectorizer = TfidfVectorizer(stop_words='english')
X = vectorizer.fit_transform(texts)
y = labels

# ---------------------------
# 3. Train/Test Split
# ---------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ---------------------------
# 4. Train Naïve Bayes
# ---------------------------
nb = MultinomialNB()
nb.fit(X_train, y_train)

# ---------------------------
# 5. Evaluate Model
# ---------------------------
y_pred = nb.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# ---------------------------
# 6. Test with new input and show probabilities
# ---------------------------
async def classify_document(doc):
    doc_vec = vectorizer.transform([doc])
    probs = nb.predict_proba(doc_vec)[0]   # probability distribution
    categories = nb.classes_
    result = {cat: round(p*100, 2) for cat, p in zip(categories, probs)}
    predicted = nb.classes_[np.argmax(probs)]
    return predicted, result
