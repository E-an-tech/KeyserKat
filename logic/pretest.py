#Pretest logic in progress for the Quesito!

import json

def load_preset(path="data/pretest.json"): 
    with open(path, "r") as 
file:
    return json.load(file)

def grade_pretest(user_answers, correct answers):
    score = sum(1 for u, c in zip(user_answers, correct answers)if u == c)
    if score >=4: 
        return "advanced"
    elif score >= 2:
        return "intermediate"
    else:
        return "beginner"