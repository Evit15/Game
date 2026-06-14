import re
import pandas as pd

rows = []

with open("/Users/hieu.dang/Github/Game/ocr.txt", encoding="utf-8") as f:
    blocks = f.read().split("====================")

for block in blocks:
    print("Processing block:")
    print(block)
    print("-" * 20)
    lines = [
        x.strip()
        for x in block.splitlines()
        if x.strip()
    ]

    if len(lines) < 3:
        continue

    # Look for "Question:" pattern
    question_idx = -1
    for i, line in enumerate(lines):
        if line.startswith("Question"):
            question_idx = i
            break
    
    # If "Question:" found, use the next line as the actual question
    if question_idx != -1 and question_idx + 1 < len(lines):
        question = lines[question_idx + 1]
        # Skip 1 line, then option A, then option B
        if question_idx + 4 < len(lines):
            option_a = lines[question_idx + 3]
            option_b = lines[question_idx + 4]
        else:
            option_a = ""
            option_b = ""
    else:
        # Fallback: Skip metadata lines and find question
        question_idx = 0
        for i, line in enumerate(lines):
            if len(line) > 10 and not any(keyword in line for keyword in ["Score:", "Question :", "Streak"]):
                question_idx = i
                break
        
        question = lines[question_idx]
        option_a = ""
        option_b = ""

        # Try to find options with A/B prefixes first
        for line in lines[question_idx+1:]:
            if line.startswith("A"):
                option_a = line
            elif line.startswith("B"):
                option_b = line

        # If A/B format not found, use the next two lines as options
        if not option_a and not option_b:
            option_lines = [line for line in lines[question_idx+1:] if len(line) > 2]
            if len(option_lines) >= 2:
                option_a = option_lines[0]
                option_b = option_lines[1]

    if option_a and option_b:
        rows.append({
            "Question": question,
            "A": option_a,
            "B": option_b
        })
    print(f"Extracted question: {question}")
    print(f"Option A: {option_a}")
    print(f"Option B: {option_b}")
    print("=" * 40)

df = pd.DataFrame(rows)

df.drop_duplicates(inplace=True)

df.to_excel("questions.xlsx", index=False)

print(df.head())