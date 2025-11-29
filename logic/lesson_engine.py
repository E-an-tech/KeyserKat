import json
import random
import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.uix.popup import Popup
#Added from pre test imagined every asset will need to be importe

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
#Find and structure the headings
#Interactive headings that make content load
#Some content has interactive multiple choice structure borrow from pretest
class QuestionEngine:
    def __init__(self, json_path):
        self.json_path = json_path
        self.lesson_data = self.load_json()
        self.sections = self.lesson_data.get("content", [])
        self.results = []

    def load_json(self):
        with open(self.json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def has_questions(self, section):
        
        return "questions" in section and len(section["questions"]) > 0

    def randomize_options(self, options, answer):
        
        shuffled = options[:]
        random.shuffle(shuffled)
        new_correct_index = shuffled.index(answer)
        return shuffled, new_correct_index

    def run_section(self, section):
        print(f"\n--- {section['heading']} ---")

        for q in section["questions"]:
            question_text = q["question"]
            options = q["options"]
            answer = q["answer"]

            # Shuffle options
            shuffled_options, correct_index = self.randomize_options(
                options,
                answer
            )

            # Display Question
            print(f"\n{question_text}")
            for i, op in enumerate(shuffled_options):
                print(f"{i+1}. {op}")

            # User answer
            while True:
                try:
                    user_choice = int(input("Choose an option ")) - 1
                    if 0 <= user_choice < len(shuffled_options):
                        break
                except ValueError:
                    pass
                print("Try again. Keyser sees invalid input.")

            # Grade
            is_correct = (user_choice == correct_index)

            self.results.append({
                "question": question_text,
                "chosen": shuffled_options[user_choice],
                "correct": answer,
                "is_correct": is_correct
            })

    def run_quiz(self):
        print("Keyser is cooking your questions")

        for section in self.sections:
            if not self.has_questions(section):
                # Skip empty sections
                continue

            # Run normally if it has questions
            self.run_section(section)

        self.finish()

    def finish(self):
        print("Keyser has graded you")
        correct = sum(1 for r in self.results if r["is_correct"])
        total = len(self.results)

        print(f"Score: {correct}/{total} correct")

        print("Keyser explains what you were or were not mistaken in")
        for r in self.results:
            status = "Correct" if r["is_correct"] else "Incorrect"
            print(f"\n{status}")
            print(f"Q: {r['question']}")
            print(f"Selected answer: {r['chosen']}")
            print(f"Correct answer: {r['correct']}")
#Under the content load it's sources
#Meow <3