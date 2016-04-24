import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
import logging

kivy.require('1.9.0')
# Logger.setLevel(logging.DEBUG)

import contextmenu

kv = """
FloatLayout:
    id: layout
    AppMenu:
        id: app_menu
        top: root.height
        cancel_handler_widget: layout

        AppMenuTextItem:
            text: "Menu #2"
            ContextMenu:
                ContextMenuTextItem:
                    text: "Item #21"
                    on_release: app.fire_event(self.text)
                ContextMenuTextItem:
                    text: "Item #22"
                    on_release: app.fire_event(self.text)
                ContextMenuTextItem:
                    text: "Item #23"
                    on_release: app.fire_event(self.text)
                ContextMenuTextItem:
                    text: "Item #24"
                    ContextMenu:
                        ContextMenuTextItem:
                            text: "Item #24A"
                            on_release: app.fire_event(self.text)
                        ContextMenuTextItem:
                            text: "Item #24C"
                            on_release: app.fire_event(self.text)
                        ContextMenuTextItem:
                            text: "Item #24D"
                            on_release: app.fire_event(self.text)
                        ContextMenuTextItem:
                            text: "Item #24E"
                            on_release: app.fire_event(self.text)
        AppMenuTextItem:
            text: "Menu #3"
            ContextMenu:
                ContextMenuTextItem:
                    text: "SubMenu #31"
                    on_release: app.fire_event(self.text)
                ContextMenuTextItem:
                    text: "SubMenu #32"
                    on_release: app.fire_event(self.text)
                ContextMenuTextItem:
                    text: "SubMenu #33"
                    on_release: app.fire_event(self.text)
                ContextMenuDivider:
                ContextMenuTextItem:
                    text: "SubMenu #34"
                    on_release: app.fire_event(self.text)


    Label:
        pos: 10, 10
        text: "Left click anywhere outside the context menu to close it"
        size_hint: None, None
        size: self.texture_size
"""


class MyApp(App):
    def build(self):
        self.title = 'Demonstration of Menus'
        b = BoxLayout(orientation='vertical')
        t = TextInput(font_size=50,
                size_hint_y=None,
                height=100,
                text='default')

        f = FloatLayout()
        s = Scatter()
        l = Label(text='default',
                font_size=50)

        t.bind(text=l.setter('text'))
        self.menu = Builder.load_string(kv)

        f.add_widget(s)
        s.add_widget(l)

        b.add_widget(t)
        b.add_widget(f)
        b.add_widget(self.menu)
        return b

    def fire_event(self, text):
        print(text)
        self.menu.ids['app_menu'].close_all()


if __name__ == '__main__':
    MyApp().run()
