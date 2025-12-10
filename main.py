#Our son <3
#main.py
from logic.lesson_engine import parse_lesson_for_app  # add at top
import os
import json
import random
from kivy.config import Config
from kivy.core.text import LabelBase
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.anchorlayout import AnchorLayout
from time import time
from kivy.uix.switch import Switch



from level_loader import LEVELS



#Development convenience
from kivy.core.window import Window


#Background
from kivy.graphics import Color, Rectangle


# ---------- Appearance / config ----------
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'resizable', True)

# register a font if available (optional)
try:
    LabelBase.register(name="SamulFont", fn_regular="C:/Windows/Fonts/H2SA1M.TTF")
    
except Exception:
    pass

# ---------- Paths ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGIC_DIR = os.path.join(BASE_DIR, "logic")
COURSES_INDEX = os.path.join(DATA_DIR, "levels.json")  # master index of courses
PRETEST_FILE = os.path.join(DATA_DIR, "pretest_physics.json")  # your pretest pool
USED_QUESTIONS_FILE = os.path.join(LOGIC_DIR, "used_questions.json")
USER_ANSWERS_FILE = os.path.join(LOGIC_DIR, "user_answers.json")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGIC_DIR, exist_ok=True)

# ---------- Utility: safe json load/save ----------
def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ---------- Load courses index (levels.json) ----------
courses_index = load_json(COURSES_INDEX)
if courses_index is None:
    raise FileNotFoundError(f"Could not find {COURSES_INDEX}. Make sure your levels.json exists in the data folder.")


    # do NOT overwrite user's file automatically; just continue with fallback

# ---------- Pretest question selection (single load, cleaned) ----------
question_pool = load_json(PRETEST_FILE, default={})  # expected dict: unit_name -> [questions]
used_questions = load_json(USED_QUESTIONS_FILE, default=[])

import random

MAX_TOTAL_QUESTIONS = 12
MAX_PER_UNIT = 2

selected_questions = []
all_candidates = []

# Step 1: collect candidates per unit
for unit_key, questions in question_pool.items():
    remaining = [q for q in questions if q.get("question") not in used_questions]
    if len(remaining) < MAX_PER_UNIT:
        used_questions = []
        remaining = questions[:]
    # pick up to MAX_PER_UNIT for this unit
    chosen = random.sample(remaining, min(MAX_PER_UNIT, len(remaining)))
    for q in chosen:
        q["unit"] = unit_key
    all_candidates.extend(chosen)

# Step 2: limit total to MAX_TOTAL_QUESTIONS
if len(all_candidates) > MAX_TOTAL_QUESTIONS:
    selected_questions = random.sample(all_candidates, MAX_TOTAL_QUESTIONS)
else:
    selected_questions = all_candidates[:]

# Step 3: save used questions
for q in selected_questions:
    used_questions.append(q.get("question"))

save_json(USED_QUESTIONS_FILE, used_questions)


# ---------- App state storages ----------
user_answers = {}  # question_text -> answer
score = 0

# ---------- Pomodoro Globals ----------
pomodoro_active = False          # Whether pomodoro is running
pomodoro_focus_minutes = 0       # Length of study phase
pomodoro_break_minutes = 0       # Length of break phase
pomodoro_seconds_left = 0        # Countdown seconds
pomodoro_in_break = False        # False = studying, True = break



# ---------- Screens ----------
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
        app.start_quiz_timer()   # <- start timer here
        if selected_questions:
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = "question_0"

