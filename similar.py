import json
from sklearn.feature_extraction.text import TfidfVectorizer

with open("issues.json", encoding="utf-8") as file:
    issues = json.load(file)

texts = [
    f"{issue['title']} {issue['title']} {issue['title']} {issue['body'][:1500]}"
    for issue in issues
]
vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
vectors = vectorizer.fit_transform(texts)

query = input("Describe a new issue: ")
query_vector = vectorizer.transform([query])
scores = (vectors @ query_vector.T).toarray().ravel()

print("\nMost similar past issues:")
for index in scores.argsort()[::-1][:5]:
    if scores[index] == 0:
        continue
    print(f"\nScore: {scores[index]:.2f}")
    print("Title:", issues[index]["title"])
    print("URL:", issues[index]["url"])