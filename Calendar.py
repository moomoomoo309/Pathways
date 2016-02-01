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
from kivy.core.window import Window
from datetime import datetime
from Event import Event
from kivy.graphics import Rectangle, Color

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

class CalendarLessThan30Days(Widget):
    outerLayout = BoxLayout(orientation="vertical", size=Window.size,
                            spacing=1)  # Contains the top bar "head" and body.
    innerLayout = BoxLayout(orientation="horizontal", size=Window.size)  # Sizes the bodyView
    hourBar = BoxLayout(orientation="vertical", size=Window.size, size_hint_x=.2)  # Has the time being viewed
    bodyLayout = GridLayout(rows=1, width=Window.width, size_hint_y=None, height=2048)  # Has the hourbar and inner body
    innerBodyLayout = GridLayout(rows=1)  # Contains the actual body
    bodyView = ScrollView(size_hint_y=None, width=Window.width)  # Scrollable bits, dayBar and actual body
    days = BoundedNumericProperty(7, min=1, max=7)
    dayBarLayout = GridLayout(rows=1, spacing=1, size_hint_y=.15)  # Layout for the dayBar, if it exists, and body
    dayList = []
    eventHeight = 65
    startDate = ObjectProperty(date.today())

    def __init__(self, **kwargs):
        super(CalendarLessThan30Days, self).__init__()
        # Propagate resize to children below
        self.bind(size=lambda inst, size: setattr(self.outerLayout, "size", size))
        self.outerLayout.bind(width=lambda inst, width: setattr(self.innerLayout, "width", width))
        self.innerLayout.bind(size=lambda inst, size: setattr(self.bodyView, "size", (size[0], self.height * .8675)))
        self.bodyView.bind(width=lambda inst, width: setattr(self.bodyLayout, "width", width))

        # Forces the relativeLayout to size the dayBar to a constant(-ish) width

        self.hourBar.realWidth = 100  # Test width, should be width of the largest time label when done
        self.hourBar.bind(size=lambda inst, size: setattr(inst, "size_hint_x", float(inst.realWidth) / Window.width))
        for i in range(24):
            lbl = Button(text=str((i + 11) % 12 + 1) + " " + ("AM" if i < 12 else "PM"), color=(0, 0, 0, 1),
                         background_normal="CalendarActive.png", background_down="CalendarActive.png", halign="center",
                         valign="top", text_size=(100, 2048 / 24))
            lbl.bind(size=lambda inst, size: setattr(lbl, "text_size", size))
            self.hourBar.add_widget(lbl)

        # Adding layout structure below...
        self.add_widget(self.outerLayout)
        self.outerLayout.add_widget(self.innerLayout)
        self.innerLayout.add_widget(self.bodyView)
        self.bodyView.add_widget(self.bodyLayout)
        self.bodyLayout.add_widget(self.hourBar)
        self.bodyLayout.add_widget(self.innerBodyLayout)
        # Test widget
        WidgetsToAddOnAGivenDay = []  # This is for demo purposes, it will be removed.
        if self.days > 1:  # Add the hour bar if it's not one day
            self.outerLayout.add_widget(self.dayBarLayout, len(self.outerLayout.children))
            self.weekButton = Button(text=str(self.startDate.isocalendar()[1]), size_hint_x=None, color=(0, 0, 0, 1),
                                     background_normal="CalendarActive.png", background_down="CalendarActive.png")
            self.hourBar.bind(width=lambda inst, width: setattr(self.weekButton, "width", width))
            self.dayBarLayout.add_widget(self.weekButton)
        dayNames = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")
        for i in range(self.days):
            self.dayBarLayout.add_widget(Button(background_normal="CalendarInactive.png", halign="center",
                                                background_down="CalendarInactive.png", color=(0, 0, 0, 1),
                                                text=dayNames[(self.startDate.isocalendar()[2] + i) % 7] + "\n" + str(
                                                    self.startDate.month) + "/" + str(
                                                    self.startDate.day + i)))  # Test Widget
            # Place your events using pos_hint and size_hint!
            dayLayout = RelativeLayout()
            dayLayout.canvas.before.add(Color(1, 1, 1, 1))
            rect = Rectangle(pos=Widget.to_widget(dayLayout, 0, 0), size=dayLayout.size)
            dayLayout.bind(
                size=lambda inst, size: setattr(inst.canvas.before.children[len(inst.canvas.before.children) - 1],
                                                "size", (size[0] - 1, size[1])))
            dayLayout.bind(
                pos=lambda inst, pos: setattr(inst.canvas.before.children[len(inst.canvas.before.children) - 1], "pos",
                                              inst.to_local(pos[0] + 1, pos[1])))
            dayLayout.canvas.before.add(rect)
            self.dayList.append(dayLayout)  # Put a layout for each day, so the columns are separate.

            self.innerBodyLayout.add_widget(self.dayList[i])
            # Test Widget
            event = Event(size_hint_y=float(self.eventHeight) / self.bodyLayout.height, x=1,
                          pos_hint={"center_y": timeToPos(datetime.now())},
                          name="TestButton" + str(i), background_normal="CalendarInactive.png",
                          background_down="CalendarInactive.png", background_color=(0, .5, 0, 1),
                          color=(0, 0, 0, 1), on_press=openEventGUI)
            event.bind(width=lambda inst, width: setattr(inst, "width", inst.parent.width - 1))
            self.dayList[i].add_widget(event)
            for event in WidgetsToAddOnAGivenDay:  # Sort them out by date before here
                event.pos_hint = {"center_y": timeToPos(event.time)}
                self.dayList[i].add_widget(event)

def openEventGUI(self):
    pass


def timeToPos(time):  # Returns the time to be given to pos_hint={"center_y".
    return 1 - (1.6 / 24 + float(time.hour - 1. + time.minute / 60) / 24.)
