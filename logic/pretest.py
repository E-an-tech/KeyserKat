# pretest.py
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
from kivy.uix.scrollview import ScrollView
import time

from main import MainScreen



# === File setup ===
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "pretest_physics.json")
USED_QUESTIONS_FILE = os.path.join(SCRIPT_DIR, "used_questions.json")
USER_ANSWERS_FILE = os.path.join(SCRIPT_DIR, "user_answers.json")

# === Load question pool ===
with open(JSON_PATH, "r", encoding="utf-8") as f:
    pool = json.load(f)


# === Select questions for this pretest ===
MAX_TOTAL_QUESTIONS = 12
MAX_PER_UNIT = 2
selected_questions = []
all_candidates = []

# Track used questions
if os.path.exists(USED_QUESTIONS_FILE):
    with open(USED_QUESTIONS_FILE, "r") as f:
        used_questions = json.load(f)
else:
    used_questions = []

# Step 1: collect candidates per unit
for unit_key, questions in pool.items():
    remaining = [q for q in questions if q.get("question") not in used_questions]
    if len(remaining) < MAX_PER_UNIT:
        used_questions = []  # reset if not enough unused
        remaining = questions[:]
    chosen = random.sample(remaining, min(MAX_PER_UNIT, len(remaining)))
    for q in chosen:
        q["unit"] = unit_key
    all_candidates.extend(chosen)

# Step 2: limit total questions
if len(all_candidates) > MAX_TOTAL_QUESTIONS:
    selected_questions = random.sample(all_candidates, MAX_TOTAL_QUESTIONS)
else:
    selected_questions = all_candidates[:]

# Step 3: save used questions
for q in selected_questions:
    used_questions.append(q.get("question"))

with open(USED_QUESTIONS_FILE, "w", encoding="utf-8") as f:
    json.dump(used_questions, f, indent=2)



# Track used questions (optional)
if os.path.exists(USED_QUESTIONS_FILE):
    with open(USED_QUESTIONS_FILE, "r") as f:
        used_ids = set(json.load(f))
else:
    used_ids = set()

# Helper to normalize strings
def normalize(s):
    return "".join(s.lower().strip().split())

# === Kivy Screens ===

class PreTestScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)
        layout.add_widget(Label(text="Welcome to the Pre-Test!", font_size=24))
        start_btn = Button(text="Start Quiz", size_hint=(1, 0.15))
        start_btn.bind(on_release=lambda *a: self.start_quiz())
        layout.add_widget(start_btn)
        self.add_widget(layout)

    def start_quiz(self):
        app = App.get_running_app()
        app.start_quiz_timer()   # <-- start the timer here
        print("Quiz started at:", app.start_time) 

        if selected_questions:
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = "question_0"
        else:
            popup = Popup(title="No questions",
                        content=Label(text="No pretest questions found."),
                        size_hint=(0.6,0.3))
            popup.open()



class QuestionScreen(Screen):
    
    def __init__(self, question_data, index, **kwargs):
        super().__init__(**kwargs)
        self.question_data = question_data
        self.index = index
        self.answer_input = None
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation="vertical", padding=16, spacing=12)

        scroll = ScrollView(size_hint=(1, 0.6))
        self.question_label = Label(
            text=f"Q{self.index + 1}: {self.question_data.get('question','')}",
            halign="left",
            valign="top",
            size_hint_y=None,
            font_size=20,
            text_size=(None, None),  # initial, will update dynamically
        )
        scroll.add_widget(self.question_label)
        layout.add_widget(scroll)

        # Function to wrap text and adjust height
        def update_label_wrap(*args):
            # Use scroll.width (or layout.width) minus padding
            width = scroll.width - 20
            self.question_label.text_size = (width, None)
            self.question_label.texture_update()
            self.question_label.height = self.question_label.texture_size[1]

        # Bind to ScrollView width and question text
        scroll.bind(width=update_label_wrap)
        self.question_label.bind(texture_size=update_label_wrap)

        # Initial update
        Clock.schedule_once(lambda dt: update_label_wrap(), 0)

        # Multiple-choice options
        if "options" in self.question_data and self.question_data["options"]:
            for opt in self.question_data["options"]:
                btn = Button(text=opt, size_hint_y=None, height=50)
                btn.bind(on_release=self.check_answer)
                layout.add_widget(btn)
        else:
            self.answer_input = TextInput(
                hint_text="Type your answer...",
                multiline=False,
                size_hint_y=None,
                height=50
            )
            layout.add_widget(self.answer_input)
            submit = Button(text="Submit Answer", size_hint_y=None, height=44)
            submit.bind(on_release=self.check_answer)
            layout.add_widget(submit)

        print("OPTIONS FOUND:", self.question_data.get("options"))

        self.add_widget(layout)


    def check_answer(self, instance):
 
        print(">>> check_answer triggered")

        app = App.get_running_app()

        user_answer = instance.text.strip() if hasattr(instance, "text") else self.answer_input.text.strip()
        correct_answer = self.question_data.get("answer")

        correct = normalize(user_answer) == normalize(correct_answer)

        print("CHECK_ANSWER RAN:", user_answer, correct)

        app.answers.append({
            "question": self.question_data.get("question"),
            "user_answer": user_answer,
            "correct": correct,
            "unit": self.question_data.get("unit")
        })

        popup = Popup(
            title="Result",
            content=Label(text="Correct!" if correct else f"Wrong!\nAnswer: {correct_answer}"),
            size_hint=(0.6, 0.3)
        )
        popup.open()

        Clock.schedule_once(lambda dt: self.next_screen(popup), 1.5)


    def next_screen(self, popup):
        popup.dismiss()
        app = App.get_running_app()
        if self.index + 1 < len(selected_questions):
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = f"question_{self.index + 1}"
        else:
            # Save used questions
            used_ids.update([q["question"] for q in selected_questions])
            with open(USED_QUESTIONS_FILE, "w") as f:
                json.dump(list(used_ids), f)

            # Save user answers
            with open(USER_ANSWERS_FILE, "w") as f:
                json.dump(app.answers, f, indent=2)

            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = "done"


class DoneScreen(Screen):
    def on_enter(self):
        self.clear_widgets()

        app = App.get_running_app()
        total_time = app.finish_quiz_timer()  # in seconds
        minutes, seconds = divmod(int(total_time), 60)

        layout = BoxLayout(orientation="vertical", padding=16, spacing=12)
        total = len(app.answers)
        correct_count = sum(1 for a in app.answers if a["correct"])

        label = Label(
            text=f"Quiz Complete!\nScore: {correct_count}/{total}\nTime: {minutes}m {seconds}s",
            font_size=22,
            halign="center",
            valign="middle"
        )
        label.text_size = (self.width - 40, None)  # allow wrapping
        layout.add_widget(label)
        self.add_widget(layout)

        # Only go back after 4-5 seconds so you can see it
        Clock.schedule_once(lambda dt: setattr(self.manager, "current", "main"), 5.0)



class PretestApp(App):
    def build(self):
        self.answers = []
        self.score = 0 
        self.start_time = None
        self.end_time = None

        sm = ScreenManager(transition=SlideTransition())  # create the manager first

        # Add screens
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(PreTestScreen(name="pretest"))
        for i, q in enumerate(selected_questions):
            sm.add_widget(QuestionScreen(q, i, name=f"question_{i}"))
        sm.add_widget(DoneScreen(name="done"))

        return sm


    def start_quiz_timer(self):
        self.start_time = time()

  
    def finish_quiz_timer(self):
        if not self.start_time:
            return 0
        return time() - self.start_time


if __name__ == "__main__":
    PretestApp().run()
