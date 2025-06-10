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
from kivy.graphics import Color, Rectangle

# Register your custom font
LabelBase.register(
    name="MeowFonto",
    fn_regular="assets/meow_fonto.ttf"
)

Config.set('kivy', 'default_font', [
    'MeowFonto',
    'assets/meow_fonto.ttf',
    '', '', ''
])

class MeowLabel(Label):
    def __init__(self, **kwargs):
        kwargs.setdefault('font_name', 'MeowFonto')
        super().__init__(**kwargs)

class MeowButton(Button):
    def __init__(self, **kwargs):
        kwargs.setdefault('font_name', 'MeowFonto')
        super().__init__(**kwargs)

# A stencil widget to clip clothes inside mirror shape
class MirrorArea(StencilView):
    pass

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.clothes_index = 0
        self.clothes_images = [
            "assets/clothes2.png",  # Stats and Probability
            "assets/clothes1.png",  # Physics
        ]
        self.course_titles = [
            "Statistics and Probability",
            "Physics",
        ]

        self.start_x = 0  # For swipe detection

        layout = FloatLayout()

        # Mirror background image (big)
        self.mirror = Image(
            source="assets/mirror_bg.png",
            size_hint=(0.9, 0.9),
            pos_hint={"x": 0.05, "y": 0.17}
        )
        layout.add_widget(self.mirror)

        # Title label at top center
        self.title_label = MeowLabel(
            text=self.course_titles[self.clothes_index],
            font_size="23sp",
            size_hint=(1, 0.1),
            pos_hint={"center_x": 0.5, "top": 0.97},
            halign="center",
            valign="middle"
        )
        self.title_label.bind(size=self.title_label.setter('text_size'))
        layout.add_widget(self.title_label)

        # Cat static image, centered inside mirror area roughly
        self.cat = Image(
            source="assets/cat_static.png",
            size_hint=(0.5, 0.5),
            pos_hint={"center_x": 0.5, "center_y": 0.6}
        )
        layout.add_widget(self.cat)

        # Clipped area for clothes overlays: same size and pos as mirror to align perfectly
        self.clipped_area = MirrorArea(
            size_hint=(0.372, 0.5),
            pos_hint={"center_x": 0.5, "center_y": 0.592}
        )

        # Draw a transparent red rectangle mask for debug (set alpha=0 later)
        with self.clipped_area.canvas.before:
            Color(0, 0, 0, 0)  # Remove or change alpha to 0 when ready "Color(1, 0, 0, 0.3)"
            self.rect = Rectangle(size=self.clipped_area.size, pos=self.clipped_area.pos)

        # Update rectangle size and position when clipped_area changes
        self.clipped_area.bind(size=self.update_rect, pos=self.update_rect)

        # Clothes image starts at bottom-left of clipped_area
        self.clothes = Image(
            source=self.clothes_images[self.clothes_index],
            size_hint=(None, None),
            size=(380, 380),
            pos=(310, 260)
        )
        self.clipped_area.add_widget(self.clothes)
        layout.add_widget(self.clipped_area)

        # Bottom buttons layout
        buttons = BoxLayout(size_hint=(1, 0.15), pos_hint={"x": 0, "y": 0}, orientation='horizontal', padding=[20, 0, 20, 0])

        btn_settings = Button(background_normal="assets/settings.png", size_hint=(None, None), size=(250, 250))
        btn_crown = Button(background_normal="assets/crown.png", size_hint=(None, None), size=(250, 250))
        btn_support = Button(background_normal="assets/support.png", size_hint=(None, None), size=(250, 250))

        btn_settings.bind(on_press=self.go_to_settings)
        btn_crown.bind(on_press=self.go_to_leaderboard)
        btn_support.bind(on_press=self.go_to_support)

        buttons.add_widget(Widget(size_hint_x=1))
        buttons.add_widget(btn_settings)
        buttons.add_widget(Widget(size_hint_x=1))
        buttons.add_widget(btn_crown)
        buttons.add_widget(Widget(size_hint_x=1))
        buttons.add_widget(btn_support)
        buttons.add_widget(Widget(size_hint_x=1))

        layout.add_widget(buttons)

        self.add_widget(layout)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    # Swipe left/right detection to switch clothes
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

    def switch_clothes(self, new_index, direction="left"):
        if new_index == self.clothes_index:
            return

        screen_width = self.width
        out_target_x = -self.clothes.width if direction == "left" else screen_width
        in_start_x = screen_width if direction == "left" else -self.clothes.width
        fixed_y = 260 # <- keep Y fixed at your manually placed value

        Animation(x=310, duration=0.25, t='out_back').start(self.clothes)
        anim_out = Animation(x=out_target_x, duration=0.25)

        def on_out_complete(animation, widget):
            self.clothes.source = self.clothes_images[new_index]
            self.title_label.text = self.course_titles[new_index]
            self.clothes.pos = (in_start_x,fixed_y)
            Animation(x=310, duration=0.25).start(self.clothes)
            self.clothes_index = new_index

        anim_out.bind(on_complete=on_out_complete)
        anim_out.start(self.clothes)

    def next_clothes(self):
        new_index = (self.clothes_index + 1) % len(self.clothes_images)
        self.switch_clothes(new_index, direction="left")

    def prev_clothes(self):
        new_index = (self.clothes_index - 1) % len(self.clothes_images)
        self.switch_clothes(new_index, direction="right")

    # Screen navigation buttons
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

if __name__ == "__main__":
    MyApp().run()
