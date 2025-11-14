from screens.course_screen import CourseScreen
from screens.unit_screen import UnitScreen
from screens.lesson_screen import LessonScreen
from screens.lesson_detail_screen import LessonDetailScreen

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.core.text import LabelBase
from kivy.config import Config
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.stencilview import StencilView
from kivy.animation import Animation
from kivy.graphics import StencilPush, StencilUse, StencilUnUse, StencilPop, Rectangle
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
import json, os, random
import os
import json



# Force portrait mode
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'resizable', True)

# Register custom font
LabelBase.register(
    name="SamulFont",
    fn_regular="C:/Windows/Fonts/H2SA1M.TTF"
)


class MyScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Storage for navigation
        self.selected_course = None
        self.selected_unit = None



# === File setup ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "data", "pretest_physics.json")
USED_QUESTIONS_FILE = os.path.join(BASE_DIR,"logic", "used_questions.json")

# === Load question pool ===
with open(JSON_PATH, "r", encoding="utf-8") as f:
    question_pool = json.load(f)

# === Load question pool ===
with open(JSON_PATH, "r", encoding="utf-8") as f:
    question_pool = json.load(f)

# === Load used questions ===
if os.path.exists(USED_QUESTIONS_FILE):
    with open(USED_QUESTIONS_FILE, "r", encoding="utf-8") as f:
        used_questions = json.load(f)
else:
    used_questions = []

# === Pick 2 random questions per unit ===
import random

selected_questions = []

for unit, questions in question_pool.items():
    # Filter out already used questions from this unit
    remaining = [q for q in questions if q["question"] not in used_questions]

    # Reset if not enough new questions in this unit
    if len(remaining) < 2:
        used_questions = []
        remaining = questions

    # Pick 2 random questions (or all if less than 2 exist)
    chosen = random.sample(remaining, min(2, len(remaining)))

    # Add unit name to each
    for q in chosen:
        q["unit"] = unit
        selected_questions.append(q)
        used_questions.append(q["question"])

# Save updated used questions
with open(USED_QUESTIONS_FILE, "w", encoding="utf-8") as f:
    json.dump(used_questions, f, indent=2)



# === Save used questions ===
for q in selected_questions:
    used_questions.append(q["question"])

with open(USED_QUESTIONS_FILE, "w", encoding="utf-8") as f:
    json.dump(used_questions, f, indent=2)


# Initialize answers and score
user_answers = {}
score = 0


class PreTestScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

        layout.add_widget(Label(text="Welcome to the Pre-Test!", font_size=24))

        start_btn = Button(text="Start Quiz", size_hint=(1, 0.2))
        start_btn.bind(on_release=self.start_quiz)
        layout.add_widget(start_btn)

        self.add_widget(layout)

    def start_quiz(self, instance):
        # Switch to the first question screen
        self.manager.current = "question_0"

# === SCREENS ===
class QuestionScreen(Screen):
    def __init__(self, question_data, index, **kwargs):
        super().__init__(**kwargs)
        self.question_data = question_data
        self.index = index
        self.correct_keywords = [word.lower() for word in question_data["answer"]]
        self.answer_input = None
        self.build_ui()

    def build_ui(self):
        from kivy.uix.scrollview import ScrollView
        from kivy.core.window import Window

        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        # Scrollable area for long questions
        scroll = ScrollView(size_hint=(1, 0.6))

        # Label for the question text
        self.question_label = Label(
            text=f"Q{self.index+1}: {self.question_data['question']}",
            halign="left",
            valign="top",
            font_size=25,
            color=(1, 1, 1, 1),
            size_hint_y=None,
        )

        # Make label height fit its content
        self.question_label.bind(
            texture_size=lambda instance, value: setattr(instance, "height", value[1])
        )

        # Function to update text wrapping dynamically
        def update_text_size(*args):
            self.question_label.text_size = (Window.width - 40, None)
            self.question_label.font_size = Window.width * 0.05  # scales font size

        # Initial setup + auto-adjust when window resizes
        update_text_size()
        Window.bind(size=update_text_size)

        scroll.add_widget(self.question_label)
        layout.add_widget(scroll)

        # === Multiple choice or open-ended ===
        if "options" in self.question_data:
            for option in self.question_data["options"]:
                btn = Button(text=option, size_hint_y=None, height=50)
                btn.bind(on_press=self.check_multiple_choice)
                layout.add_widget(btn)
        else:
            self.answer_input = TextInput(
                hint_text="Type your answer...",
                multiline=False,
                size_hint_y=None,
                height=50,
            )
            layout.add_widget(self.answer_input)

            submit_btn = Button(text="Submit Answer", size_hint_y=None, height=50)
            submit_btn.bind(on_press=self.check_open_ended)
            layout.add_widget(submit_btn)

        self.add_widget(layout)

    def check_multiple_choice(self, instance):
        global score
        user_answer = instance.text.strip().lower()
        correct = [a.lower() for a in self.question_data["answer"]]
        if user_answer in correct:
            score += 1
            self.show_popup("Correct!")
        else:
            self.show_popup("Wrong!")

        user_answers[self.question_data["question"]] = instance.text
        Clock.schedule_once(lambda dt: self.go_next(), 1.5)

    def check_open_ended(self, instance):
        global score
        if not self.answer_input:
            return
        user_answer = self.answer_input.text.strip().lower()

        # Keyword check
        correct = any(keyword in user_answer for keyword in self.correct_keywords)
        if correct:
            score += 1
            self.show_popup("Correct!")
        else:
            self.show_popup("Wrong!")

        user_answers[self.question_data["question"]] = self.answer_input.text
        Clock.schedule_once(lambda dt: self.go_next(), 1.5)

    def show_popup(self, message):
        popup = Popup(title="Result", content=Label(text=message),
                      size_hint=(0.4, 0.3), auto_dismiss=True)
        popup.open()

    def go_next(self):
        app = App.get_running_app()
        sm = app.root
        if self.index + 1 < len(selected_questions):
            sm.transition = SlideTransition(direction="left")
            sm.current = f"question_{self.index + 1}"  # <- use 'question_' prefix
        else:
            sm.transition = SlideTransition(direction="left")
            sm.current = "done"