class QuestionScreen(Screen):
    def __init__(self, question_data, index, **kwargs):
        super().__init__(**kwargs)
        self.question_data = question_data
        self.index = index
        # prepare canonical answers as a list of normalized answers
        raw_answer = question_data.get("answer")
        if isinstance(raw_answer, list):
            self.canonical_answers = [self._norm(a) for a in raw_answer]
        elif raw_answer is None:
            self.canonical_answers = []
        else:
            # single string answer -> keep one entry
            self.canonical_answers = [self._norm(raw_answer)]
        self.answer_input = None
        self.build_ui()

    def _norm(self, s: str) -> str:
        """Normalize strings for safe comparison:
           - lowercase
           - strip leading/trailing whitespace
           - collapse internal whitespace
           - remove common punctuation that often differs (optional)
        """
        if s is None:
            return ""
        s = str(s).lower().strip()
        # collapse whitespace
        s = " ".join(s.split())
        # remove punctuation commonly causing mismatch but keep % and - and decimal digits
        # keep digits, letters, space, percent sign, decimal point, minus, and slash
        import re
        s = re.sub(r"[^0-9a-z %\.\-\/]", "", s)
        return s

    def build_ui(self):
        layout = BoxLayout(orientation="vertical", padding=16, spacing=12)

        # keep scroll reference so update uses its width
        self.scroll = ScrollView(size_hint=(1, 0.6))
        self.question_label = Label(
            text=f"Q{self.index+1}: {self.question_data.get('question','')}",
            halign="left",
            valign="top",
            size_hint_y=None,
            font_size=20,
        )
        # don't bind height directly to texture_size yet; we update in update_question_wrap
        self.scroll.add_widget(self.question_label)
        layout.add_widget(self.scroll)


        # update function uses self.scroll.width so wrapping matches the lesson screen behavior
        def update_question_wrap(*args):
            try:
                w = max(10, self.scroll.width - 20)  # subtract padding similar to lesson screen
                self.question_label.text_size = (w, None)
                self.question_label.texture_update()
                self.question_label.height = self.question_label.texture_size[1]
            except Exception:
                pass

        # Bind to scroll width changes and label texture_size changes
        self.scroll.bind(width=update_question_wrap)
        self.question_label.bind(texture_size=lambda inst, val: update_question_wrap())

        # run once after layout settles
        Clock.schedule_once(lambda dt: update_question_wrap(), 0.05)

        # Options or input
        if "options" in self.question_data and self.question_data.get("options"):
            for opt in self.question_data.get("options", []):
                btn = Button(text=opt, size_hint_y=None, height=50)
                btn.bind(on_release=self.check_multiple_choice)
                layout.add_widget(btn)
        else:
            self.answer_input = TextInput(
                hint_text="Type your answer...",
                multiline=False,
                size_hint_y=None,
                height=50,
            )
            layout.add_widget(self.answer_input)

            submit = Button(text="Submit Answer", size_hint_y=None, height=44)
            submit.bind(on_release=self.check_open_ended)
            layout.add_widget(submit)

        self.add_widget(layout)


    def check_multiple_choice(self, instance):
        app = App.get_running_app()
        user_answer = instance.text.strip()
        user_norm = self._norm(user_answer)

        # debug print (optional)
        # print("MULTIPLE CHOICE:", user_answer, "Canonical:", self.canonical_answers)

        correct = user_norm in self.canonical_answers

        # store into the central app.answers list
        app.answers.append({
            "question": self.question_data.get("question"),
            "user_answer": user_answer,
            "correct": bool(correct),
            "unit": self.question_data.get("unit")
        })

        if correct:
            self.show_popup("Correct!")
        else:
            correct_text = self.question_data.get("answer")
            self.show_popup(f"Wrong!\nAnswer: {correct_text}")

        Clock.schedule_once(lambda dt: self.go_next(), 1.2)


    def check_open_ended(self, instance):
        global score
        if not self.answer_input:
            return
        user_answer = self.answer_input.text.strip()
        user_norm = self._norm(user_answer)

        # Strategy:
        # 1) exact normalized match (best)
        # 2) if canonical answer contains multiple words, allow 'in' matching for short synonyms
        correct = False
        if user_norm in self.canonical_answers:
            correct = True
        else:
            # allow partial match: any canonical answer token appears in user input OR vice versa
            for canon in self.canonical_answers:
                # if numeric-ish, require exact match (avoid accidental substring matches)
                if any(ch.isdigit() for ch in canon):
                    if user_norm == canon:
                        correct = True
                        break
                else:
                    # check tokens
                    canon_tokens = [t for t in canon.split() if len(t) > 1]
                    if any(tok in user_norm for tok in canon_tokens):
                        correct = True
                        break

        if correct:
            score += 1
            self.show_popup("Correct!")
        else:
            correct_text = self.question_data.get("answer")
            self.show_popup(f"Wrong!\nAnswer: {correct_text}")

        user_answers[self.question_data.get("question")] = self.answer_input.text
        Clock.schedule_once(lambda dt: self.go_next(), 1.2)

    def show_popup(self, msg):
        content = Label(
            text=msg,
            text_size=(400, None),  # max width for wrapping
            halign="center",
            valign="middle"
        )

        # Let the label expand height automatically
        content.bind(
            texture_size=lambda inst, val: setattr(inst, 'height', val[1])
        )

        # Create popup without fixed height yet
        p = Popup(
            title="Result",
            content=content,
            size_hint=(None, None),
            width=450,  # adjust as needed
            auto_dismiss=True
        )

        # Once the label texture updates, set the popup height
        def adjust_popup_height(*args):
            p.height = content.texture_size[1] + 100  # 100 for title + padding
        content.bind(texture_size=adjust_popup_height)

        # Open popup
        p.open()



    def go_next(self):
        if self.index + 1 < len(selected_questions):
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = f"question_{self.index+1}"
        else:
            # save answers (from app.answers) to file as list
            app = App.get_running_app()
            save_json(USER_ANSWERS_FILE, app.answers)
            # Also update used_ids file if you maintain used_ids elsewhere
            # used_ids.update([q["question"] for q in selected_questions])
            # with open(USED_QUESTIONS_FILE, "w") as f:
            #     json.dump(list(used_ids), f)

            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = "done"

class DoneScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        app = App.get_running_app()
        total_time = app.finish_quiz_timer()  # in seconds
        minutes, seconds = divmod(int(total_time), 60)

        layout = BoxLayout(orientation="vertical", padding=16, spacing=12)

        # Summary: score and time
        total = len(app.answers)
        correct_count = sum(1 for a in app.answers if a["correct"])
        summary_label = Label(
            text=f"Quiz Complete!\nScore: {correct_count}/{total}\nTime: {minutes}m {seconds}s",
            font_size=22,
            halign="center",
            valign="middle"
        )
        summary_label.text_size = (self.width - 40, None)
        layout.add_widget(summary_label)

        # Analyze performance per unit
        unit_scores = {}
        unit_totals = {}

        for ans in app.answers:
            unit = ans["unit"]
            unit_scores[unit] = unit_scores.get(unit, 0) + (1 if ans["correct"] else 0)
            unit_totals[unit] = unit_totals.get(unit, 0) + 1

        # Find units where the user scored <50%
        weak_units = [unit for unit in unit_scores if unit_scores[unit]/unit_totals[unit] < 0.5]

        if weak_units:
            weak_text = "You need improvement in:\n" + "\n".join(weak_units)
        else:
            weak_text = "Great job! No weak areas detected."

        weak_label = Label(
            text=weak_text,
            font_size=18,
            halign="center",
            valign="middle"
        )
        weak_label.text_size = (self.width - 40, None)
        layout.add_widget(weak_label)

        # Add button to return to main menu manually
        btn = Button(text="Return to Main Menu", size_hint=(1, 0.15))
        btn.bind(on_release=lambda x: setattr(self.manager, "current", "main"))
        layout.add_widget(btn)

        self.add_widget(layout)


# ---------- Main UI screens ----------
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.clothes_index = 0
        self.course_keys = ["statistics_probability", "physics"]
        self.course_titles = [courses_index.get(k, {}).get("title", k.replace("_"," ").title()) for k in self.course_keys]
        self.clothes_images = ["assets/clothes2.png", "assets/clothes1.png"]
        self.start_x = 0

        layout = FloatLayout()

        # ---------------- BACKGROUND COLOR ----------------
        with layout.canvas.before:
            Color(0.3, 0.3, 0.3, 0.1)  # Light grey, semi-transparent
            self.bg_rect = Rectangle(pos=(0,0), size=Window.size)

        # Update rectangle on window resize
        def update_bg_rect(*args):
            self.bg_rect.size = Window.size
        Window.bind(size=update_bg_rect)

        # ---------------- TITLE ----------------
        self.title_label = Label(
            text=self.course_titles[self.clothes_index],
            font_size="26sp",
            size_hint=(1, 0.1),
            halign="center",
            valign="middle",
            pos_hint={"top": 0.98}
        )
        self.title_label.bind(size=self.title_label.setter('text_size'))
        layout.add_widget(self.title_label)

        # ---------------- CAT + MIRROR ----------------
        self.cat_area = AnchorLayout(
            anchor_x="center",
            anchor_y="center",
            size_hint=(1, 0.7)
        )

        self.mirror = Image(
            source="assets/mirror_bg.png",
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(0.9, 0.9)
        )
        self.cat_area.add_widget(self.mirror)

        self.cat = Image(
            source="assets/cat_static.png",
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(0.45, 0.45)
        )
        self.cat_area.add_widget(self.cat)

        self.clothes = Image(
            source=self.clothes_images[self.clothes_index],
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(0.45, 0.45)
        )
        self.cat_area.add_widget(self.clothes)

        layout.add_widget(self.cat_area)

        # ---------------- BUTTON BAR ----------------
        buttons = BoxLayout(
            size_hint=(1, 0.12),
            pos_hint={"x": 0, "y": 0},
            padding=[10,0,10,0],
            spacing=8
        )
        btn_settings = Button(background_normal="assets/settings.png", size_hint=(None,None), size=(120,120))
        btn_crown = Button(background_normal="assets/crown.png", size_hint=(None,None), size=(120,120))
        btn_support = Button(background_normal="assets/support.png", size_hint=(None,None), size=(120,120))

        btn_settings.bind(on_release=lambda *a: setattr(self.manager,'current','settings'))
        btn_crown.bind(on_release=lambda *a: setattr(self.manager,'current','leaderboard'))
        btn_support.bind(on_release=lambda *a: setattr(self.manager,'current','support'))

        buttons.add_widget(Widget())
        buttons.add_widget(btn_settings)
        buttons.add_widget(Widget())
        buttons.add_widget(btn_crown)
        buttons.add_widget(Widget())
        buttons.add_widget(btn_support)
        buttons.add_widget(Widget())
        layout.add_widget(buttons)

        self.add_widget(layout)



    def on_touch_down(self, touch):
        self.start_x = touch.x
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        dx = touch.x - self.start_x
        if abs(dx) > 40:
            if dx < 0:
                self.next_clothes()
            else:
                self.prev_clothes()
            return super().on_touch_up(touch)

        if self.clothes.collide_point(*touch.pos):
            # determine course key and navigate
            course_key = self.course_keys[self.clothes_index]
            app = App.get_running_app()
            app.selected_course = course_key
            # ensure CourseSelectScreen updates
            if "courses" in self.manager.screen_names:
                cs = self.manager.get_screen("courses")
                if hasattr(cs, "go_to_course"):
                    cs.go_to_course(course_key)
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = "units"
            return True

        return super().on_touch_up(touch)

    def switch_title(self):
        self.title_label.text = self.course_titles[self.clothes_index]

    def next_clothes(self):
        self.clothes_index = (self.clothes_index + 1) % len(self.clothes_images)
        self.clothes.source = self.clothes_images[self.clothes_index]
        self.switch_title()

    def prev_clothes(self):
        self.clothes_index = (self.clothes_index - 1) % len(self.clothes_images)
        self.clothes.source = self.clothes_images[self.clothes_index]
        self.switch_title()

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=12)
        layout.add_widget(Label(text="Settings", font_size=26))
        back = Button(text="Go back", size_hint=(None,None), size=(180,80))
        back.bind(on_release=lambda *a: setattr(self.manager, "current", "main"))
        layout.add_widget(back)
        self.add_widget(layout)

class LeaderboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=12)
        layout.add_widget(Label(text="Leaderboard", font_size=26))
        back = Button(text="Go back", size_hint=(None,None), size=(180,80))
        back.bind(on_release=lambda *a: setattr(self.manager, "current", "main"))
        layout.add_widget(back)
        self.add_widget(layout)

class SupportScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=12)
        layout.add_widget(Label(text="Support Us", font_size=26))
        back = Button(text="Go back", size_hint=(None,None), size=(180,80))
        back.bind(on_release=lambda *a: setattr(self.manager, "current", "main"))
        layout.add_widget(back)
        self.add_widget(layout)

# ---------- Course / Unit / Lesson screens ----------
class CourseSelectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=12, spacing=10)
        self.title_label = Label(text="Select Course", size_hint=(1,None), height=40)
        self.layout.add_widget(self.title_label)
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=8)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll = ScrollView()
        self.scroll.add_widget(self.grid)
        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)

    def on_pre_enter(self):
        self.grid.clear_widgets()
        for key, info in courses_index.items():
            btn = Button(text=info.get("title", key), size_hint_y=None, height=60)
            btn.bind(on_release=lambda inst, k=key: self.go_to_course(k))
            self.grid.add_widget(btn)

    def go_to_course(self, course_key):
        app = App.get_running_app()
        app.selected_course = course_key
        self.title_label.text = f"{courses_index.get(course_key,{}).get('title',course_key)}"
        # load units into UnitScreen
        if "units" in self.manager.screen_names:
            unit_screen = self.manager.get_screen("units")
            if hasattr(unit_screen, "load_units"):
                unit_screen.load_units(course_key)
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "units"

