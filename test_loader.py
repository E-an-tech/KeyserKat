import json
import os

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def test_levels():
    print("=== TESTING LEVELS ===")
    levels = load_json("data/levels.json")

    for course_key, course in levels.items():
        print(f"\nCourse: {course_key} — {course.get('title')}")
        for unit in course.get("units", []):
            print(f"  Unit {unit['id']}: {unit['title']}")
            print(f"    Lessons: {len(unit.get('lessons', []))}")

def test_lessons():
    print("\n=== TESTING INDIVIDUAL LESSON FILES ===")

    files = [
        "data/courses/physics/unit1/lesson1.json",
        "data/courses/physics/unit1/lesson2.json",
        "data/courses/physics/unit1/lesson3.json",
        "data/courses/physics/unit1/lesson4.json",
        "data/placeholder_stats.json"
    ]

    for f in files:
        print(f"\nFILE: {f}")
        try:
            data = load_json(f)
            print("  Loaded OK")
            print("  Title:", data.get("title", "[missing title]"))
        except Exception as e:
            print("  ERROR:", e)

if __name__ == "__main__":
    test_levels()
    test_lessons()
