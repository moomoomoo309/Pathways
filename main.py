from __future__ import print_function
import calendar
from datetime import date, datetime
from functools import partial
from kivy.config import ConfigParser
from kivy.properties import BoundedNumericProperty
from kivy.uix.label import Label
from kivy.uix.settings import Settings, SettingItem
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.slider import Slider

from Calendar import Calendar30Days
from tabview import TabView, genericResize
from DatePicker import shouldUseWhiteText


def makeCalWidget(self):  # Initializes the Calendar grid
    return Calendar30Days(MonthLength=calendar.monthrange(datetime.now().year, datetime.now().month)[1], pos=(0, 0),
                          MonthStart=(date.today().replace(day=1).weekday() + 1) % 7,
                          size=(Window.width, Window.height - self.topBarSize - self.tabSize - self.tabMargin),
                          online=self.online, randomImages=self.randomImages, getImageSource=self._getImageSource)

class SettingSlider(SettingItem):
    value = BoundedNumericProperty(min=0, defaultvalue=50)
    def __init__(self, **kwargs):
        super(SettingSlider, self).__init__(**kwargs)
        self.value = self.panel.get_value(self.section, self.key)
        self.label = Label(text=str(self.value))
        self.add_widget(self.label)
        self.slider = Slider(min=0, max=100, value=self.value, step=1, size_hint_x=5)
        self.add_widget(self.slider)
        self.slider.bind(value=lambda self,newVal: setattr(self.parent.parent.parent.label, "text", str(int(newVal))))
        self.label.bind(text=lambda self,newVal: setattr(self.parent.parent.parent, "value", int(newVal)))



class main(App):
    def build(self):
        topBarSize = 75
        app = TabView(size=(Window.width, Window.height), randomImages=True, online=False, topBarSize=topBarSize)
        app.add_screen(makeCalWidget(app))
        appScreen = Screen(name="App")
        settingsScreen = Screen(name="Settings")
        settingsScreen.bind(size=partial(genericResize, objs=settingsScreen.children, fct=lambda: Window.size))
        screenManager = ScreenManager(transition=NoTransition(), size=Window.size)
        Window.bind(on_resize=partial(genericResize, objs=screenManager, fct=lambda: Window.size))
        screenManager.bind(size=partial(genericResize, objs=screenManager.children, fct=lambda: Window.size))
        screenManager.add_widget(appScreen)
        screenManager.add_widget(settingsScreen)
        appScreen.add_widget(app)
        appScreen.bind(size=partial(genericResize, objs=app, fct=lambda: Window.size))
        settingsButton = Button(pos=(Window.width - topBarSize, Window.height - topBarSize),
                                size=(topBarSize, topBarSize),
                                on_press=lambda self: setattr(self.parent.parent, "current",
                                                              self.parent.parent.screens[1].name),
                                background_normal="Settings.png", background_down="Settings.png",
                                background_color=(0, 0, 0, 1) if not shouldUseWhiteText(
                                    app.MonthButton.background_color) else (1, 1, 1, 1), size_hint=(None, None),
                                mipmap=True
                                )
        Window.bind(on_resize=lambda self, _, __: setattr(settingsButton, "pos",
                                                          (Window.width - topBarSize, Window.height - topBarSize)))
        appScreen.add_widget(settingsButton)

        settings = Settings()
        settings.register_type("slider", SettingSlider)
        settings.on_close = lambda: setattr(screenManager, "current", screenManager.screens[0].name)
        configParser = ConfigParser()
        configParser.read("Settings.cfg")
        configParser.adddefaultsection("Examples")
        configParser.setdefault("Examples", "numeric", 50)
        configParser.setdefault("Examples", "Checkbox", False)
        configParser.setdefault("Examples", "List", "Option 1")
        configParser.write()
        configParser.read("Settings.cfg")
        settings.add_json_panel("Example settings", configParser, "ExampleSettings.json")
        settingsScreen.add_widget(settings)
        return screenManager


if __name__ == "__main__":
    main().run()
