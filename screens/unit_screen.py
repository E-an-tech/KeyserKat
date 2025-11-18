# screens/unit_screen.py

# screens/unit_screen.py
import os, json
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

# Utility to find project base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_JSON = os.path.join(BASE_DIR, "data", "levels.json")  # change if using courses.json

class UnitScreen(Screen):
    """
    Loads units for the selected course.
    Expects app.selected_course to be the course key (e.g. 'statistics_probability').
    When a unit is tapped, it sets manager.selected_unit to the unit id and goes to 'lessons'.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content = BoxLayout(orientation="vertical", padding=12, spacing=12)
        self.title_label = Label(text="Units", size_hint=(1, None), height=40)
        self.content.add_widget(self.title_label)

        # Scrollable area with a vertical grid for buttons
        self.scroll = ScrollView(size_hint=(1, 1))
        self.grid = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=[0,10,0,10])
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        self.content.add_widget(self.scroll)

        self.add_widget(self.content)

        # load data cache
        self._courses_data = None

    def _load_courses_data(self):
        if self._courses_data is not None:
            return self._courses_data
        if os.path.exists(DATA_JSON):
            with open(DATA_JSON, "r", encoding="utf-8") as f:
                self._courses_data = json.load(f)
                return self._courses_data
        else:
            self._courses_data = {}
            return self._courses_data

    def on_pre_enter(self):
        app = self.manager.get_screen('courses').manager.get_running_app() if hasattr(self.manager, 'get_screen') else None
        # But easier: read selected_course from app
        app = self.manager.get_screen('courses').manager.get_running_app()
        selected = getattr(app, "selected_course", None) or getattr(self.manager, "selected_course", None)
        if not selected:
            selected = "statistics_probability"  # fallback
        self.load_units(selected)

    def load_units(self, course_key):
        """
        Called externally by CourseSelectScreen.go_to_course(course_id) or similar.
        course_key must match the key in levels.json (e.g. 'statistics_probability').
        """
        data = self._load_courses_data()
        self.grid.clear_widgets()

        course = data.get(course_key)
        if not course:
            self.title_label.text = f"Course not found: {course_key}"
            return

        self.title_label.text = f"{course.get('title','Course')} — Units"

        for unit in course.get("units", []):
            uid = unit.get("id")
            title = unit.get("title", f"Unit {uid}")
            btn = Button(text=f"Unit {uid}: {title}", size_hint_y=None, height=64)
            # capture unit object in lambda default
            btn.bind(on_release=lambda inst, u=unit: self.open_unit(u))
            self.grid.add_widget(btn)

    def open_unit(self, unit_obj):
        """
        Set manager selectors and navigate to lesson list.
        """
        # store selected unit in manager/app for other screens
        self.manager.selected_unit = unit_obj.get("id")
        self.manager.selected_unit_obj = unit_obj  # keep full object
        # also set in app
        app = self.manager.get_screen('courses').manager.get_running_app()
        app.selected_unit = unit_obj.get("id")

        # Pre-populate lesson list screen with this unit's lessons
        if "lessons" in self.manager.screen_names:
            lessons_screen = self.manager.get_screen("lessons")
            if hasattr(lessons_screen, "load_lessons"):
                lessons_screen.load_lessons(unit_obj, app.selected_course)
        # Change screen
        self.manager.transition.direction = "left"
        self.manager.current = "lessons"
