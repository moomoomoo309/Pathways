from calendar import monthrange
from datetime import date

from kivy.properties import BooleanProperty, BoundedNumericProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget

from AsyncImageButton import AsyncImageButton


class CalendarSingleDay(Widget):  # This will be very similar to CalendarLessThan30Days.
    pass


class CalendarLessThan30Days(Widget):
    outerLayout = BoxLayout(orientation="horizontal")
    dayBarLayout = BoxLayout(orientation="vertical")
    bodyLayout = BoxLayout(orientation="vertical")
    bodyView = ScrollView(size_hint_y=None)
    days = BoundedNumericProperty(7, min=1, max=7)
    HourBar = RelativeLayout()
    dayList = []

    def __init__(self):
        super(CalendarLessThan30Days, self).__init__()
        self.outerLayout.add_widget(self.dayBarLayout)
        self.outerLayout.add_widget(self.bodyView)
        self.bodyView.add_widget(self.bodyLayout)
        if self.days > 1:
            self.bodyLayout.add_widget(self.HourBar)
        for i in range(self.days):
            self.dayList[i] = RelativeLayout()
            self.bodyLayout.add_widget(self.dayList[i])



class Calendar30Days(Widget):
    randomImages = BooleanProperty(False)
    online = BooleanProperty(True)
    topBarSize = BoundedNumericProperty(75, min=0)
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
        self.rows = 6
        if self.MonthLength + self.MonthStart < 36:
            self.rows = 5
        # The grid is 7x6 because 7x5 isn't enough for months which start on Saturday
        # Keep it within its bounds.
        self.spacing = 1
        self.Layout = GridLayout(pos=self.pos, size=self.size, rows=self.rows, cols=self.cols, spacing=self.spacing)
        self.populate_body()
        # The empty images after the month in the calendar
        self.add_widget(self.Layout)

    def populate_body(self):
        self.Layout.clear_widgets()
        self.gridSize = (self.size[0] / self.cols, self.size[1] / self.rows)
        for i in range(0, self.MonthStart):
            self.Layout.add_widget(
                AsyncImageButton(source=self.getImageSource(None), allow_stretch=True, size=self.gridSize,
                                 keep_ratio=False, on_press=lambda x: setattr(x, "source", self.getImageSource(None))))
            # If the month doesn't start on a Monday, you need empty days.

        for i in range(0, self.MonthLength):
            self.Layout.add_widget(ToggleButton(texture=None, background_normal="CalendarInactive.png",
                                                background_down="CalendarActive.png", group="Calendar30Days",
                                                text="[color=000000][size=36]" + str(i + 1) + "[/color][/size]",
                                                markup=True, halign="right", valign="top", text_size=self.gridSize))
            # The group means they act as radio buttons, so only one is toggleable at a time.
            # They will be changed to be normal buttons which switch to the day view with the date of the button.
        for i in range(0, self.rows * self.cols - self.MonthLength - self.MonthStart):
            self.Layout.add_widget(
                AsyncImageButton(source=self.getImageSource(None), allow_stretch=True, size=self.gridSize,
                                 keep_ratio=False, on_press=lambda x: setattr(x, "source", self.getImageSource(None))))

    def _resize(self, *args):
        self.gridSize = (self.size[0] / self.cols, self.size[1] / self.rows)
        self.Layout.size = self.size
        self.Layout.pos = self.pos

    def setDate(self, date):
        self.MonthLength = monthrange(date.year, date.month)[1]
        self.MonthStart = (date.replace(day=1).weekday() + 1) % 7
        self.populate_body()
