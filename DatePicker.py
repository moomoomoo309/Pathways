from calendar import monthrange
from datetime import date
from datetime import timedelta
from math import ceil

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Rectangle, Color
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout

import Globals
from ColorUtils import shouldUseWhiteText


def getMonthLength(month, year):  # Returns how many days are in the given month in the given year
    return monthrange(year, month)[1]


def getStartDay(month, year):  # Returns which day of the week the given month in the given year starts on
    return monthrange(year, month)[0]


# noinspection PyUnusedLocal
class DatePicker(BoxLayout):
    visibleDate = ObjectProperty(baseclass=date)  # The month currently visible on the datepicker

    def __init__(self, *args, **kwargs):
        super(DatePicker, self).__init__(**kwargs)
        self.bind(size=lambda inst, size: setattr(self, "y", Window.height - size[1])) # Align to the top of the window
        self.selectedColor = lambda: Globals.PrimaryColor  # The current active color
        self.y = Window.height - self.height

        # Default value is today
        self.selectedDate = kwargs["date"] if "date" in kwargs else date.today()

        self.visibleDate = self.selectedDate.replace(day=1)  # The month currently visible on the datepicker

        # Set up layout
        self.orientation = "vertical"

        # The size of the top bar containing the month and year
        self.topBarSize = kwargs["topBarSize"] if "topBarSize" in kwargs else 85

        # The white background behind the DatePicker, and the black line on the bottom of it
        self.background = Rectangle(pos=(self.pos[0], self.pos[1] + 1), size=(self.size[0], self.size[1] - 1))
        self.bottomBorder = Rectangle(pos=self.pos, size=self.size)

        # Update the size of the background and line with the widget
        self.bind(size=lambda inst, size: setattr(self.background, "size", (size[0], size[1] - 1)))
        self.bind(pos=lambda inst, pos: setattr(self.background, "pos", (pos[0], pos[1] + 1)))
        self.bind(size=lambda inst, size: setattr(self.bottomBorder, "size", size))
        self.bind(pos=lambda inst, pos: setattr(self.bottomBorder, "pos", pos))

        # Add the bacground to the canvas of the widget
        self.canvas.add(Color(0, 0, 0, 1))
        self.canvas.add(self.bottomBorder)
        self.canvas.add(Color(1, 1, 1, 1))
        self.canvas.add(self.background)

        # Month names
        self.month_names = ('January',
        'February',
        'March',
        'April',
        'May',
        'June',
        'July',
        'August',
        'September',
        'October',
        'November',
        'December')

        # The top containing the buttons for switching months and the current month and year
        self.header = BoxLayout(orientation="horizontal", size_hint_y=None, height=self.topBarSize)

        # The previous month button
        self.header.add_widget(Button(on_press=self.lastMonth, background_normal="CalendarInactive.png", font_size=36,
            background_down="CalendarInactive.png", background_color=self.selectedColor(), size_hint_x=None, width=185,
            text="<", color=(1, 1, 1, 1) if shouldUseWhiteText(self.selectedColor()) else (0, 0, 0, 1)))

        # The current month and year
        self.header.add_widget(Button(background_normal="CalendarInactive.png",
            background_down="CalendarInactive.png", background_color=self.selectedColor(),
            text=self.month_names[self.visibleDate.month - 1] + " " + str(self.visibleDate.year), width=50,
            font_size=36, color=(1, 1, 1, 1) if shouldUseWhiteText(self.selectedColor()) else (0, 0, 0, 1)))

        # Update the month and year text as the user switches them
        self.bind(visibleDate=lambda inst, visibleDate: setattr(self.header.children[1], "text",
            self.month_names[visibleDate.month - 1] + " " + str(self.visibleDate.year)))

        # The next month button
        self.header.add_widget(Button(on_press=self.nextMonth, background_normal="CalendarInactive.png", font_size=36,
            background_down="CalendarInactive.png", background_color=self.selectedColor(), size_hint_x=None, width=185,
            text=">  ", color=(1, 1, 1, 1) if shouldUseWhiteText(self.selectedColor()) else (0, 0, 0, 1),
            halign="right"))

        # Updates the color of the header when the primary color changes
        def updateBodyColor(*args):
            for i in self.header.children:
                i.background_color = self.selectedColor()

        Globals.redraw.append((None, updateBodyColor))

        # The layout containing all of the days
        self.body = GridLayout(cols=7)

        # Fills in the days
        self.populate_body()

        self.add_widget(self.header)
        self.add_widget(self.body)

    def populate_body(self):
        # Clear any existing days first
        self.body.clear_widgets()

        # Add as many rows as is necessary for the given month
        self.body.rows = int(ceil(getMonthLength(self.visibleDate.month, self.visibleDate.year) +
                                  (getStartDay(self.visibleDate.month, (self.visibleDate.year + 1) % 7)) / 7))

        # Add filler widgets at the beginning of the month
        for i in range((getStartDay(self.visibleDate.month, self.visibleDate.year) + 1) % 7):
            self.body.add_widget(Button(on_press=lambda inst: self.dismiss(self.selectedDate),
                background_color=(0, 0, 0, 0)))  # Filler widget

        # Add each day
        currentDate = date(year=self.visibleDate.year, month=self.visibleDate.month,
            day=1)  # The date of the current button
        for i in range(getMonthLength(self.visibleDate.month, self.visibleDate.year)):
            btn = Button(background_normal="Circle3.png", background_down="Circle3.png", background_color=(0, 0, 0, 0),
                on_press=self.select, text=str(i + 1), font_size=36, color=(0, 0, 0, 1))
            if currentDate == self.selectedDate:  # If the date is today, give it the circle image
                btn.background_color = self.selectedColor()
                btn.color = (1, 1, 1, 1) if shouldUseWhiteText(self.selectedColor()) else (0, 0, 0, 1)
                # Update the color automatically
                Globals.redraw.append((btn, lambda btn: setattr(btn, "background_color", Globals.PrimaryColor)))
            self.body.add_widget(btn)
            currentDate += timedelta(days=1)  # Move the date of the current button

        # Add filler widgets at the end of the month
        for i in range(7 - len(self.body.children) % 7):
            self.body.add_widget(Button(on_press=lambda inst: self.dismiss(self.selectedDate),
                background_color=(0, 0, 0, 0)))

    def select(self, btn): # Sets the date to the date of the clicked button, or dismisses the datepicker
        newDate = date(year=self.visibleDate.year, month=self.visibleDate.month, day=int(btn.text))
        if newDate == self.selectedDate:
            self.dismiss(newDate)
            return
        self.selectedDate = newDate
        self.populate_body()

    def lastMonth(self, *args): # Move the datepicker back one month
        if self.visibleDate.month == 1:
            self.visibleDate = date(year=self.visibleDate.year - 1, month=12, day=1)
        else:
            self.visibleDate = date(year=self.visibleDate.year, month=self.visibleDate.month - 1, day=1)
        self.populate_body()

    def nextMonth(self, *args): # Move the datepicker forward one month
        if self.visibleDate.month == 12:
            self.visibleDate = date(year=self.visibleDate.year + 1, month=1, day=1)
        else:
            self.visibleDate = date(year=self.visibleDate.year, month=self.visibleDate.month + 1, day=1)
        self.populate_body()

    def dismiss(self, *args): # Dismisses the widget, and returns the date. Overridden in tabview.
        pass


class MyApp(App):  # Test for the datePicker
    def build(self):
        # Test the widget
        widget = DatePicker(size=Window.size)

        # Propagate window resize to app
        Window.bind(size=lambda inst, size: setattr(widget, "size", size))
        return widget


if __name__ == '__main__':
    MyApp().run()
