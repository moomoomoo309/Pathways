import calendar
from datetime import date, datetime
from functools import partial
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Rectangle
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition
from kivy.uix.settings import Settings, SettingItem
from kivy.uix.slider import Slider
import pytz # Don't forget to include this module!

from kivy.properties import BoundedNumericProperty, ListProperty, StringProperty

import Globals
from Calendar import Calendar30Days, CalendarLessThan30Days
from ColorUtils import shouldUseWhiteText, PrimaryColors, Gradient
from ScheduleView import ScheduleView
from tabview import TabView, genericResize


def makeCalWidget(self):  # Initializes the Calendar grid
    return Calendar30Days(MonthLength=calendar.monthrange(datetime.now().year, datetime.now().month)[1], pos=(0, 0),
        MonthStart=(date.today().replace(day=1).weekday() + 1) % 7,
        size=(Window.width, Window.height - self.topBarSize - self.tabSize - self.tabMargin),
        randomImages=Globals.config.getboolean("Real Settings", "randomImages"),
        online=Globals.config.getboolean("Real Settings", "online"))


class SettingSlider(SettingItem):
    value = BoundedNumericProperty(min=0, defaultvalue=50)

    def __init__(self, **kwargs):
        super(SettingSlider, self).__init__(**kwargs)
        # Current value on the slider
        self.value = self.panel.get_value(self.section, self.key)

        # Label with the current value on it
        self.label = Label(text=str(self.value))

        self.add_widget(self.label)
        # Slider range is 0-100 with an interval of 1
        self.slider = Slider(min=0, max=100, value=self.value, step=1, size_hint_x=5)

        # Add the slider in, so it exists
        self.add_widget(self.slider)

        # Update the label with the slider value
        self.slider.bind(value=lambda self, newVal: setattr(self.parent.parent.parent.label, "text", str(int(newVal))))

        # Update the setting from the label value
        self.label.bind(text=lambda self, newVal: setattr(self.parent.parent.parent, "value", int(newVal)))


class SettingColorList(SettingItem):
    value = StringProperty()  # The color in text form
    colors = PrimaryColors  # The colors it has to pick from in the list
    realValue = ListProperty()  # The actual color, as a list

    def __init__(self, **kwargs):
        super(SettingColorList, self).__init__(**kwargs)
        # Get the previous value, convert it back to a list
        self.value = self.panel.get_value(self.section, self.key)
        for i in self.value.translate({ord(k): None for k in u' ()[]{}'}).split(","):
            self.realValue.append(float(i))

        # Bind color changes from children to parents
        self.bind(realValue=lambda inst, val: setattr(self, "value", str(val)))
        self.bind(realValue=updatePrimaryColor)
        # The button which holds the current color
        self.btns = GridLayout(cols=4, spacing=1)
        self.popup = Popup(title="Primary Color", content=self.btns, size_hint=(.75, .75))
        self.btn = Button(background_down="CalendarInactive.png", background_normal="CalendarInactive.png",
            background_color=self.realValue, on_press=self.popup.open)
        # Recolor that button with the current color
        self.btn.bind(background_color=lambda inst, val: setattr(self, "realValue", val))
        self.btn.bind(background_color=self.popup.dismiss)
        self.add_widget(self.btn)

        # Add the buttons for each color
        for i in self.colors:
            self.btns.add_widget(
                Button(background_down="CalendarInactive.png", background_normal="CalendarInactive.png",
                    background_color=i,
                    on_press=lambda inst: setattr(self.btn, "background_color", inst.background_color)))

        # Update the primary color
        Globals.PrimaryColor = self.realValue


