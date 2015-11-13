from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton

from kivy.properties import BooleanProperty, BoundedNumericProperty

from AsyncImageButton import AsyncImageButton


# The grid which contains the 30(ish) days for each month
class Calendar30Days(GridLayout):
    randomImages = BooleanProperty(False)
    online = BooleanProperty(True)
    topBarSize = BoundedNumericProperty(0, min=0)

    def __init__(self, **kwargs):
        super(Calendar30Days, self).__init__()  # I need this line for reasons.
        MonthLength = kwargs["MonthLength"]
        # The length of the current month
        MonthStart = kwargs["MonthStart"]
        # The day of the week the month starts on
        self.pos = kwargs["pos"]
        # Get the position of the widget
        getImageSource = kwargs["getImageSource"]
        self.cols = 7
        self.rows = 6
        if MonthLength + MonthStart < 36:
            self.rows = 5
        # The grid is 7x6 because 7x5 isn't enough for months which start on Saturday
        self.size = kwargs["size"]
        # Keep it within its bounds.
        self.spacing = 1
        # The size of each box in the grid
        gridSize = (self.size[0] / self.cols, self.size[1] / self.rows)
        for i in range(0, MonthStart):
            self.add_widget(AsyncImageButton(source=getImageSource(None), allow_stretch=True, keep_ratio=False,
                                             size=gridSize))  # If the month doesn't start on a Monday, you need empty days.

        for i in range(0, MonthLength):
            self.add_widget(ToggleButton(texture=None, background_normal="CalendarInactive.png",
                                         background_down="CalendarActive.png", group="CalendarGrid_Days",
                                         text="[color=000000][size=36]" + str(i + 1) + "[/color][/size]",
                                         markup=True, halign="right", valign="top", text_size=gridSize))
            # The group means they act as radio buttons, so only one is toggleable at a time.
        for i in range(0, self.rows * self.cols - MonthLength - MonthStart):
            self.add_widget(
                AsyncImageButton(source=getImageSource(None), allow_stretch=True, keep_ratio=False, size=gridSize))
            # The empty images after the month in the calendar
