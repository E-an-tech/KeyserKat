# screens/unit_screen.py

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from data.courses import COURSES

class UnitScreen(Screen):
    def load_course(self, course_name):
        self.course_name = course_name
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()

        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        units = COURSES[self.course_name]["units"]

        for unit_name in units.keys():
            btn = Button(text=unit_name, size_hint_y=None, height=80)
            btn.bind(on_release=lambda x, u=unit_name: self.open_unit(u))
            layout.add_widget(btn)

        self.add_widget(layout)

    def open_unit(self, unit_name):
        self.manager.get_screen("lessons").load_lesson_list(self.course_name, unit_name)
        self.manager.current = "lessons"
