import os
import json

# Root folder containing all courses
#It is finding the lesson our dear consumer choose
COURSE_ROOT = "courses"

def discover_all_lessons(root=COURSE_ROOT):

    courses = {}

    if not os.path.exists(root):
        raise FileNotFoundError(f"Keyser could not find the course folder not found: {root}")

    for course in os.listdir(root):
        course_path = os.path.join(root, course)
        if not os.path.isdir(course_path):
            continue

        courses[course] = {}

        for unit in os.listdir(course_path):
            unit_path = os.path.join(course_path, unit)
            if not os.path.isdir(unit_path):
                continue

            lessons = [
                os.path.join(unit_path, f)
                for f in os.listdir(unit_path)
                if f.endswith(".json")
            ]

            lessons.sort()
            courses[course][unit] = lessons

    return courses


def load_lesson_json(path):
  
# Reads a lesson JSON file and goes hmmm so this is what you want yay!.

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
#Have fun understanding this code poyo 