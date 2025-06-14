import json
import random
import os

# Load the question pool
with open("pretest_physics.json", "r") as f:
    pool = json.load(f)

USED_QUESTIONS_FILE = "used_questions.json"

def make_id(unit, category, index):
    return f"{unit}|{category}|{index}"

# Load previously used question IDs
if os.path.exists(USED_QUESTIONS_FILE):
    with open(USED_QUESTIONS_FILE, "r") as f:
        used_ids = set(json.load(f))
else:
    used_ids = set()

# Target question types
target_counts = {"Application": 2, "Theory": 2, "Analysis": 2}
current_counts = {"Application": 0, "Theory": 0, "Analysis": 0}

selected_questions = []

# Shuffle units and categories
units = list(pool.keys())
random.shuffle(units)

for unit in units:
    categories = pool[unit]
    possible_cats = list(categories.keys())
    random.shuffle(possible_cats)

    for cat in possible_cats:
        if current_counts[cat] >= target_counts[cat]:
            continue
        questions = categories[cat]
        q_indexes = list(range(len(questions)))
        random.shuffle(q_indexes)

        for i in q_indexes:
            q_id = make_id(unit, cat, i)
            if q_id not in used_ids:
                question = questions[i]
                question["unit"] = unit
                question["category"] = cat
                question["id"] = q_id
                selected_questions.append(question)
                used_ids.add(q_id)
                current_counts[cat] += 1
                break
        break

    if all(current_counts[c] == target_counts[c] for c in target_counts):
        break

# Sanity check
if len(selected_questions) < 6:
    print("Not enough meowsome questions found. Try restarting the quiz to give Keyser a chance to find the questions.")
    exit()
else:
    random.shuffle(selected_questions)

    print("\n Here's the KeyserKat approved physics pre-test \n")

    user_answers = []

    for q in selected_questions:
        print(q["question"])
        if "options" in q:
            for opt in q["options"]:
                print(f"- {opt}")
            answer = input("Type your chosen answer (copy and paste it if you desire Keyser will not mind): ").strip()
        else:
            valid_options = [opt.strip().lower() for opt in q["options"]]
while True:
    answer = input("Type your chosen answer (copy it or type it fully): ").strip()
    if answer.lower() in valid_options:
        break
    else:
        print("Keyser never allowed you to choose that answer. How dare you! Try again...")

        print()
        user_answers.append({
            "question_id": q["id"],
            "user_answer": answer,
            "unit_hidden": q["unit"],  # for tracking performance
            "original_question": q["question"]
        })

    # Save used question IDs
    with open(USED_QUESTIONS_FILE, "w") as f:
        json.dump(list(used_ids), f)

    # Save answers
    with open("user_answers.json", "w") as f:
        json.dump(user_answers, f, indent=2)

    print("Keyser is now assessing your answers. Please wait patiently he likes to take his time.")