import json
from collections import Counter

with open("issues.json", encoding="utf-8") as file:
    issues = json.load(file)

label_counts = Counter(
    label
    for issue in issues
    for label in issue["labels"]
)

unlabeled = sum(not issue["labels"] for issue in issues)

print("Total issues:", len(issues))
print("Issues without labels:", unlabeled)
print("\nMost common labels:")
for label, count in label_counts.most_common(15):
    print(f"{label}: {count}")

print("\nExample issue:")
print("Title:", issues[0]["title"])
print("Labels:", issues[0]["labels"])
print("URL:", issues[0]["url"])