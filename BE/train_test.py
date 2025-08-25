import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score


data=[]

#read json file from disk
with open("data/task_two_Data.json", "r") as f:
    data = json.load(f)

texts = [d["text"] for d in data]
labels = [d["category"] for d in data]

# ---------------------------
# 2. Preprocess & Convert to Features
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
# 6. Test with new input
# ---------------------------
def classify_document(doc):
    doc_vec = vectorizer.transform([doc])
    prediction = nb.predict(doc_vec)[0]
    return prediction

# Example predictions
print("\nPrediction Examples:")
print("Input: 'The president met with foreign leaders to discuss trade policies.'")
print("Predicted Category:", classify_document("The president met with foreign leaders to discuss trade policies."))

print("\nInput: 'Pfizer announced a breakthrough in cancer research.'")
print("Predicted Category:", classify_document("Pfizer announced a breakthrough in cancer research."))

print("\nInput: 'The stock market crashed due to rising inflation concerns.'")
print("Predicted Category:", classify_document("The stock market crashed due to rising inflation concerns."))
