#Our son <3

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
courses_index = load_json(COURSES_INDEX, default=None)
if courses_index is None:
    # minimal fallback to keep app running; user should replace levels.json later
    courses_index = {
        "statistics_probability": {
            "title": "Statistics & Probability",
            "units": [
                {"id": 1, "title": "Descriptive Statistics", "lessons": [
                    {"id": 1, "title": "Measures of Central Tendency", "time_estimate": "5 min", "content": "<b>Mean</b> — the average...\n\nMode — the most frequent value..."},
                    {"id": 2, "title": "Spread & Variability", "time_estimate": "6 min", "content": "Variance and standard deviation..."}
                ]},
                {"id": 2, "title": "Probability Basics", "lessons": [
                    {"id": 1, "title": "Basic Probability", "time_estimate": "7 min", "content": "Events, sample spaces, P(A)..."}
                ]}
            ]
        },
        "physics": {
            "title": "Physics",
            "units": [
                {"id": 1, "title": "Motion", "lessons": [
                    {"id": 1, "title": "Kinematics", "time_estimate": "8 min", "content": "Displacement, velocity, acceleration..."}
                ]}
            ]
        }
    }
    # do NOT overwrite user's file automatically; just continue with fallback

# ---------- Pretest question selection (single load, cleaned) ----------
question_pool = load_json(PRETEST_FILE, default={})  # expected dict: unit_name -> [questions]
used_questions = load_json(USED_QUESTIONS_FILE, default=[])

selected_questions = []
if question_pool:
    # For each key in pool, pick up to 2 random unused questions
    for unit_key, questions in question_pool.items():
        remaining = [q for q in questions if q.get("question") not in used_questions]
        if len(remaining) < 2:
            # reset used list for fairness (simple policy)
            used_questions = []
            remaining = questions[:]
        chosen = random.sample(remaining, min(2, len(remaining)))
        for q in chosen:
            q["unit"] = unit_key
            selected_questions.append(q)
            used_questions.append(q.get("question"))
    save_json(USED_QUESTIONS_FILE, used_questions)

# ---------- App state storages ----------
user_answers = {}  # question_text -> answer
score = 0

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
        # go to first question
        if selected_questions:
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = "question_0"
        else:
            popup = Popup(title="No questions", content=Label(text="No pretest questions found."), size_hint=(0.6,0.3))
            popup.open()

class QuestionScreen(Screen):
    def __init__(self, question_data, index, **kwargs):
        super().__init__(**kwargs)
        self.question_data = question_data
        self.index = index
        self.correct_keywords = [w.lower() for w in (question_data.get("answer") or [])]
        self.answer_input = None
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation="vertical", padding=16, spacing=12)
        scroll = ScrollView(size_hint=(1, 0.6))
        self.question_label = Label(text=f"Q{self.index+1}: {self.question_data.get('question','')}",
                                    halign="left", valign="top", size_hint_y=None, font_size=20)
        self.question_label.bind(texture_size=lambda instance, value: setattr(instance, "height", value[1]))
        scroll.add_widget(self.question_label)
        layout.add_widget(scroll)

        if "options" in self.question_data:
            for opt in self.question_data.get("options", []):
                btn = Button(text=opt, size_hint_y=None, height=50)
                btn.bind(on_release=self.check_multiple_choice)
                layout.add_widget(btn)
        else:
            self.answer_input = TextInput(hint_text="Type your answer...", multiline=False, size_hint_y=None, height=50)
            layout.add_widget(self.answer_input)
            submit = Button(text="Submit Answer", size_hint_y=None, height=44)
            submit.bind(on_release=self.check_open_ended)
            layout.add_widget(submit)

        self.add_widget(layout)

    def check_multiple_choice(self, instance):
        global score
        user_answer = instance.text.strip()
        correct = [a.lower() for a in (self.question_data.get("answer") or [])]
        if user_answer.lower() in correct:
            score += 1
            self.show_popup("Correct!")
        else:
            self.show_popup("Wrong!")
        user_answers[self.question_data.get("question")] = user_answer
        Clock.schedule_once(lambda dt: self.go_next(), 1.2)

    def check_open_ended(self, instance):
        global score
        if not self.answer_input:
            return
        text = self.answer_input.text.strip().lower()
        if any(k in text for k in self.correct_keywords):
            score += 1
            self.show_popup("Correct!")
        else:
            self.show_popup("Wrong!")
        user_answers[self.question_data.get("question")] = self.answer_input.text
        Clock.schedule_once(lambda dt: self.go_next(), 1.2)

    def show_popup(self, msg):
        p = Popup(title="Result", content=Label(text=msg), size_hint=(0.5,0.3))
        p.open()

    def go_next(self):
        if self.index + 1 < len(selected_questions):
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = f"question_{self.index+1}"
        else:
            # save answers
            save_json(USER_ANSWERS_FILE, user_answers)
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = "done"