# --- UNIT SCREEN ---
class UnitScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content = BoxLayout(orientation="vertical", padding=12, spacing=10)
        
        # Top bar with back button + centered title
        top_bar = FloatLayout(size_hint=(1,None), height=42)

        self.back_btn = Button(text="Back", size_hint=(None,1), width=120, pos_hint={"x":0, "y":0})
        self.back_btn.bind(on_release=self.go_back)
        top_bar.add_widget(self.back_btn)

        self.title_label = Label(text="Units", size_hint=(None,1), width=200, halign="center", valign="middle",
                                pos_hint={"center_x":0.5, "center_y":0.5})
        self.title_label.bind(size=self.title_label.setter('text_size'))
        top_bar.add_widget(self.title_label)

        self.content.add_widget(top_bar)

        
        self.grid = GridLayout(cols=1, spacing=8, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll = ScrollView()
        self.scroll.add_widget(self.grid)
        self.content.add_widget(self.scroll)
        self.add_widget(self.content)

    def go_back(self, instance):
        """Return to MainScreen"""
        if "main" in self.manager.screen_names:
            self.manager.transition = SlideTransition(direction="right")
            self.manager.current = "main" 

    def load_units(self, course_key):
        course = courses_index.get(course_key)
        if not course:
            self.title_label.text = "Course not found"
            return
        self.title_label.text = f"{course.get('title','Course')} — Units"
        self.grid.clear_widgets()
        for unit in course.get("units", []):
            btn = Button(
                text=f"Unit {unit.get('id')}: {unit.get('title')}",
                size_hint_y=None,
                height=64
            )
            btn.bind(on_release=lambda inst, u=unit: self.open_unit(u))
            self.grid.add_widget(btn)

    def open_unit(self, unit_obj):
        app = App.get_running_app()
        app.selected_unit = unit_obj.get("id")
        if "lessons" in self.manager.screen_names:
            lesson_screen = self.manager.get_screen("lessons")
            lesson_screen.load_lessons(unit_obj)
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "lessons"


def finish_session(screen, score_msg="Session complete!"):
    """Stop Pomodoro and return to lesson detail with optional score message."""
    global pomodoro_active, pomodoro_popup, pomodoro_label, pomodoro_break_popup_open, pomodoro_current_screen

    # Stop Pomodoro timer
    pomodoro_active = False
    pomodoro_break_popup_open = False

    if pomodoro_popup:
        pomodoro_popup.dismiss()
        pomodoro_popup = None
        pomodoro_label = None
        pomodoro_current_screen = None

    # Show score popup
    content = BoxLayout(orientation="vertical", padding=8, spacing=8)
    content.add_widget(Label(text=score_msg, font_size=18))
    btn_ok = Button(text="OK", size_hint=(1, None), height=50)
    content.add_widget(btn_ok)

    popup = Popup(
        title="Session Finished",
        content=content,
        size_hint=(0.7, None),
        height=200,
        auto_dismiss=False
    )

    btn_ok.bind(on_release=lambda *_: (
        popup.dismiss(),
        setattr(screen.manager, 'current', "lesson_detail")  # go back to lesson
    ))

    popup.open()

# --- LESSON LIST SCREEN ---
class LessonListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=12, spacing=10)

        # --- Top bar with back button + centered title ---
        top_bar = FloatLayout(size_hint=(1, None), height=42)

        # Back button on the left
        self.back_btn = Button(
            text="Back",
            size_hint=(None, 1),
            width=120,
            pos_hint={"x": 0, "y": 0}
        )
        self.back_btn.bind(on_release=self.go_back)
        top_bar.add_widget(self.back_btn)

        # Centered title
        self.title_label = Label(
            text="Lessons",
            size_hint=(None, 1),
            width=250,
            halign="center",
            valign="middle",
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        self.title_label.bind(size=self.title_label.setter('text_size'))
        top_bar.add_widget(self.title_label)

        self.layout.add_widget(top_bar)

        # --- Grid of lessons ---
        self.grid = GridLayout(cols=1, spacing=8, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))

        self.scroll = ScrollView()
        self.scroll.add_widget(self.grid)
        self.layout.add_widget(self.scroll)

        self.add_widget(self.layout)

    def go_back(self, instance):
        """Return to UnitScreen"""
        if "units" in self.manager.screen_names:
            self.manager.transition = SlideTransition(direction="right")
            self.manager.current = "units"


    def load_lessons(self, unit_obj):
        """Load lesson buttons for the selected unit"""
        self.title_label.text = f"{unit_obj.get('title','Unit')} — Lessons"
        self.grid.clear_widgets()
        for lesson in unit_obj.get("lessons", []):
            btn = Button(
                text=f"Lesson {lesson.get('id')}: {lesson.get('title')}",
                size_hint_y=None,
                height=64
            )
            btn.bind(on_release=lambda inst, l=lesson: self.open_lesson(l))
            self.grid.add_widget(btn)

    def open_lesson(self, lesson_obj):
        """Load JSON lesson file and go to LessonDetailScreen"""
        lesson_path = lesson_obj.get("file")  # must exist in levels.json
        if not lesson_path or not os.path.exists(lesson_path):
            print(f"[Error] Lesson JSON not found: {lesson_path}")
            return

        with open(lesson_path, "r", encoding="utf-8") as f:
            lesson_data = json.load(f)

        if "lesson_detail" in self.manager.screen_names:
            ld = self.manager.get_screen("lesson_detail")
            ld.load_lesson(lesson_data)
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = "lesson_detail"


