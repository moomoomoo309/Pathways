from calendar import monthrange
from datetime import date

from kivy.properties import BooleanProperty, BoundedNumericProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget

from AsyncImageButton import AsyncImageButton


class Calendar30Days(Widget):
    randomImages = BooleanProperty(False)
    # Use random images on empty days
    online = BooleanProperty(True)
    # If randomImages is true, get images from the internet
    topBarSize = BoundedNumericProperty(75, min=0)
    # Size of the top bar for placement purposes
    startDate = ObjectProperty(allow_none=True, baseclass=date)
    # Lets you put in a date class instead of specifying MonthLength or MonthStart
    MonthLength = BoundedNumericProperty(monthrange(date.today().year, date.today().month)[1], min=28, max=31)
    # The length of the current month
    MonthStart = BoundedNumericProperty((date.today().replace(day=1).weekday() + 1) % 7, min=0, max=6)
    # The day of the week the month starts on
    gridSize = 0

    def __init__(self, **kwargs):
        super(Calendar30Days, self).__init__()  # I need this line for reasons.
        if self.startDate is not None:
            self.setDate(self.startDate)
        self.getImageSource = kwargs["getImageSource"] if "getImageSource" in kwargs else lambda \
                x: "CalendarInactive.png"
        self.size = kwargs["size"] if "size" in kwargs else [100, 100]
        self.pos = kwargs["pos"] if "pos" in kwargs else [0, 0]
        self.bind(size=self._resize)
        self.cols = 7
        self.rows = 7  # Extra row for dayNames

        # The grid is 7x7 because 7x6 isn't enough for months which start on Saturday
        if self.MonthLength + self.MonthStart < 36:
            self.rows = 6

        # Keep it within its bounds.
        self.spacing = 1

        # Put the children in a gridLayout
        self.Layout = GridLayout(pos=self.pos, size=self.size, rows=self.rows, cols=self.cols, spacing=self.spacing)

        # Populate the body and add the layout to the widget
        self.populate_body()
        self.add_widget(self.Layout)

    def populate_body(self):
        self.Layout.clear_widgets()
        self.gridSize = (self.size[0] / self.cols, self.size[1] / self.rows)

        # Add the names of the days of the week
        dayNames = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")
        for i in range(7):
            btn = Button(texture=None, background_normal="CalendarInactive.png",
                         background_down="CalendarActive.png",
                         # Used the first letter of each dayName
                         text="[color=000000][size=36]" + dayNames[i][0] + "[/color][/size]",
                         markup=True, halign="center", valign="middle", text_size=self.gridSize)
            btn.bind(size=lambda self, newVal: setattr(self, "text_size", newVal))
            # Keep the text_size correct so the text lines up correctly on resize
            self.Layout.add_widget(btn)
        for i in range(0, self.MonthStart):
            self.Layout.add_widget(
                    AsyncImageButton(source=self.getImageSource(None), allow_stretch=True, size=self.gridSize,
                                     keep_ratio=False,
                                     on_press=lambda x: setattr(x, "source", self.getImageSource(None))))
            # If the month doesn't start on a Monday, you need empty days.

        # Add all of the days
        for i in range(0, self.MonthLength):
            # The group means they act as radio buttons, so only one is toggleable at a time.
            # They will be changed to be normal buttons which switch to the day view with the date of the button.
            btn = ToggleButton(texture=None, background_normal="CalendarInactive.png",
                               background_down="CalendarActive.png", group="Calendar30Days",
                               text="[color=000000][size=36]" + str(i + 1) + "[/color][/size]",
                               markup=True, halign="left", valign="top", text_size=self.gridSize)
            btn.bind(size=lambda self, newVal: setattr(self, "text_size", newVal))
            # Keep text lined up on resize
            self.Layout.add_widget(btn)

        # Add filler days at the end of the month if necessary
        for i in range(0, self.rows * self.cols - self.MonthLength - self.MonthStart - 7):
            # Subtract 7 to remove dayNames
            self.Layout.add_widget(
                    AsyncImageButton(source=self.getImageSource(None), allow_stretch=True, size=self.gridSize,
                                     keep_ratio=False,
                                     on_press=lambda x: setattr(x, "source", self.getImageSource(None))))

    def _resize(self, *args): # Propogate resize to children
        self.gridSize = (self.size[0] / self.cols, self.size[1] / self.rows)
        self.Layout.size = self.size
        self.Layout.pos = self.pos

    def setDate(self, date): # Set the date to the given date
        self.MonthLength = monthrange(date.year, date.month)[1]
        self.MonthStart = (date.replace(day=1).weekday() + 1) % 7
        self.populate_body()
