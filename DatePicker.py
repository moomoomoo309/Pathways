from __future__ import print_function

import calendar
from datetime import date, datetime
from functools import partial

from kivy.app import App
from kivy.config import ConfigParser
from kivy.core.window import Window
from kivy.properties import BoundedNumericProperty
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition
from kivy.uix.settings import Settings, SettingItem
from kivy.uix.slider import Slider

from Calendar import Calendar30Days
from DatePicker import shouldUseWhiteText
from tabview import TabView, genericResize


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
        # Slider range is 0-100 with an interval of 1
        self.add_widget(self.slider)
        self.slider.bind(value=lambda self,newVal: setattr(self.parent.parent.parent.label, "text", str(int(newVal))))
        # Update the label with the slider value
        self.label.bind(text=lambda self,newVal: setattr(self.parent.parent.parent, "value", int(newVal)))
        # Update the setting from the label value



class main(App):
    layout = RelativeLayout()
    # This is here so things can be placed on the root widget if needed.
    def build(self):
        topBarSize = 75
        app = TabView(size=(Window.width, Window.height), randomImages=True, online=False, topBarSize=topBarSize)
        app.add_screen(makeCalWidget(app))
        # Put the calendar on the Month view
        appScreen = Screen(name="App")
        settingsScreen = Screen(name="Settings")
        # Make screens for the app itself and the settings menu
        settingsScreen.bind(size=partial(genericResize, objs=settingsScreen.children, fct=lambda: Window.size))
        # Resize the settings menu on window resize
        screenManager = ScreenManager(transition=NoTransition(), size=Window.size)
        # Don't have a transition when switching to the settings menu
        Window.bind(on_resize=partial(genericResize, objs=screenManager, fct=lambda: Window.size))
        # Resize all widgets on window resize
        screenManager.bind(size=partial(genericResize, objs=screenManager.children, fct=lambda: Window.size))
        # Propogate resize to all children
        screenManager.add_widget(appScreen)
        screenManager.add_widget(settingsScreen)
        # Add screens into screen manager
        appScreen.add_widget(app)
        # Add the app into the screen so it actually shows up
        appScreen.bind(size=partial(genericResize, objs=app, fct=lambda: Window.size))
        # Propogate resize to all children
        settingsButton = Button(pos=(Window.width - topBarSize, Window.height - topBarSize),
                                size=(topBarSize, topBarSize),
                                on_press=lambda self: setattr(self.parent.parent, "current",
                                                              self.parent.parent.screens[1].name),
                                background_normal="Settings.png", background_down="Settings.png",
                                background_color=(0, 0, 0, 1) if not shouldUseWhiteText(
                                    app.MonthButton.background_color) else (1, 1, 1, 1), size_hint=(None, None),
                                mipmap=True)
        # Button to go to the settings screen, changes color depending on what's behind it
        Window.bind(on_resize=lambda self, _, __: setattr(settingsButton, "pos",
                                                          (Window.width - topBarSize, Window.height - topBarSize)))
        # Move the settings button so it always stays in the top right corner
        appScreen.add_widget(settingsButton)
        # Add the button to switch to the settings screen within the app
        settings = Settings()
        settings.register_type("slider", SettingSlider)
        # Add the slider to the settings menu; kivy does not implement one by default
        settings.on_close = lambda: setattr(screenManager, "current", screenManager.screens[0].name)
        # When closing the settings menu, switch back to the app.
        configParser = ConfigParser()
        configParser.read("Settings.cfg")
        configParser.adddefaultsection("Examples")
        configParser.setdefault("Examples", "num", 0)
        configParser.setdefault("Examples", "numeric", 50)
        configParser.setdefault("Examples", "Checkbox", False)
        configParser.setdefault("Examples", "List", "Option 1")
        configParser.write()
        configParser.read("Settings.cfg")
        # Write defaults to the config if it is missing any fields
        settings.add_json_panel("Example settings", configParser, "ExampleSettings.json")
        settingsScreen.add_widget(settings)
        return screenManager

if __name__ == "__main__":
    main().run()