class DoneScreen(Screen):
    def on_enter(self):
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        result_label = Label(
            text=f"Quiz Complete!\nYour score: {score}/{len(selected_questions)}",
            halign="center"
        )
        layout.add_widget(result_label)
        self.add_widget(layout)

        # Save answers
        with open("user_answers.json", "w", encoding="utf-8") as f:
            json.dump(user_answers, f, indent=2)

        # Automatically return to main screen after 3 seconds
        Clock.schedule_once(self.go_to_main, 3)

    def go_to_main(self, dt):
        self.manager.current = "main"


class PretestApp(App):
      def build(self):
        sm = ScreenManager()
        sm.add_widget(PreTestScreen(name="pretest"))

        # add question screens
        for i, q in enumerate(selected_questions):
            sm.add_widget(QuestionScreen(name=f"question_{i}", question_data=q, index=i))

        sm.add_widget(DoneScreen(name="done"))

        sm.current = "pretest"
        return sm



class CoursesScreen(Screen):
    def load_course(self, course_id):
        print("Loaded course:", course_id)



class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Clothes + titles
        self.clothes_index = 0
        self.clothes_images = ["assets/clothes2.png", "assets/clothes1.png"]
        self.course_titles = ["Statistics and Probability", "Physics"]

        self.start_x = 0  # swipe detection

        layout = FloatLayout()

        # Transparent red rectangle (animation boundary)
        with layout.canvas.after:
            Color(0, 0, 0, 0)  # red with transparency
            self.transition_box = Rectangle()

        # Function to center and resize rectangle
        def update_box(*args):
            box_width = Window.width * 0.595   # same ratio as cat container
            box_height = Window.height * 0.35
            box_x = (Window.width - box_width) / 2
            box_y = (Window.height - box_height) / 2
            self.transition_box.pos = (box_x, box_y)
            self.transition_box.size = (box_width, box_height)

        # Initial and responsive update
        update_box()
        Window.bind(size=update_box)


        # Mirror background
        self.mirror = Image(
            source="assets/mirror_bg.png",
            size_hint=(1, 0.9),
            pos_hint={"center_x": 0.5, "center_y": 0.50}
        )
        layout.add_widget(self.mirror)

        # Title label
        self.title_label = Label(
            text=self.course_titles[self.clothes_index],
            font_size="23sp",
            font_name="SamulFont",
            size_hint=(1, 0.1),
            pos_hint={"center_x": 0.5, "top": 0.97},
            halign="center",
            valign="middle"
        )
        self.title_label.bind(size=self.title_label.setter("text_size"))
        layout.add_widget(self.title_label)

        # Container for cat + clothes (relative to mirror)
        self.cat_container = FloatLayout(
            size_hint=(0.55, 0.55),  # same as mirror
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        # Cat image (bottom layer)
        self.cat = Image(
            source="assets/cat_static.png",
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        self.cat_container.add_widget(self.cat)

        # Clothes image (top layer)
        self.clothes = Image(
            source=self.clothes_images[self.clothes_index],
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        self.cat_container.add_widget(self.clothes)

        # Add container to main layout
        layout.add_widget(self.cat_container)

        # Bottom buttons
        buttons = BoxLayout(
            size_hint=(1, 0.1),
            pos_hint={"x": 0, "y": 0},
            orientation="horizontal",
            padding=[10, 0, 10, 0],
            spacing=10
        )

        btn_settings = Button(background_normal="assets/settings.png", size_hint=(None, None), size=(110, 110))
        btn_crown    = Button(background_normal="assets/crown.png", size_hint=(None, None), size=(110, 110))
        btn_support  = Button(background_normal="assets/support.png", size_hint=(None, None), size=(110, 110))

        btn_settings.bind(on_press=self.go_to_settings)
        btn_crown.bind(on_press=self.go_to_leaderboard)
        btn_support.bind(on_press=self.go_to_support)

        # Spacer widgets
        buttons.add_widget(Widget(size_hint_x=1))
        buttons.add_widget(btn_settings)
        buttons.add_widget(Widget(size_hint_x=1))
        buttons.add_widget(btn_crown)
        buttons.add_widget(Widget(size_hint_x=1))
        buttons.add_widget(btn_support)
        buttons.add_widget(Widget(size_hint_x=1))

        layout.add_widget(buttons)
        self.add_widget(layout)

    # Swipe detection
    def on_touch_down(self, touch):
        self.start_x = touch.x
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        dx = touch.x - self.start_x
        
        # 1. Detect swipe
        if abs(dx) > 50:
            if dx < 0:
                self.next_clothes()
            else:
                self.prev_clothes()
            return super().on_touch_up(touch)

        # 2. Detect TAP on the clothes image (open course)
        if self.clothes.collide_point(*touch.pos):
            self.open_current_course()
            return True

        return super().on_touch_up(touch)


    # Clothes switching
    def switch_clothes(self, new_index, direction="left"):
        if new_index == self.clothes_index:
            return
        self.clothes.source = self.clothes_images[new_index]
        self.title_label.text = self.course_titles[new_index]
        self.clothes_index = new_index


    def next_clothes(self):
        new_index = (self.clothes_index + 1) % len(self.clothes_images)
        self.switch_clothes(new_index)

    def prev_clothes(self):
        new_index = (self.clothes_index - 1) % len(self.clothes_images)
        self.switch_clothes(new_index)


    def open_current_course(self):
        course_id = self.clothes_index + 1
        self.manager.get_screen("courses").go_to_course(course_id)
        self.manager.current = "courses"



    # Navigation buttons
    def go_to_settings(self, instance):
        self.manager.current = "settings"

    def go_to_leaderboard(self, instance):
        self.manager.current = "leaderboard"

    def go_to_support(self, instance):
        self.manager.current = "support"






class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        layout.add_widget(Label(text="Settings Page", font_name="SamulFont", font_size=50))
        btn_back = Button(text="Go Back", font_name="SamulFont", size_hint=(None, None), font_size=35, size=(200, 100),
                          pos_hint={"center_x": 0.5})
        btn_back.bind(on_press=self.go_back)
        layout.add_widget(btn_back)
        self.add_widget(layout)

    def go_back(self, instance):
        self.manager.current = "main"


class LeaderboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        layout.add_widget(Label(text="Leaderboard Page", font_name="SamulFont", font_size=50))
        btn_back = Button(text="Go Back", font_name="SamulFont", size_hint=(None, None), font_size=35, size=(200, 100),
                          pos_hint={"center_x": 0.5})
        btn_back.bind(on_press=self.go_back)
        layout.add_widget(btn_back)
        self.add_widget(layout)

    def go_back(self, instance):
        self.manager.current = "main"


class SupportScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        layout.add_widget(Label(text="Support Us Page", font_name="SamulFont", font_size=50))
        btn_back = Button(text="Go Back", font_name="SamulFont", size_hint=(None, None), font_size=35, size=(200, 100),
                          pos_hint={"center_x": 0.5})
        btn_back.bind(on_press=self.go_back)
        layout.add_widget(btn_back)
        self.add_widget(layout)

    def go_back(self, instance):
        self.manager.current = "main"


class CourseSelectScreen(Screen):
    """
    Shows a placeholder course list.
    Your cat clothing press event will call go_to_course(course_id).
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # This *is* the correct title label
        self.title_label = Label(text="Select a Course", font_size=30)
        layout.add_widget(self.title_label)

        # Example button – you will replace it with the cat interaction
        btn = Button(text="Example Course", size_hint=(1, 0.2))
        btn.bind(on_release=lambda *a: self.go_to_course("Physics"))
        layout.add_widget(btn)

        self.add_widget(layout)

    def go_to_course(self, course_id):
        print(f"Loaded course: {course_id}")

        app = App.get_running_app()
        app.selected_course = course_id

        # Store the selected course inside THIS screen
        self.selected_course = course_id

        # Update your UI title (you already have this)
        self.title_label.text = f"Course: {course_id}"

        # Tell UnitListScreen which course was selected
        if "units" in self.manager.screen_names:
            unit_screen = self.manager.get_screen("units")

            # If UnitListScreen has load_units(), send the course here
            if hasattr(unit_screen, "load_units"):
                unit_screen.load_units(course_id)
            else:
                print("⚠ UnitListScreen exists but has NO load_units(course_id) function.")

            # Then switch screens
            self.manager.current = "units"
        else:
            print("⚠ WARNING: No 'units' screen added to ScreenManager.")


class UnitListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        self.title = Label(text="Units", size_hint=(1, 0.1))
        self.layout.add_widget(self.title)

        self.unit_btn = Button(text="Unit 1", size_hint=(1, 0.2))
        self.unit_btn.bind(on_release=lambda *a: self.open_unit(1))
        self.layout.add_widget(self.unit_btn)

        self.add_widget(self.layout)

    def on_pre_enter(self):
        app = App.get_running_app()
        # Make sure selected_course exists
        course = app.selected_course
        self.title.text = f"{course} — Units"

    def open_unit(self, unit_number):
        self.manager.selected_unit = unit_number
        self.manager.current = "lessons"



class LessonListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        self.title = Label(text="Lessons", size_hint=(1,0.1))
        layout.add_widget(self.title)

        btn = Button(text="Lesson 1", size_hint=(1,0.2))
        btn.bind(on_release=lambda *a: self.open_lesson(1))
        layout.add_widget(btn)

        self.add_widget(layout)

    def on_pre_enter(self):
        course = self.manager.selected_course
        unit = self.manager.selected_unit
        self.title.text = f"{course} — Unit {unit} — Lessons"

    def open_lesson(self, lesson_number):
        self.manager.selected_lesson = lesson_number
        self.manager.current = "lesson_view"



class LessonScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Title
        self.header = Label(text="", size_hint=(1,0.1))
        layout.add_widget(self.header)

        # Time estimate
        self.time_label = Label(text="5 min read", size_hint=(1,0.1))
        layout.add_widget(self.time_label)

        # Scroll area
        from kivy.uix.scrollview import ScrollView
        scroll = ScrollView(size_hint=(1,0.6))
        self.lesson_label = Label(size_hint_y=None, text="", markup=True)
        self.lesson_label.bind(texture_size=lambda *a: setattr(self.lesson_label, "height", self.lesson_label.texture_size[1]))
        scroll.add_widget(self.lesson_label)
        layout.add_widget(scroll)

        # Buttons bottom row
        btn_row = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1,0.15))

        flash_btn = Button(text="Flashcards")
        quiz_btn = Button(text="Quiz")
        pomo_btn = Button(text="Pomodoro")

        flash_btn.bind(on_release=lambda *a: print("FLASHCARDS"))
        quiz_btn.bind(on_release=lambda *a: print("QUIZ"))
        pomo_btn.bind(on_release=lambda *a: print("POMODORO"))

        btn_row.add_widget(flash_btn)
        btn_row.add_widget(quiz_btn)
        btn_row.add_widget(pomo_btn)

        layout.add_widget(btn_row)

        self.add_widget(layout)

    def on_pre_enter(self):
        c = self.manager.selected_course
        u = self.manager.selected_unit
        l = self.manager.selected_lesson

        self.header.text = f"{c} — Unit {u} — Lesson {l}"
        self.lesson_label.text = "Put your lesson text here.\nYou can load from a file or a dict later."



class MyApp(App):
    def build(self):
        sm = ScreenManager()

        # Add pretest screens
        sm.add_widget(PreTestScreen(name="pretest"))
        for i, q in enumerate(selected_questions):
            sm.add_widget(QuestionScreen(name=f"question_{i}", question_data=q, index=i))
        sm.add_widget(DoneScreen(name="done"))

        # Add main app screens
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(LeaderboardScreen(name="leaderboard"))
        sm.add_widget(SupportScreen(name="support"))


        # ➜ Add new course → units → lessons → lesson view screens
        sm.add_widget(CourseSelectScreen(name="courses"))
        sm.add_widget(UnitListScreen(name="units"))
        sm.add_widget(LessonListScreen(name="lessons"))
        sm.add_widget(LessonScreen(name="lesson_view"))

        # Decide what screen to show first
        sm.current = "pretest"  # or "main" if you want to start in main UI
        return sm
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_course = None
        self.selected_unit = None


if __name__ == "__main__":
    MyApp().run()
