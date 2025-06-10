from kivy.core.text import LabelBase


# Register the font once
LabelBase.register(
    name="MeowFonto",  # Internal font name used in widgets
    fn_regular="assets/meow_fonto.ttf"
)

from kivy.config import Config
# Optional: set it as the global default
Config.set('kivy', 'default_font', [
    'MeowFonto',
    'assets/meow_fonto.ttf',
    '', '', ''  # bold, italic, bold-italic (leave blank if unused)
])

from kivy.uix.button import Button
from kivy.uix.label import Label

class MeowLabel(Label):
    def __init__(self, **kwargs):
        kwargs.setdefault('font_name', 'MeowFonto')
        super().__init__(**kwargs)

class MeowButton(Button):
    def __init__(self, **kwargs):
        kwargs.setdefault('font_name', 'MeowFonto')
        super().__init__(**kwargs)


from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.stencilview import StencilView
from kivy.animation import Animation

class MirrorArea(StencilView):
    pass


class ClothesMirrorApp(App):
    def build(self):
        # Index of the clothes image to show
        self.clothes_index = 0
        self.layout = layout
        layout = FloatLayout()

            # Mirror background image
        mirror = Image(
            source="assets/mirror_bg.png",
            size_hint=(0.9, 0.9),
            pos_hint={"x": 0.05, "y": 0.17}
        )
        layout.add_widget(mirror)

        # Clipped area inside the mirror
        clipped_area = MirrorArea(
            size_hint=(0.9, 0.9),
            pos_hint={"x": 0.05, "y": 0.17}
        )
        layout.add_widget(clipped_area)


        # When you create the clothes Image widget, use it like this:
        self.clothes = Image(
            source=clothes_images[self.clothes_index],  # get image from your list
            size_hint=(None, None),
            size=(200, 300),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        # Then add this Image inside the clipped_area (StencilView)
        clipped_area.add_widget(self.clothes)

        return layout


    


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
            text=self.course_titles[self.clothes_index],
            font_size="24sp",
            font_name="MeowFonto",  # ✅ Use the name from LabelBase.register
            size_hint=(1, 0.1),
            pos_hint={"center_y": 0.92},
            halign="center",
            valign="middle"
        )

    #But be warned: sometimes global default font doesn’t affect -
    #"Button" or "TextInput" in all Kivy versions
    #Its safer to manually set it for those if it doesn’t work.

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

    def switch_clothes(self, new_index, direction="left"):
            if new_index == self.clothes_index:
                return

            screen_width = self.width

            # Decide direction
            out_target_x = -self.clothes.width if direction == "left" else screen_width
            in_start_x = screen_width if direction == "left" else -self.clothes.width
            center_x = (screen_width - self.clothes.width) / 2

            # Animate old clothes out
            anim_out = Animation(x=out_target_x, duration=0.25)

            def on_out_complete(animation, widget):
                # Update image + label
                self.clothes.source = self.clothes_images[new_index]
                self.title_label.text = self.course_titles[new_index]

                # Move clothes offscreen to opposite side
                self.clothes.x = in_start_x

                # Animate new clothes in
                anim_in = Animation(x=center_x, duration=0.25)
                anim_in.start(self.clothes)

                # Update index
                self.clothes_index = new_index

            anim_out.bind(on_complete=on_out_complete)
            anim_out.start(self.clothes)
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
        new_index = (self.clothes_index + 1) % len(self.clothes_images)
        self.switch_clothes(new_index, direction="left")

    def prev_clothes(self):
        new_index = (self.clothes_index - 1) % len(self.clothes_images)
        self.switch_clothes(new_index, direction="right")



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

        layout.add_widget(MeowLabel(text="Settings Page", font_size=24))

        btn_back = MeowButton(text="Go Back", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.5})
        btn_back.bind(on_press=self.go_back)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def go_back(self, instance):
        self.manager.current = "main"


class LeaderboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)

        layout.add_widget(MeowLabel(text="Leaderboard Page", font_size=24))

        btn_back = MeowButton(text="Go Back", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.5})
        btn_back.bind(on_press=self.go_back)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def go_back(self, instance):
        self.manager.current = "main"


class SupportScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)

        layout.add_widget(MeowLabel(text="Support Us Page", font_size=24))

        btn_back = MeowButton(text="Go Back", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.5})
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
