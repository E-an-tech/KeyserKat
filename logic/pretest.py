# main.py
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



# === File setup ===
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "data", "pretest_physics.json"))
USED_QUESTIONS_FILE = os.path.join(SCRIPT_DIR, "used_questions.json")

# === Load question pool ===
with open(JSON_PATH, "r", encoding="utf-8") as f:
    pool = json.load(f)

def make_id(unit, category, index):
    return f"{unit}|{category}|{index}"

# === Used question tracking ===
if os.path.exists(USED_QUESTIONS_FILE):
    with open(USED_QUESTIONS_FILE, "r") as f:
        used_ids = set(json.load(f))
else:
    used_ids = set()

# === Select Questions ===
target_counts = {"Application": 2, "Theory": 2, "Analysis": 2}
current_counts = {"Application": 0, "Theory": 0, "Analysis": 0}
selected_questions = []

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

if len(selected_questions) < 6:
    raise Exception("Not enough questions. Restart the app.")

random.shuffle(selected_questions)


# === Kivy Screens ===


class QuestionScreen(Screen):
    def __init__(self, question_data, index, **kwargs):
        super().__init__(**kwargs)
        self.question_data = question_data
        self.index = index
        self.selected_answer = None

        layout = BoxLayout(orientation="vertical", spacing=10, padding=20)
        layout.add_widget(Label(text=question_data["question"], font_size=18))

        if "options" in question_data:
            # Create a button for each option
            for opt in question_data["options"]:
                btn = Button(text=opt, size_hint_y=None, height=40)
                btn.bind(on_release=self.option_selected)
                layout.add_widget(btn)
        else:
            self.text_input = TextInput(hint_text="Type your answer", multiline=False, size_hint_y=None, height=40)
            layout.add_widget(self.text_input)
            btn = Button(text="Submit", size_hint_y=None, height=40)
            btn.bind(on_release=self.written_submit)
            layout.add_widget(btn)

        self.add_widget(layout)

    def option_selected(self, instance):
        self.selected_answer = instance.text.strip()
        self.submit_answer()

    def written_submit(self, _):
        self.selected_answer = self.text_input.text.strip()
        self.submit_answer()

    def submit_answer(self):
        q = self.question_data
        user_input = self.selected_answer
        correct = False

        # Check multiple-choice
        if "options" in q:
            if isinstance(q["answer"], list):
                correct = user_input.lower() in [a.lower() for a in q["answer"]]
            else:
                correct = user_input.lower() == q["answer"].lower()
        # Check open-ended with keywords
        elif isinstance(q.get("answer"), list):
            for keyword in q["answer"]:
                if keyword.strip().lower() in user_input.lower():
                    correct = True
                    break

        # Save answer
        app = App.get_running_app()
        app.answers.append({
            "question_id": q["id"],
            "user_answer": user_input,
            "correct": correct,
            "unit_hidden": q["unit"],
            "original_question": q["question"]
        })

        # Show popup result
        popup = Popup(
            title="Answer Result",
            content=Label(text="Correct!" if correct else "Wrong!"),
            size_hint=(None, None),
            size=(300, 200)
        )
        popup.open()

        # Close popup & go to next question after 1.5s
        def next_screen_callback(dt):
            popup.dismiss()
            if self.index + 1 < len(app.questions):
                app.sm.current = f"question_{self.index+1}"
            else:
                app.sm.current = "done"

        Clock.schedule_once(next_screen_callback, 1.5)


class DoneScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        self.add_widget(self.layout)

    def on_enter(self):
        self.layout.clear_widgets()

        app = App.get_running_app()
        correct_count = sum(1 for a in app.answers if a["correct"])
        total = len(app.answers)

        self.layout.add_widget(Label(
            text=f"You scored {correct_count} out of {total}",
            font_size=20
        ))

        save_btn = Button(text="Save Answers", size_hint_y=None, height=50)
        save_btn.bind(on_release=self.save_answers)
        self.layout.add_widget(save_btn)

    def save_answers(self, _):
        app = App.get_running_app()
        with open(USED_QUESTIONS_FILE, "w") as f:
            json.dump(list(used_ids), f)
        with open("user_answers.json", "w") as f:
            json.dump(app.answers, f, indent=2)

        self.layout.add_widget(Label(text="Answers saved! Keyser is proud."))



class PretestApp(App):
    def build(self):
        self.answers = []
        self.questions = selected_questions
        self.sm = ScreenManager(transition=SlideTransition())

        for i, q in enumerate(self.questions):
            screen = QuestionScreen(q, i, name=f"question_{i}")
            self.sm.add_widget(screen)

        self.sm.add_widget(DoneScreen(name="done"))
        return self.sm


if __name__ == "__main__":
    PretestApp().run()
