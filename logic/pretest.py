import json
import random
import os

# Loads the queso physics questions
with open("pretest_physics.json", "r") as f:
    pool = json.load(f)

# File to store previously used question IDs
USED_QUESTIONS_FILE = "used_questions.json"

# Helper to create a unique ID for each question
def make_id(unit, category, index):
    return f"{unit}|{category}|{index}"

# Load used question IDs if they exist
if os.path.exists(USED_QUESTIONS_FILE):
    with open(USED_QUESTIONS_FILE, "r") as f:
        used_ids = set(json.load(f))
else:
    used_ids = set()

# Target: 2 application, 2 theory, 2 analysis
target_counts = {"Application": 2, "Theory": 2, "Analysis": 2}
current_counts = {"Application": 0, "Theory": 0, "Analysis": 0}

# Track selected questions
selected_questions = []

# Shuffle units for variety
units = list(pool.keys())
random.shuffle(units)

# First pass: try to select 1 question per unit while respecting the category limits
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

# Sanity check not enoungh meowney can keep me sane :D
if len(selected_questions) < 6:
    print("Not enough meowsome questions found. Try resetting used questions.")
else:
    random.shuffle(selected_questions)

    print("\n🎓 Here's your randomized 6-question quiz:\n")

    user_answers = []

    for i, q in enumerate(selected_questions, 1):
        print(f"Q{i}. ({q['category']})")
        print(q["question"])
        if "options" in q:
            option_labels = ['A', 'B', 'C', 'D', 'E']
            for label, opt in zip(option_labels, q["options"]):
                print(f" {label}. {opt}")
            answer = input("Your answer (A/B/C/D): ").strip().upper()
        else:
            answer = input("Your response: ").strip()
        print()
        user_answers.append({
            "question_id": q["id"],
            "category": q["category"],
            "user_answer": answer,
            "unit_hidden": q["unit"],  # not shown but saved for backend or later analysis
            "original_question": q["question"]
        })

    # Save used questions
    with open(USED_QUESTIONS_FILE, "w") as f:
        json.dump(list(used_ids), f)

    # Save user answers (optional)
    with open("user_answers.json", "w") as f:
        json.dump(user_answers, f, indent=2)

    print("Keyser is now assesing your answers please wait patiently for the next step he likes to take his time.")