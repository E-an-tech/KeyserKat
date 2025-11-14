# widgets/course_selector.py

from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout

class CourseSelector(BoxLayout):
    def __init__(self, course_name, icon_path, on_select, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.on_select = on_select
        self.course_name = course_name

        self.image = Image(source=icon_path, size_hint=(1, 0.85))
        self.add_widget(self.image)

        self.button = Button(
            text=course_name,
            size_hint=(1, 0.15)
        )
        self.button.bind(on_release=lambda x: self.on_select(self.course_name))
        self.add_widget(self.button)
