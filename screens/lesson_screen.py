# screens/lesson_screen.py

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from data.courses import COURSES

class LessonScreen(Screen):
    def load_lesson_list(self, course_name, unit_name):
        self.course_name = course_name
        self.unit_name = unit_name
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()

        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        lessons = COURSES[self.course_name]["units"][self.unit_name]["lessons"]

        for lesson_name in lessons.keys():
            btn = Button(text=lesson_name, size_hint_y=None, height=80)
            btn.bind(on_release=lambda x, l=lesson_name: self.open_lesson(l))
            layout.add_widget(btn)

        self.add_widget(layout)

    def open_lesson(self, lesson_name):
        screen = self.manager.get_screen("lesson_detail")
        screen.load_lesson(
            self.course_name,
            self.unit_name,
            lesson_name
        )
        self.manager.current = "lesson_detail"
