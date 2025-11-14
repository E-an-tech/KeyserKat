# screens/course_screen.py

from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from widgets.course_selector import CourseSelector
from data.courses import COURSES

class CourseScreen(Screen):
    def on_enter(self):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()

        scroll = ScrollView()
        layout = GridLayout(cols=2, padding=10, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter("height"))

        for course_name, course_data in COURSES.items():
            widget = CourseSelector(
                course_name,
                course_data["icon"],
                on_select=self.open_course
            )
            layout.add_widget(widget)

        scroll.add_widget(layout)
        self.add_widget(scroll)

    def open_course(self, course_name):
        self.manager.get_screen("units").load_course(course_name)
        self.manager.current = "units"
