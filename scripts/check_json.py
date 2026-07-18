import json

import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(SCRIPT_DIR, "..", "questions.json"), "r", encoding="utf-8") as f:
    data = json.load(f)

for exam in data:
    print(f"Exam: {exam['exam_name']}")
    nums = [q['number'] for q in exam['questions']]
    print(f"  Question numbers: {nums}")
    empty_opts = [q for q in exam['questions'] if not q['options']]
    if empty_opts:
        print(f"  Empty option question numbers: {[q['number'] for q in empty_opts]}")
        for q in empty_opts:
            print(f"    Q{q['number']}: {q['statement'][:150]}...")
