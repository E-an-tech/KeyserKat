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
from kivy.graphics import Color, Rectangle





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

        #
        # Create the clothes image, start it at the center
        self.clothes = Image(
            source=self.clothes_images[self.clothes_index],
            size_hint=(None, None),
            size=(200, 300),
            pos_hint={"center_x": 0.5, "center_y": 0.6}
        )

        self.clipped_area.add_widget(self.clothes)
        layout.add_widget(self.clipped_area)

        return layout
    
    def on_size(self, *args):
        # This ensures the clothes image is centered inside the clipped area
        if self.clothes and self.clipped_area:
            self.clothes.pos = (
                (self.clipped_area.width - self.clothes.width) / 2,
                0
            )



# Clothes/course overlays (transparent PNGs)
clothes_images = [
    "assets/clothes2.png",  # Statistics and probability
    "assets/clothes1.png",  # Physics
]

class MirrorArea(StencilView):
    pass

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

        layout = FloatLayout()

        self.title_label = Label(
            text=self.course_titles[self.clothes_index],
            font_size="24sp",
            font_name="MeowFonto",
            size_hint=(1, 0.1),
            pos_hint={"center_y": 0.92},
            halign="center",
            valign="middle"
        )
        
        self.title_label.bind(size=self.title_label.setter('text_size'))
        layout.add_widget(self.title_label)

        # Mirror background
        mirror = Image(source="assets/mirror_bg.png", size_hint=(0.9, 0.9), pos_hint={"x": 0.05, "y": 0.17})
        layout.add_widget(mirror)

        # Cat static image
        cat = Image(source="assets/cat_static.png", size_hint=(0.5, 0.5), pos_hint={"center_x": 0.5, "center_y": 0.6})
        layout.add_widget(cat)

        # ✅ Create a stencil mask for the clothes
        self.clipped_area = MirrorArea(size_hint=(0.5, 0.5), pos_hint={"center_x": 0.5, "center_y": 0.6})

        with self.clipped_area.canvas.before:
            Color(1, 0, 0, 0.3)
            self.rect=Rectangle(size=self.clipped_area.size, pos=self.clipped_area.pos)


        self.clothes = Image(source=self.clothes_images[self.clothes_index],
                             size_hint=(None, None), size=(200, 300), pos=(0, 0))
        self.clipped_area.add_widget(self.clothes)
        layout.add_widget(self.clipped_area)

        # Bottom buttons
        buttons = BoxLayout(size_hint=(1, 0.15), pos_hint={"x": 0, "y": 0}, orientation='horizontal',
                            padding=[20, 0, 20, 0])

        btn_settings = Button(background_normal="assets/settings.png", size_hint=(None, None), size=(200, 200))
        btn_crown = Button(background_normal="assets/crown.png", size_hint=(None, None), size=(200, 200))
        btn_support = Button(background_normal="assets/support.png", size_hint=(None, None), size=(200, 200))

        for btn, callback in [
            (btn_settings, self.go_to_settings),
            (btn_crown, self.go_to_leaderboard),
            (btn_support, self.go_to_support)
        ]:
            btn.bind(on_press=callback)

        buttons.add_widget(Widget(size_hint_x=1))
        buttons.add_widget(btn_settings)
        buttons.add_widget(Widget(size_hint_x=1))
        buttons.add_widget(btn_crown)
        buttons.add_widget(Widget(size_hint_x=1))
        buttons.add_widget(btn_support)
        buttons.add_widget(Widget(size_hint_x=1))

        layout.add_widget(buttons)
        self.add_widget(layout)

    def switch_clothes(self, new_index, direction="left"):
        if new_index == self.clothes_index:
            return

        screen_width = self.width
        out_target_x = -self.clothes.width if direction == "left" else screen_width
        in_start_x = screen_width if direction == "left" else -self.clothes.width
        center_x = (self.clipped_area.width - self.clothes.width) / 2

        anim_out = Animation(x=out_target_x, duration=0.25)

        def on_out_complete(animation, widget):
            self.clothes.source = self.clothes_images[new_index]
            self.title_label.text = self.course_titles[new_index]
            self.clothes.x = in_start_x
            Animation(x=center_x, duration=0.25).start(self.clothes)
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

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


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
        self.bind(size=self.on_size)
        self.add_widget(layout)

    def go_back(self, instance):
        self.manager.current = "main"

    def on_size(self, *args):
        pass  # or put code to handle size changes here



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
