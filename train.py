import json
from collections import Counter

import joblib
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

from semantic_search import PREFIX, SemanticIssueSearch


with open("issues.json", encoding="utf-8") as file:
    issues = json.load(file)

texts = []
categories = []
issue_indices = []
target_labels = {"Bug", "Docs", "Enhancement"}

for index, issue in enumerate(issues):
    matches = target_labels.intersection(issue["labels"])
    if len(matches) != 1:
        continue

    title = PREFIX.sub("", issue["title"])
    texts.append(f"{title} {issue['body'][:1500]}")
    categories.append(next(iter(matches)))
    issue_indices.append(index)

print("Training examples:", dict(Counter(categories)))

search = SemanticIssueSearch()
embeddings = search.vectors[issue_indices]
train_indices, test_indices = train_test_split(
    list(range(len(texts))),
    test_size=0.2,
    random_state=42,
    stratify=categories,
)

vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=2)
vectorizer.fit([texts[index] for index in train_indices])


def features(indices):
    words = vectorizer.transform([texts[index] for index in indices])
    meaning = csr_matrix(embeddings[indices])
    return hstack([words, meaning]).tocsr()


classifier = LogisticRegression(max_iter=1000, class_weight="balanced")
classifier.fit(features(train_indices), [categories[index] for index in train_indices])
predictions = classifier.predict(features(test_indices))
print(classification_report([categories[index] for index in test_indices], predictions))

# Refit on every labeled issue after measuring performance on the held-out split.
vectorizer.fit(texts)
classifier.fit(features(list(range(len(texts)))), categories)
joblib.dump({"vectorizer": vectorizer, "classifier": classifier}, "issue_model.joblib")
print("Saved model to issue_model.joblib")
