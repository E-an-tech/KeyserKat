# screens/lesson_detail_screen.py
import os, json
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.clock import Clock

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class LessonDetailScreen(Screen):
    """
    Displays lesson content. Expects:
      - manager.selected_course (string key)
      - manager.selected_unit_obj (the unit object with lessons list)
      - manager.selected_lesson (integer lesson id) OR call load_lesson(lesson_obj)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.root_layout = BoxLayout(orientation="vertical", padding=12, spacing=8)
        self.header = Label(text="Lesson Title", size_hint=(1, None), height=48)
        self.root_layout.add_widget(self.header)

        # time estimate
        self.time_label = Label(text="", size_hint=(1, None), height=28)
        self.root_layout.add_widget(self.time_label)

        # scrollable content
        self.scroll = ScrollView(size_hint=(1, 1))
        self.content_label = Label(text="", size_hint_y=None, markup=True)
        self.content_label.bind(texture_size=lambda *a: setattr(self.content_label, "height", self.content_label.texture_size[1]))
        self.scroll.add_widget(self.content_label)
        self.root_layout.add_widget(self.scroll)

        # bottom buttons
        bottom = BoxLayout(size_hint=(1, None), height=64, spacing=8)
        self.btn_quiz = Button(text="Quiz")
        self.btn_flash = Button(text="Flashcards")
        self.btn_pomo = Button(text="Pomodoro")

        self.btn_quiz.bind(on_release=self.on_quiz)
        self.btn_flash.bind(on_release=self.on_flashcards)
        self.btn_pomo.bind(on_release=self.on_pomodoro)

        bottom.add_widget(self.btn_quiz)
        bottom.add_widget(self.btn_flash)
        bottom.add_widget(self.btn_pomo)
        self.root_layout.add_widget(bottom)

        self.add_widget(self.root_layout)

        # state
        self.lesson_obj = None
        self.pomodoro_seconds = None

    def on_pre_enter(self):
        # Try to resolve a lesson to show from manager fields
        # If a full lesson object is set at manager.selected_lesson_obj use it
        lesson_obj = getattr(self.manager, "selected_lesson_obj", None)
        if not lesson_obj:
            # Try to find from selected_unit_obj & selected_lesson id
            unit_obj = getattr(self.manager, "selected_unit_obj", None)
            lid = getattr(self.manager, "selected_lesson", None)
            if unit_obj and lid:
                for l in unit_obj.get("lessons", []):
                    if l.get("id") == lid:
                        lesson_obj = l
                        break

        if lesson_obj:
            self.load_lesson(lesson_obj)
        else:
            self.header.text = "No lesson selected"
            self.content_label.text = ""

    def load_lesson(self, lesson_obj):
        """
        lesson_obj should have at least: title, content_file or content, time_estimate
        """
        self.lesson_obj = lesson_obj
        self.header.text = lesson_obj.get("title", "Lesson")
        self.time_label.text = lesson_obj.get("time_estimate", "")

        # Load content either inline or from content_file
        content = lesson_obj.get("content")
        if not content and lesson_obj.get("content_file"):
            path = os.path.join(BASE_DIR, lesson_obj["content_file"])
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    try:
                        lesson_json = json.load(f)
                        content = lesson_json.get("content", "")
                    except Exception:
                        # maybe file is plain text
                        f.seek(0)
                        content = f.read()
            else:
                content = f"(missing content file: {lesson_obj['content_file']})"

        # Fallback text
        if not content:
            content = "No content available."

        # Accept markup in the content (e.g. <b>, [ref], etc.)
        self.content_label.text = content

        # attach flashcards / quiz to buttons if present
        self._flashcards = lesson_obj.get("flashcards", [])
        self._quiz = lesson_obj.get("quiz", [])

    def on_quiz(self, *a):
        if getattr(self, "_quiz", None):
            # set manager state and go to quiz screen (if you have one)
            self.manager.selected_quiz = self._quiz
            if "quiz" in self.manager.screen_names:
                self.manager.current = "quiz"
            else:
                print("Quiz payload:", self._quiz)
        else:
            self._show_msg("No quiz available for this lesson.")

    def on_flashcards(self, *a):
        if getattr(self, "_flashcards", None):
            self.manager.selected_flashcards = self._flashcards
            if "flashcards" in self.manager.screen_names:
                self.manager.current = "flashcards"
            else:
                print("Flashcards payload:", self._flashcards)
        else:
            self._show_msg("No flashcards for this lesson.")

    def on_pomodoro(self, *a):
        # open popup to set minutes
        content = BoxLayout(orientation="vertical", padding=8, spacing=8)
        ti = TextInput(text="25", input_filter="int", multiline=False, size_hint=(1, None), height=40)
        btn_start = Button(text="Set Pomodoro", size_hint=(1, None), height=44)

        content.add_widget(Label(text="Pomodoro minutes:"))
        content.add_widget(ti)
        content.add_widget(btn_start)

        popup = Popup(title="Pomodoro", content=content, size_hint=(0.8, None), height=220, auto_dismiss=True)

        def do_set(_):
            val = ti.text.strip()
            if not val:
                popup.dismiss()
                return
            try:
                minutes = int(val)
                self.pomodoro_seconds = minutes * 60
                # store to app for other screens to access
                app = self.manager.get_screen('courses').manager.get_running_app()
                app.pomodoro_seconds = self.pomodoro_seconds
                print(f"Pomodoro set: {minutes} minutes ({self.pomodoro_seconds}s)")
                popup.dismiss()
                self._show_msg(f"Pomodoro set: {minutes} min")
            except Exception:
                self._show_msg("Invalid minutes")

        btn_start.bind(on_release=do_set)
        popup.open()

    def _show_msg(self, text):
        popup = Popup(title="Info", content=Label(text=text), size_hint=(0.6, 0.3))
        popup.open()
