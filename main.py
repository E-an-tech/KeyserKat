from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.label import Label

# Clothes/course overlays (transparent PNGs)
clothes_images = [
    "assets/clothes2.png",  # Statistics and probability
    "assets/clothes1.png",  # Physics
]

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clothes_index = 0

        self.clothes_images = [
            "assets/clothes2.png",
            "assets/clothes1.png",
        ]

        self.course_titles = [
            "Statistics and Probability",
            "Physics",
        ]
        self.start_x = 0
        self.courses = [
            "Statistics and Probability",
            "Physics",
            # Add more if needed
        ]
        self.current_index = 0


        layout = FloatLayout()

        self.title_label = Label(
            text=self.course_titles[self.clothes_index],  # Where the titles appear
            font_size="24sp",
            font_name="assets/meow_font.otf",
            size_hint=(1, 0.1),
            pos_hint={"center_y": 0.92},
            halign="center",
            valign="middle"
        )
        self.title_label.bind(size=self.title_label.setter('text_size'))
        
        # Optional mirror background
        mirror = Image(
            source="assets/mirror_bg.png",
            size_hint=(0.9, 0.9),
            pos_hint={"x": 0.05, "y": 0.17}
        )

        layout.add_widget(mirror)
        layout.add_widget(self.title_label)


        # Static cat in the center
        cat = Image(source="assets/cat_static.png", size_hint=(0.5, 0.5), pos_hint={"center_x": 0.5, "center_y": 0.6})
        layout.add_widget(cat)

        # Clothes overlay (this is what changes)
        self.clothes = Image(source=clothes_images[self.clothes_index],
                             size_hint=(0.5, 0.5), pos_hint={"center_x": 0.5, "center_y": 0.6})
        layout.add_widget(self.clothes)

        # Bottom button bar with fixed size and spacing
        buttons = BoxLayout(
            size_hint=(1, 0.15),
            pos_hint={"x": 0, "y": 0},
            orientation='horizontal',
            padding=[20, 0, 20, 0]
        )

        spacer1 = Widget(size_hint_x=1)
        spacer2 = Widget(size_hint_x=1)
        spacer3 = Widget(size_hint_x=1)
        spacer4 = Widget(size_hint_x=1)

        btn_settings = Button(
            background_normal="assets/settings.png",
            size_hint=(None, None),
            size=(200, 200)
        )
        btn_crown = Button(
            background_normal="assets/crown.png",
            size_hint=(None, None),
            size=(200, 200)
        )
        btn_support = Button(
            background_normal="assets/support.png",
            size_hint=(None, None),
            size=(200, 200)
        )

        btn_settings.bind(on_press=self.go_to_settings)
        btn_crown.bind(on_press=self.go_to_leaderboard)
        btn_support.bind(on_press=self.go_to_support)

        buttons.add_widget(spacer1)
        buttons.add_widget(btn_settings)
        buttons.add_widget(spacer2)
        buttons.add_widget(btn_crown)
        buttons.add_widget(spacer3)
        buttons.add_widget(btn_support)
        buttons.add_widget(spacer4)

        layout.add_widget(buttons)
        self.add_widget(layout)


    def on_touch_down(self, touch):
        self.start_x = touch.x
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        dx = touch.x - self.start_x
        if abs(dx) > 50:
            if dx < 0:
                self.next_clothes()
            else:
                self.prev_clothes()
        return super().on_touch_up(touch)

    def next_clothes(self):
        self.clothes_index = (self.clothes_index + 1) % len(self.clothes_images)
        self.clothes.source = self.clothes_images[self.clothes_index]
        self.title_label.text = self.course_titles[self.clothes_index]

    def prev_clothes(self):
        self.clothes_index = (self.clothes_index - 1) % len(self.clothes_images)
        self.clothes.source = self.clothes_images[self.clothes_index]
        self.title_label.text = self.course_titles[self.clothes_index]


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

        layout.add_widget(Label(text="Settings Page", font_size=24))

        btn_back = Button(text="Go Back", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.5})
        btn_back.bind(on_press=self.go_back)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def go_back(self, instance):
        self.manager.current = "main"


class LeaderboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)

        layout.add_widget(Label(text="Leaderboard Page", font_size=24))

        btn_back = Button(text="Go Back", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.5})
        btn_back.bind(on_press=self.go_back)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def go_back(self, instance):
        self.manager.current = "main"


class SupportScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)

        layout.add_widget(Label(text="Support Us Page", font_size=24))

        btn_back = Button(text="Go Back", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.5})
        btn_back.bind(on_press=self.go_back)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def go_back(self, instance):
        self.manager.current = "main"

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(LeaderboardScreen(name="leaderboard"))
        sm.add_widget(SupportScreen(name="support"))
        return sm

MyApp().run()
