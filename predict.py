import re
import joblib

model = joblib.load("issue_model.joblib")

title = input("Enter an issue title: ")
title = re.sub(r"^(BUG|DOCS?)\s*:\s*", "", title, flags=re.IGNORECASE)

print("Suggested label:", model.predict([title])[0])