import joblib
from fastapi import FastAPI
from pydantic import BaseModel
from scipy.sparse import csr_matrix, hstack

from semantic_search import PREFIX, SemanticIssueSearch, issue_text

app = FastAPI()
model = joblib.load("issue_model.joblib")
semantic_search = SemanticIssueSearch()

class IssueRequest(BaseModel):
    title: str
    body: str = ""


@app.get("/")
def home():
    return {"message": "Issue triage API is running"}


@app.post("/classify")
def classify(issue: IssueRequest):
    text = f"{PREFIX.sub('', issue.title)} {issue.body[:1500]}"
    words = model["vectorizer"].transform([text])
    meaning = semantic_search.model.encode(
        issue_text(issue.title, issue.body), normalize_embeddings=True
    )
    features = hstack([words, csr_matrix(meaning.reshape(1, -1))]).tocsr()
    label = model["classifier"].predict(features)[0]
    return {"suggested_label": str(label)}

@app.post("/similar")
def similar(issue: IssueRequest):
    return {"similar_issues": semantic_search.search(issue.title, issue.body)}

@app.post("/analyze")
def analyze(issue: IssueRequest):
    label_result = classify(issue)
    similar_result = similar(issue)

    return {
        "suggested_label": label_result["suggested_label"],
        "similar_issues": similar_result["similar_issues"],
    }
