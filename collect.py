import json
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

issues = []

for page in range(1, 11):
    params = urlencode({
        "q": "repo:pandas-dev/pandas is:issue",
        "sort": "created",
        "order": "desc",
        "per_page": 100,
        "page": page,
    })
    url = f"https://api.github.com/search/issues?{params}"
    request = Request(url, headers={"User-Agent": "issue-triage-project"})

    with urlopen(request, timeout=30) as response:
        data = json.load(response)

    for item in data["items"]:
        issues.append({
            "number": item["number"],
            "title": item["title"],
            "body": item["body"] or "",
            "labels": [label["name"] for label in item["labels"]],
            "url": item["html_url"],
            "created_at": item["created_at"],
        })

    print(f"Page {page}: collected {len(data['items'])} issues")
    time.sleep(2)

with open("issues.json", "w", encoding="utf-8") as file:
    json.dump(issues, file, indent=2, ensure_ascii=False)

print(f"Saved {len(issues)} issues to issues.json")