# --- LESSON DETAIL SCREEN ---
class LessonDetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.root_layout = BoxLayout(orientation="vertical", padding=12, spacing=10)

        # Header
        self.header = Label(text="Lesson Title", size_hint=(1,None), height=42)
        self.root_layout.add_widget(self.header)

        # Time label
        self.time_label = Label(text="", size_hint=(1,None), height=28)
        self.root_layout.add_widget(self.time_label)

        # Scrollable content
        self.scroll = ScrollView(size_hint=(1,1))
        self.content_label = Label(
            text="", size_hint_y=None, markup=True, halign="left", valign="top"
        )
        self.scroll.add_widget(self.content_label)
        self.root_layout.add_widget(self.scroll)

        # Bind ScrollView width to update wrapping
        self.scroll.bind(width=lambda instance, value: self.update_label_wrap())

        # Bottom buttons layout
        bottom = BoxLayout(size_hint=(1,None), height=64, spacing=8)
        self.btn_quiz = Button(text="Quiz")
        self.btn_flash = Button(text="Flashcards")
        self.btn_pomo = Button(text="Pomodoro")
        self.btn_back = Button(text="Back")  # <-- Back button
        bottom.add_widget(self.btn_quiz)
        bottom.add_widget(self.btn_flash)
        bottom.add_widget(self.btn_pomo)
        bottom.add_widget(self.btn_back)  # add to layout
        self.root_layout.add_widget(bottom)

        # Add the layout to the screen
        self.add_widget(self.root_layout)

        # Internal storage
        self._quiz = []
        self._flashcards = []

        # Bind button events
        self.btn_quiz.bind(on_release=self.on_quiz)
        self.btn_flash.bind(on_release=self.on_flashcards)
        self.btn_pomo.bind(on_release=self.on_pomodoro)
        self.btn_back.bind(on_release=self.go_back)  # bind back button

    # --- Outside __init__() ---
    def go_back(self, instance):
        """Return to the lessons list screen"""
        if self.manager.has_screen("lessons"):
            self.manager.current = "lessons"


    def update_label_wrap(self):
        self.content_label.text_size = (self.scroll.width - 20, None)
        self.content_label.texture_update()
        self.content_label.height = self.content_label.texture_size[1]


    def parse_lesson(self, lesson_json):
        """Extract quizzes and flashcards from lesson JSON"""
        quiz = []
        flashcards = []

        for section in lesson_json.get("sections", []):
            # Flashcards: heading -> content
            heading = section.get("heading")
            content = section.get("content")
            if heading and content:
                flashcards.append({"front": heading, "back": content})

            # Quiz: problems
            for prob in section.get("problems", []):
                quiz.append({
                    "question": prob.get("question"),
                    "options": prob.get("options", []),
                    "answer": prob.get("answer")
                })
        return quiz, flashcards

    def load_lesson(self, lesson_obj):
        """Populate lesson detail screen"""
        self.header.text = lesson_obj.get("title","Lesson")
        self.time_label.text = f"Read Time: {lesson_obj.get('read_time','N/A')}"

        # Combine all section text for display
        content_text = ""
        for section in lesson_obj.get("sections", []):
            heading = section.get("heading")
            content = section.get("content")
            if heading: content_text += f"[b]{heading}[/b]\n"
            if content: content_text += f"{content}\n"
            # optional: bullet points
            for bp in section.get("bullet_points", []):
                content_text += f"• {bp}\n"
            content_text += "\n"
        self.content_label.text = content_text.strip()
        self.update_label_wrap()

        # Parse quizzes & flashcards
        self._quiz, self._flashcards = self.parse_lesson(lesson_obj)
        self.btn_quiz.disabled = not bool(self._quiz)
        self.btn_flash.disabled = not bool(self._flashcards)

    
    
    def on_quiz(self, instance):
        if self._quiz:
            app = App.get_running_app()
            if app.pomodoro_enabled:
                start_pomodoro(app.pomodoro_study_minutes, app.pomodoro_break_minutes, screen=self.manager.get_screen("quiz"))
            self.manager.get_screen("quiz").load_quiz(self._quiz)
            self.manager.current = "quiz"

    def on_flashcards(self, instance):
        if self._flashcards:
            app = App.get_running_app()
            if app.pomodoro_enabled:
                start_pomodoro(app.pomodoro_study_minutes, app.pomodoro_break_minutes, screen=self.manager.get_screen("flashcards"))
            self.manager.get_screen("flashcards").load_flashcards(self._flashcards)
            self.manager.current = "flashcards"



    def _show_msg(self, msg):
            popup = Popup(
                title="Notice",
                content=Label(text=msg),
                size_hint=(0.6, 0.3)
            )
            popup.open()

        
    def on_pomodoro(self, *a):
        app = App.get_running_app()
        
        content = BoxLayout(orientation="vertical", padding=8, spacing=8)

        focus_input = TextInput(
            text=str(app.pomodoro_study_minutes),
            input_filter="int", multiline=False,
            size_hint=(1, None), height=40
        )
        break_input = TextInput(
            text=str(app.pomodoro_break_minutes),
            input_filter="int", multiline=False,
            size_hint=(1, None), height=40
        )

        pomo_switch = Switch(active=app.pomodoro_enabled, size_hint=(1,None), height=40)
        switch_label = Label(text="Enable Pomodoro", size_hint=(1,None), height=30)

        btn_save = Button(text="Save Settings", size_hint=(1, None), height=44)

        content.add_widget(Label(text="Focus minutes:"))
        content.add_widget(focus_input)
        content.add_widget(Label(text="Break minutes:"))
        content.add_widget(break_input)
        content.add_widget(switch_label)
        content.add_widget(pomo_switch)
        content.add_widget(btn_save)

        popup = Popup(title="Pomodoro Settings", content=content, size_hint=(0.8, None), height=320)

        def save_settings(_):
            try:
                fm = int(focus_input.text)
                bm = int(break_input.text)
            except ValueError:
                popup.dismiss()
                print("Invalid minutes")
                return

            app.pomodoro_study_minutes = fm
            app.pomodoro_break_minutes = bm
            app.pomodoro_enabled = pomo_switch.active

            popup.dismiss()
            print(f"Pomodoro saved: {fm}m focus / {bm}m break — Enabled: {app.pomodoro_enabled}")

        btn_save.bind(on_release=save_settings)
        popup.open()
        