class DoneScreen(Screen):
    def on_enter(self):
        layout = BoxLayout(orientation="vertical", padding=16, spacing=12)
        layout.add_widget(Label(text=f"Quiz Complete!\nScore: {score}/{len(selected_questions)}", halign="center"))
        self.add_widget(layout)
        # return to main after short delay
        Clock.schedule_once(lambda dt: setattr(self.manager, "current", "main"), 2.0)

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

class UnitScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content = BoxLayout(orientation="vertical", padding=12, spacing=10)
        self.title_label = Label(text="Units", size_hint=(1,None), height=42)
        self.content.add_widget(self.title_label)
        self.grid = GridLayout(cols=1, spacing=8, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll = ScrollView()
        self.scroll.add_widget(self.grid)
        self.content.add_widget(self.scroll)
        self.add_widget(self.content)
        self._courses = courses_index

    def load_units(self, course_key):
        course = self._courses.get(course_key)
        if not course:
            self.title_label.text = "Course not found"
            return
        self.title_label.text = f"{course.get('title','Course')} — Units"
        self.grid.clear_widgets()
        for unit in course.get("units", []):
            btn = Button(text=f"Unit {unit.get('id')}: {unit.get('title')}", size_hint_y=None, height=64)
            btn.bind(on_release=lambda inst, u=unit: self.open_unit(u))
            self.grid.add_widget(btn)

    def open_unit(self, unit_obj):
        # store selection
        app = App.get_running_app()
        app.selected_unit = unit_obj.get("id")
        self.manager.selected_unit_obj = unit_obj
        # prepare LessonListScreen
        if "lessons" in self.manager.screen_names:
            lessons = self.manager.get_screen("lessons")
            if hasattr(lessons, "load_lessons"):
                lessons.load_lessons(unit_obj, app.selected_course)
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "lessons"

class LessonListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content = BoxLayout(orientation="vertical", padding=12, spacing=10)
        self.title_label = Label(text="Lessons", size_hint=(1,None), height=42)
        self.content.add_widget(self.title_label)
        self.grid = GridLayout(cols=1, spacing=8, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll = ScrollView()
        self.scroll.add_widget(self.grid)
        self.content.add_widget(self.scroll)
        self.add_widget(self.content)

    def load_lessons(self, unit_obj, course_key):
        self.title_label.text = f"{courses_index.get(course_key,{}).get('title',course_key)} — {unit_obj.get('title')}"
        self.grid.clear_widgets()
        for lesson in unit_obj.get("lessons", []):
            btn = Button(text=f"Lesson {lesson.get('id')}: {lesson.get('title')}", size_hint_y=None, height=64)
            btn.bind(on_release=lambda inst, l=lesson: self.open_lesson(l))
            self.grid.add_widget(btn)

    def open_lesson(self, lesson_obj):
        # set selection and navigate to detailed lesson view
        self.manager.selected_lesson_obj = lesson_obj
        if "lesson_detail" in self.manager.screen_names:
            ld = self.manager.get_screen("lesson_detail")
            if hasattr(ld, "load_lesson"):
                ld.load_lesson(lesson_obj)
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "lesson_detail"

class LessonDetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.root_layout = BoxLayout(orientation="vertical", padding=12, spacing=10)
        self.header = Label(text="Lesson Title", size_hint=(1,None), height=48)
        self.root_layout.add_widget(self.header)
        self.time_label = Label(text="", size_hint=(1,None), height=28)
        self.root_layout.add_widget(self.time_label)
        self.scroll = ScrollView()
        self.content_label = Label(text="", size_hint_y=None, markup=True)
        self.content_label.bind(texture_size=lambda *a: setattr(self.content_label, "height", self.content_label.texture_size[1]))
        self.scroll.add_widget(self.content_label)
        self.root_layout.add_widget(self.scroll)
        # bottom buttons: Quiz / Flashcards / Pomodoro
        bottom = BoxLayout(size_hint=(1,None), height=64, spacing=8)
        self.btn_quiz = Button(text="Quiz")
        self.btn_flash = Button(text="Flashcards")
        self.btn_pomo = Button(text="Pomodoro")
        self.btn_quiz.bind(on_release=self.on_quiz)
        self.btn_flash.bind(on_release=self.on_flashcards)
        self.btn_pomo.bind(on_release=self.on_pomodoro)
        bottom.add_widget(self.btn_quiz); bottom.add_widget(self.btn_flash); bottom.add_widget(self.btn_pomo)
        self.root_layout.add_widget(bottom)
        self.add_widget(self.root_layout)
        self.lesson_obj = None
        self._flashcards = []
        self._quiz = []

    def load_lesson(self, lesson_obj):
        self.lesson_obj = lesson_obj
        self.header.text = lesson_obj.get("title", "Lesson")
        self.time_label.text = lesson_obj.get("time_estimate", "")
        content = lesson_obj.get("content")
        # if content_file exists, try to load it relative to BASE_DIR
        cf = lesson_obj.get("content_file")
        if not content and cf:
            path = os.path.join(BASE_DIR, cf)
            if os.path.exists(path):
                try:
                    item = load_json(path, default={})
                    content = item.get("content") or json.dumps(item)
                except Exception:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
            else:
                content = f"(missing content file: {cf})"
        if not content:
            content = "No content available."
        self.content_label.text = content
        self._flashcards = lesson_obj.get("flashcards", [])
        self._quiz = lesson_obj.get("quiz", [])

    def on_quiz(self, *a):
        if self._quiz:
            # placeholder: navigate to quiz screen if you build one
            print("Starting quiz:", self._quiz)
            popup = Popup(title="Quiz", content=Label(text="Quiz not implemented yet."), size_hint=(0.6,0.3))
            popup.open()
        else:
            popup = Popup(title="Info", content=Label(text="No quiz available."), size_hint=(0.6,0.3)); popup.open()

    def on_flashcards(self, *a):
        if self._flashcards:
            print("Flashcards:", self._flashcards)
            popup = Popup(title="Flashcards", content=Label(text="Flashcards not implemented yet."), size_hint=(0.6,0.3))
            popup.open()
        else:
            popup = Popup(title="Info", content=Label(text="No flashcards."), size_hint=(0.6,0.3)); popup.open()

    def on_pomodoro(self, *a):
        content = BoxLayout(orientation="vertical", padding=8, spacing=8)
        ti = TextInput(text="25", input_filter="int", multiline=False, size_hint=(1,None), height=44)
        btn = Button(text="Set", size_hint=(1,None), height=44)
        content.add_widget(Label(text="Minutes:"))
        content.add_widget(ti)
        content.add_widget(btn)
        popup = Popup(title="Pomodoro", content=content, size_hint=(0.8,None), height=220)
        def do_set(_):
            v = ti.text.strip()
            if v.isdigit():
                app = App.get_running_app()
                app.pomodoro_seconds = int(v)*60
                popup.dismiss()
                Popup(title="Set", content=Label(text=f"Pomodoro set: {v} min"), size_hint=(0.6,0.3)).open()
            else:
                Popup(title="Error", content=Label(text="Enter minutes (int)"), size_hint=(0.5,0.25)).open()
        btn.bind(on_release=do_set)
        popup.open()

# ---------- Application ----------
class MyApp(App):
    def build(self):
        sm = ScreenManager()
        # pretest screens
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

        # start on pretest (or "main" if you prefer)
        sm.current = "pretest"

        # store selected items
        self.selected_course = None
        self.selected_unit = None
        self.pomodoro_seconds = None

        # bind key to skip pretest
        Window.bind(on_key_down=self.skip_pretest)

        return sm

    def skip_pretest(self, window, key, *args):
        if key == ord('q'):  # press Q to skip pretest
            self.root.current = "main"
            return True  # consume the key event
        return False

if __name__ == "__main__":
    MyApp().run()