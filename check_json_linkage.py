import json
import os

# Folder where your lesson JSONs are
DATA_FOLDER = "data"

def check_json_linkage(file_path):
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            lesson = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {file_path}")
            print(e)
            return

    print(f"\n✅ Loaded JSON: {lesson.get('title', 'Unknown Title')}")
    quiz = lesson.get("quiz")
    flashcards = lesson.get("flashcards")
    print("Quiz found?      ", bool(quiz))
    print("Flashcards found?", bool(flashcards))
    print("Raw Quiz:        ", quiz)
    print("Raw Flashcards:  ", flashcards)

def main():
    if not os.path.exists(DATA_FOLDER):
        print(f"❌ Data folder not found: {DATA_FOLDER}")
        return

    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".json"):
            check_json_linkage(os.path.join(DATA_FOLDER, filename))

if __name__ == "__main__":
    main()