class QuizScreen(Screen):
    def load_quiz(self, questions):
        self.clear_widgets()
        self.questions = questions
        self.current = 0
        self.score = 0  # track correct answers
        self.show_question()

    def show_question(self):
        self.clear_widgets()
        if self.current >= len(self.questions):
            # Quiz complete
            total = len(self.questions)
            score_msg = f"You scored {self.score}/{total}!"

            # Stop Pomodoro and return to lesson
            app = App.get_running_app()
            finish_session(app.root.get_screen("quiz"), score_msg=score_msg)
            return

        q = self.questions[self.current]
        layout = BoxLayout(orientation="vertical", spacing=8, padding=8)
        layout.add_widget(Label(text=q["question"], font_size=20, size_hint_y=None, height=60))

        for opt in q["options"]:
            btn = Button(text=opt, size_hint_y=None, height=50)
            btn.bind(on_release=lambda x, opt=opt: self.check_answer(opt))
            layout.add_widget(btn)

        self.add_widget(layout)

    def check_answer(self, selected):
        q = self.questions[self.current]
        if selected == q["answer"]:
            print("Correct!")
            self.score += 1
        else:
            print("Wrong")
        self.current += 1
        self.show_question()


class FlashcardScreen(Screen):
    def load_flashcards(self, cards):
        self.clear_widgets()
        self.cards = cards
        self.index = 0
        self.show_card()

    def show_card(self):
        self.clear_widgets()
        if self.index >= len(self.cards):
            # Flashcards complete
            app = App.get_running_app()
            finish_session(app.root.get_screen("flashcards"), score_msg="Flashcards complete!")
            return

        card = self.cards[self.index]
        layout = BoxLayout(orientation="vertical", spacing=8, padding=8)
        front = Label(text=card["front"], font_size=24, size_hint_y=None, height=60)
        layout.add_widget(front)

        flip_btn = Button(text="Show Answer", size_hint_y=None, height=50)
        flip_btn.bind(on_release=lambda x: setattr(front, "text", card["back"]))
        next_btn = Button(text="Next", size_hint_y=None, height=50)
        next_btn.bind(on_release=lambda x: self.next_card())

        layout.add_widget(flip_btn)
        layout.add_widget(next_btn)

        self.add_widget(layout)

    def next_card(self):
        self.index += 1
        self.show_card()



pomodoro_popup = None
pomodoro_label = None
pomodoro_current_screen = None
pomodoro_break_popup_open = False
pomodoro_event = None  # global variable to track scheduled Clock

def pomodoro_tick(dt):
    global pomodoro_active, pomodoro_seconds_left, pomodoro_in_break
    global pomodoro_popup, pomodoro_break_popup_open, pomodoro_current_screen, pomodoro_label

    if not pomodoro_active:
        return

    pomodoro_seconds_left -= 1
    minutes, seconds = divmod(max(pomodoro_seconds_left, 0), 60)
    status = "Break" if pomodoro_in_break else "Focus"

    # Update timer label if exists
    if pomodoro_label:
        pomodoro_label.text = f"{status} Time: {minutes:02d}:{seconds:02d}"

    # End of current session
    if pomodoro_seconds_left <= 0:
        app = App.get_running_app()
        pomodoro_in_break = not pomodoro_in_break

        if pomodoro_in_break:
            # Start break
            pomodoro_seconds_left = app.pomodoro_break_minutes * 60

            if pomodoro_current_screen and not pomodoro_break_popup_open:
                pomodoro_break_popup_open = True

                content = BoxLayout(orientation="vertical", padding=8, spacing=8)
                pomodoro_label = Label(
                    text=f"Break Time: {app.pomodoro_break_minutes:02d}:00",
                    font_size=20
                )
                leave_btn = Button(text="Leave Quiz/Flashcards", size_hint=(1, None), height=50)
                content.add_widget(pomodoro_label)
                content.add_widget(leave_btn)

                pomodoro_popup = Popup(
                    title="Break Time",
                    content=content,
                    size_hint=(0.7, None),
                    height=200,
                    auto_dismiss=False
                )

                def leave_quiz(_):
                    global pomodoro_active, pomodoro_break_popup_open
                    pomodoro_active = False  # stop timer
                    pomodoro_break_popup_open = False
                    pomodoro_popup.dismiss()
                    # Return to lesson detail screen
                    app.root.get_screen("lesson_detail").manager.current = "lesson_detail"

                leave_btn.bind(on_release=leave_quiz)
                pomodoro_popup.open()
        else:
            # Start next focus session
            pomodoro_seconds_left = app.pomodoro_study_minutes * 60
            pomodoro_break_popup_open = False
            if pomodoro_popup:
                pomodoro_popup.dismiss()