class main(App):
    # This is here so things can be placed on the root widget if needed.
    layout = RelativeLayout()
    settings = None

    def build_config(self, config):
        Globals.redraw = []
        Globals.config = config

        # Instantiate the settings menu
        self.settings = Settings()
        # Add the slider and color picker to the settings menu; kivy does not implement them by default
        self.settings.register_type("slider", SettingSlider)
        self.settings.register_type("colorList", SettingColorList)

        # Write defaults to the config if it is missing any fields
        def randomImagesCallback(section, key, val):
            Globals.randomImages=int(val)==1
            for i in Globals.randomImagesCallback:
                i(int(val)==1)

        def onlineCallback(section, key, val):
            Globals.online=int(val)==1
            for i in Globals.onlineCallback:
                i(int(val)==1)

        config.read(self.get_application_config())
        config.adddefaultsection("Real Settings")
        config.setdefault("Real Settings", "randomImages", True)
        config.add_callback(randomImagesCallback, "Real Settings", "randomImages")
        config.setdefault("Real Settings", "online", True)
        config.add_callback(onlineCallback, "Real Settings", "online")
        config.setdefault("Real Settings", "Primary Color", PrimaryColors[0])
        config.write()

        # Set up the structure of the actual menu
        self.settings.add_json_panel("Settings", config, "ExampleSettings.json")

    def build(self):
        Globals.randomImages=Globals.config.getboolean("Real Settings","randomImages")
        Globals.online=Globals.config.getboolean("Real Settings", "online")
        topBarSize = 75
        # Put the calendar on the Month view
        app = TabView(size=(Window.width, Window.height), randomImages=True, online=False, topBarSize=topBarSize)
        Globals.tabview = app
        app.add_screen(makeCalWidget(app))
        app.add_screen(CalendarLessThan30Days(days=7), 1)
        app.add_screen(CalendarLessThan30Days(days=3), 2)
        app.add_screen(CalendarLessThan30Days(days=1), 3)
        app.add_screen(ScheduleView(), 4)

        # When closing the settings menu, switch back to the app.
        self.settings.on_close = lambda: setattr(screenManager, "current", screenManager.screens[0].name)

        # Make screens for the app itself and the settings menu
        self.appScreen = Screen(name="App")
        self.appScreen.gradient = True
        rectHeight = 20
        self.appScreen.canvas.after.add(
            Rectangle(pos=(0, 0), size=(app.width, rectHeight), texture=Gradient.vertical((0, 0, 0, .5), (0, 0, 0, 0))))

        self.appScreen.bind(size=lambda inst, size: setattr(
            self.appScreen.canvas.after.children[len(self.appScreen.canvas.after.children) - 1], "size",
            (self.appScreen.width, rectHeight)))
        self.appScreen.bind(size=lambda inst, size:
        setattr(self.appScreen.canvas.after.children[len(self.appScreen.canvas.after.children) - 1], "pos",
            (-100000, -100000) if not inst.gradient else (0,
            self.appScreen.height - rectHeight - app.tabSize * app.floatBarRatio - app.topBarSize - app.tabMargin -
            app.tabSize * (1 - app.floatBarRatio))))
        settingsScreen = Screen(name="Settings")

        # Resize the settings menu on window resize
        settingsScreen.bind(size=partial(genericResize, objs=settingsScreen.children, fct=lambda: Window.size))

        # Don't have a transition when switching to the settings menu
        screenManager = ScreenManager(transition=NoTransition(), size=Window.size)

        # Resize all widgets on window resize
        Window.bind(on_resize=partial(genericResize, objs=screenManager, fct=lambda: Window.size))

        # Propogate resize to all children
        screenManager.bind(size=partial(genericResize, objs=screenManager.children, fct=lambda: Window.size))

        # Add screens into screen manager
        screenManager.add_widget(self.appScreen)
        screenManager.add_widget(settingsScreen)

        # Add the app into the screen so it actually shows up
        self.appScreen.add_widget(app)

        # Propogate resize to all children
        self.appScreen.bind(size=partial(genericResize, objs=app, fct=lambda: Window.size))

        # Button to go to the settings screen, changes color depending on what's behind it
        settingsButton = Button(pos=(Window.width - topBarSize, Window.height - topBarSize),
            size=(topBarSize, topBarSize),
            on_press=lambda self: setattr(self.parent.parent, "current",
                self.parent.parent.screens[1].name),
            background_normal="Settings.png", background_down="Settings.png",
            background_color=(0, 0, 0, 1) if not shouldUseWhiteText(
                app.MonthButton.background_color) else (1, 1, 1, 1), size_hint=(None, None),
            mipmap=True)

        # Move the settings button so it always stays in the top right corner
        Window.bind(on_resize=lambda self, _, __: setattr(settingsButton, "pos",
            (Window.width - topBarSize, Window.height - topBarSize)))

        # Add the button to switch to the settings screen within the app
        self.appScreen.add_widget(settingsButton)

        # Add the settings menu to the screen so it shows up
        settingsScreen.add_widget(self.settings)

        return screenManager


def updatePrimaryColor(_, color):
    Globals.PrimaryColor = color[0:3] + [1]
    for i in Globals.redraw:
        i[1](i[0])


if __name__ == "__main__":
    main().run()
