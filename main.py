from kivy.core.text import LabelBase
from kivy.config import Config
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.uix.stencilview import StencilView
from kivy.animation import Animation
from kivy.graphics import StencilPush, StencilUse, StencilUnUse, StencilPop, Rectangle
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window



# Force portrait mode
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'resizable', True)

# Register custom font
LabelBase.register(
    name="SamulFont",
    fn_regular="C:/Windows/Fonts/H2SA1M.TTF"
)


class PreTestScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)

        layout.add_widget(Label(text="Pre-Test: Answer this question", font_name="SamulFont", font_size=30))
        self.question_label = Label(text="What is 5 + 3?", font_name="SamulFont", font_size=40)
        layout.add_widget(self.question_label)

        self.answer_input = TextInput(multiline=False, size_hint=(None, None), size=(200, 40),
                                      pos_hint={"center_x": 0.5})
        layout.add_widget(self.answer_input)

        btn_submit = Button(text="Submit", size_hint=(None, None), size=(200, 60), font_name="SamulFont", font_size=35,
                            pos_hint={"center_x": 0.5})
        btn_submit.bind(on_press=self.submit_answer)
        layout.add_widget(btn_submit)

        self.add_widget(layout)

    def submit_answer(self, instance):
        answer = self.answer_input.text.strip()
        if answer == "8":
            self.manager.current = "main"
        else:
            self.question_label.text = "Wrong! Try again: What is 5 + 3?"


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
            Color(1, 0, 0, 0.3)  # red with transparency
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
        if abs(dx) > 50:
            if dx < 0:
                self.next_clothes()
            else:
                self.prev_clothes()
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


class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(PreTestScreen(name="pretest"))
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(LeaderboardScreen(name="leaderboard"))
        sm.add_widget(SupportScreen(name="support"))
        sm.current = "pretest"
        return sm


if __name__ == "__main__":
    MyApp().run()
