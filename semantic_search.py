import hashlib
import json
import re
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


PROJECT_DIR = Path(__file__).resolve().parent
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
INDEX_PATH = PROJECT_DIR / "issue_embeddings.npz"
PREFIX = re.compile(r"^(BUG|DOCS?|ENH(?:ANCEMENT)?)\s*:\s*", re.IGNORECASE)


def issue_text(title, body=""):
    return f"{PREFIX.sub('', title)}\n{body[:1000]}"


class SemanticIssueSearch:
    def __init__(self):
        with (PROJECT_DIR / "issues.json").open(encoding="utf-8") as file:
            self.issues = json.load(file)

        texts = [issue_text(issue["title"], issue["body"]) for issue in self.issues]
        digest = hashlib.sha256(
            (MODEL_NAME + "\n" + json.dumps(texts, ensure_ascii=False)).encode("utf-8")
        ).hexdigest()
        self.model = SentenceTransformer(MODEL_NAME, device="cpu")

        if INDEX_PATH.exists():
            with np.load(INDEX_PATH, allow_pickle=False) as saved:
                if saved["digest"].item() == digest:
                    self.vectors = saved["vectors"]
                    return

        self.vectors = self.model.encode(
            texts, batch_size=32, normalize_embeddings=True, show_progress_bar=False
        )
        np.savez_compressed(INDEX_PATH, digest=digest, vectors=self.vectors)

    def search(self, title, body="", limit=5):
        query = self.model.encode(issue_text(title, body), normalize_embeddings=True)
        scores = self.vectors @ query
        return [
            {
                "title": self.issues[index]["title"],
                "url": self.issues[index]["url"],
                "score": round(float(scores[index]), 3),
            }
            for index in np.argsort(scores)[-limit:][::-1]
        ]


if __name__ == "__main__":
    search = SemanticIssueSearch()
    title = input("Describe a new issue: ")
    body = input("Add a description (optional): ")
    print("\nMost similar past issues:")
    for issue in search.search(title, body):
        print(f"\nScore: {issue['score']:.3f}")
        print("Title:", issue["title"])
        print("URL:", issue["url"])
