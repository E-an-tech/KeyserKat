import kivy
kivy.require('2.1.1')

from kivy.app import App
from kivy.uix.label import Label
from kivy.lang import Builder

# 👇 This line tells Kivy to load the .kv file from inside the kv/ folder
Builder.load_file('kv/home.kv')

class MyApp(App):
    def build(self):
        return Label(text='Rawr~')  # you can remove this if you're building UI in .kv

if __name__ == '__main__':
    MyApp().run()
