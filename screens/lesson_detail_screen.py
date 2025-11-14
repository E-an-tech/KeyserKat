# screens/lesson_detail_screen.py

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from data.courses import COURSES

class LessonDetailScreen(Screen):
    def load_lesson(self, course, unit, lesson):
        self.course_name = course
        self.unit_name = unit
        self.lesson_name = lesson
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()

        lesson = COURSES[self.course_name]["units"][self.unit_name]["lessons"][self.lesson_name]

        main = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Title
        title = Label(text=self.lesson_name, size_hint_y=None, height=40, font_size=24)
        main.add_widget(title)

        # Read time
        rt = Label(text=f"{lesson['read_time']} min read", size_hint_y=None, height=30)
        main.add_widget(rt)

        # Scrollable text
        scroll = ScrollView(size_hint=(1, 1))
        lbl = Label(text=lesson["content"], size_hint_y=None, text_size=(self.width, None))
        lbl.bind(texture_size=lambda *x: setattr(lbl, 'height', lbl.texture_size[1]))
        scroll.add_widget(lbl)
        main.add_widget(scroll)

        # Bottom buttons
        bottom = BoxLayout(size_hint_y=None, height=80, spacing=10)

        flash = Button(text="Flashcards")
        quiz = Button(text="Quiz (A,B,C,D)")
        pomo = Button(text="Pomodoro")

        bottom.add_widget(flash)
        bottom.add_widget(quiz)
        bottom.add_widget(pomo)

        main.add_widget(bottom)

        self.add_widget(main)