def show_break_popup(minutes, seconds):
    """Display a blocking break popup"""
    global pomodoro_popup, pomodoro_label

    content = BoxLayout(orientation="vertical", padding=8, spacing=8)
    pomodoro_label = Label(text=f"Break Time: {minutes:02d}:{seconds:02d}", font_size=20)
    content.add_widget(pomodoro_label)

    # Disable closing by clicking outside
    pomodoro_popup = Popup(
        title="Take a Break!",
        content=content,
        size_hint=(0.7, None),
        height=200,
        auto_dismiss=False
    )
    pomodoro_popup.open()


def start_pomodoro(focus_minutes, break_minutes, screen=None):
    global pomodoro_active, pomodoro_focus_minutes, pomodoro_break_minutes
    global pomodoro_seconds_left, pomodoro_in_break
    global pomodoro_popup, pomodoro_label, pomodoro_current_screen
    global pomodoro_break_popup_open

    # Initialize Pomodoro state
    pomodoro_focus_minutes = focus_minutes
    pomodoro_break_minutes = break_minutes
    pomodoro_seconds_left = focus_minutes * 60
    pomodoro_in_break = False
    pomodoro_active = True
    pomodoro_break_popup_open = False
    pomodoro_current_screen = screen
    pomodoro_popup = None
    pomodoro_label = None

    # Terminal feedback for focus session
    minutes, seconds = divmod(pomodoro_seconds_left, 60)
    print(f"[Pomodoro] Focus session started: {minutes:02d}:{seconds:02d} remaining")

    # Start the ticking function
    Clock.schedule_interval(pomodoro_tick, 1)

    

def leave_quiz(screen):
    global pomodoro_active, pomodoro_popup, pomodoro_label, pomodoro_current_screen
    global pomodoro_break_popup_open

    pomodoro_active = False  # stop the timer
    pomodoro_break_popup_open = False

    if pomodoro_popup:
        pomodoro_popup.dismiss()
        pomodoro_popup = None
        pomodoro_label = None

    # Navigate back to lesson details
    if screen:
        screen.manager.current = "lesson_detail"
        pomodoro_current_screen = None


# ---------- Application ----------
class MyApp(App):

    pomodoro_enabled = False
    pomodoro_study_minutes = 25
    pomodoro_break_minutes = 5

    def build(self):

        self.start_time = None      # start of pretest/quiz
        self.answers = []           # track user answers

        sm = ScreenManager()

        # ADD ALL SCREENS FIRST
        sm.add_widget(PreTestScreen(name="pretest"))
        for i, q in enumerate(selected_questions):
            sm.add_widget(QuestionScreen(name=f"question_{i}", question_data=q, index=i))
        sm.add_widget(DoneScreen(name="done"))

        # main UI
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(LeaderboardScreen(name="leaderboard"))
        sm.add_widget(SupportScreen(name="support"))

        # course flow
        sm.add_widget(CourseSelectScreen(name="courses"))
        sm.add_widget(UnitScreen(name="units"))
        sm.add_widget(LessonListScreen(name="lessons"))
        sm.add_widget(LessonDetailScreen(name="lesson_detail"))
        sm.add_widget(QuizScreen(name="quiz"))
        sm.add_widget(FlashcardScreen(name="flashcards"))

        # THIS MUST COME AFTER ALL SCREENS ARE ADDED
        sm.current = "pretest"

        # store selections
        self.selected_course = None
        self.selected_unit = None
        self.pomodoro_seconds = None

        Window.bind(on_key_down=self.skip_pretest)

        return sm


# Timers and debug convenience


    def start_quiz_timer(self):
        self.start_time = time()

    def finish_quiz_timer(self):
        # safely get start_time without crashing
        start = getattr(self, "start_time", None)
        if start is None:
            return 0
        return time() - start


    def skip_pretest(self, window, key, *args):
        if key == ord('q'):
            self.root.current = "main"
            return True
        return False
    
    
if __name__ == "__main__":
    MyApp().run()