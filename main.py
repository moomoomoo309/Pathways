import calendar
import datetime
from datetime import date, datetime
from kivy.uix.settings import Settings
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from functools import partial
from kivy.uix.button import Button
from Calendar import Calendar30Days
from tabview import TabView, genericResize


def makeCalWidget(self):  # Initializes the Calendar grid
    return Calendar30Days(MonthLength=calendar.monthrange(datetime.now().year, datetime.now().month)[1], pos=(0, 0),
                          MonthStart=(date.today().replace(day=1).weekday() + 1) % 7,
                          size=(Window.width, Window.height - self.topBarSize - self.tabSize - self.tabMargin),
                          online=self.online, randomImages=self.randomImages, getImageSource=self._getImageSource)


class main(App):
    def build(self):
        app = TabView(size=(Window.width, Window.height), randomImages=True, online=False)
        Window.bind(on_resize=partial(genericResize, objs=app, fct=lambda: Window.size))
        app.add_screen(makeCalWidget(app))
        appScreen = Screen(name="App")
        settingsScreen = Screen(name="Settings")
        screenManager = ScreenManager()
        screenManager.add_widget(appScreen)
        screenManager.add_widget(settingsScreen)
        appScreen.add_widget(app)
        appScreen.add_widget(Button(pos=(100, 100), size=(1000, 1000),
                                    on_press=lambda self: setattr(self.parent.parent,"current",self.parent.parent.screens[1].name)))

        settings = Settings()
        settings.on_close = lambda: setattr(screenManager,"current",screenManager.screens[0].name)
        settings.add_kivy_panel()
        settingsScreen.add_widget(settings)
        return screenManager


if __name__ == "__main__":
    main().run()
