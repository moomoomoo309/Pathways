from __future__ import print_function

from calendar import monthrange
from datetime import date, timedelta
from datetime import datetime

from kivy.core.window import Window
from kivy.effects.opacityscroll import OpacityScrollEffect
from kivy.graphics import Rectangle, Color
from kivy.properties import BooleanProperty, BoundedNumericProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

import Globals
from AsyncImageButton import AsyncImageButton
from ColorUtils import shouldUseWhiteText
from Event import Event


class Calendar30Days(Widget):
    # Use random images on empty days
    randomImages = BooleanProperty(False)
    # If randomImages is true, get images from the internet
    online = BooleanProperty(True)
    # Size of the top bar for placement purposes
    topBarSize = BoundedNumericProperty(75, min=0)
    # Lets you put in a date class instead of specifying MonthLength or MonthStart
    startDate = ObjectProperty(date.today().replace(day=1), allow_none=True, baseclass=date)
    # The length of the current month
    MonthLength = BoundedNumericProperty(30, min=28, max=31)
    # The day of the week the month starts on
    MonthStart = BoundedNumericProperty(0, min=0, max=6)
    # The date selected
    selectedDate = ObjectProperty(date.today())

    def __init__(self, **kwargs):
        super(Calendar30Days, self).__init__(**kwargs)  # I need this line for reasons.

        self.getImageSource = kwargs["getImageSource"] if "getImageSource" in kwargs else lambda x: ""
        self.bind(selectedDate=lambda self, date: self.changeDate(date))
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

        # Add the names of the days of the week
        dayNames = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")
        for i in range(7):
            btn = Button(texture=None, background_normal="CalendarInactive.png",
                background_down="CalendarActive.png", height=75, size_hint_y=None,
                # Used the first letter of each dayName
                text="[color=000000][size=36]" + dayNames[i][0:3] + "[/color][/size]",
                markup=True, halign="center", valign="middle", on_press=self.openEventGUI)
            btn.bind(size=lambda btn, newVal: setattr(btn, "text_size", newVal))
            # Keep the text_size correct so the text lines up correctly on resize
            self.Layout.add_widget(btn)
        for i in range(0, self.MonthStart):
            self.Layout.add_widget(
                AsyncImageButton(source=self.getImageSource(None), allow_stretch=True,
                    keep_ratio=False,
                    on_press=lambda x: setattr(x, "source", self.getImageSource(None))))
        # If the month doesn't start on a Monday, you need empty days.

        # Add all of the days
        for i in range(0, self.MonthLength):
            btn = Button(texture=None, background_normal="CalendarInactive.png",
                background_down="CalendarActive.png",
                text="[color=000000][size=36]" + str(i + 1) + "[/color][/size]",
                markup=True, halign="left", valign="top")
            btn.bind(size=lambda self, newVal: setattr(self, "text_size", newVal))
            if self.startDate + timedelta(days=i) == self.selectedDate:
                btn.text = "[color=" + ("FFFFFF" if shouldUseWhiteText(Globals.PrimaryColor) else "000000") + btn.text[
                13:]
                btn.background_color = Globals.PrimaryColor
                Globals.redraw.append((btn, lambda inst: setattr(inst, "background_color", Globals.PrimaryColor)))
                Globals.redraw.append((btn, lambda inst: setattr(inst, "text", "[color=" + (
                    "FFFFFF" if shouldUseWhiteText(Globals.PrimaryColor) else "000000") + inst.text[13:])))
            # Keep text lined up on resize
            self.Layout.add_widget(btn)

        # Add filler days at the end of the month if necessary
        for i in range(0, self.rows * self.cols - self.MonthLength - self.MonthStart - 7):
            # Subtract 7 to remove dayNames
            self.Layout.add_widget(
                AsyncImageButton(source=self.getImageSource(None), allow_stretch=True,
                    keep_ratio=False,
                    on_press=lambda x: setattr(x, "source", self.getImageSource(None))))

    def _resize(self, *args):  # Propogate resize to children
        self.Layout.size = self.size
        self.Layout.pos = self.pos

    def changeDate(self, date):  # Set the date to the given date
        if self.selectedDate != date:
            self.selectedDate = date
            self.startDate = date.replace(day=1)
            self.MonthLength = monthrange(date.year, date.month)[1]
            self.MonthStart = (self.startDate.weekday() + 1) % 7
            self.populate_body()

    def openEventGUI(self, day):  # Not yet implemented
        pass


class CalendarLessThan30Days(Widget):
    # Number of days in this calendar
    days = BoundedNumericProperty(7, min=1, max=7)
    # Height of each event
    eventHeight = 65
    originalStartDate = ObjectProperty(date.today())

    def __init__(self, **kwargs):
        super(CalendarLessThan30Days, self).__init__(**kwargs)
        self.dayBarLayout = GridLayout(rows=1, spacing=1, height=75,
            size_hint_y=None)  # Layout for the dayBar, if it exists, and body
        self.dayList = []  # Has layout for each day
        self.outerLayout = BoxLayout(orientation="vertical", size=Window.size,
            spacing=1)  # Contains the top bar "head" and body.
        self.innerLayout = BoxLayout(orientation="horizontal", size=Window.size)  # Sizes the bodyView
        self.hourBar = BoxLayout(orientation="vertical", size=Window.size, size_hint_x=.2)  # Has the time being viewed
        self.bodyLayout = GridLayout(rows=1, width=Window.width, size_hint_y=None, height=2048)  # Hourbar & inner body
        self.innerBodyLayout = GridLayout(rows=1)  # Contains the actual body
        self.bodyView = ScrollView(size_hint_y=None, width=Window.width, scroll_wheel_distance=75,
            effect_y=OpacityScrollEffect())  # Scrollable bits, dayBar and actual body
        self.backgroundImage = Rectangle(source='Circle.png', size=self.innerLayout.size, pos=self.innerLayout.pos)
        self.background = Rectangle(size=(self.width,self.bodyLayout.height), pos=(self.bodyView.x,-1000000))

        self.canvas.before.add(self.backgroundImage)
        self.canvas.before.add(Color(0, 1, 1, 1))
        self.canvas.before.add(self.background)
        def getBackgroundHeight(self,inst):
            if inst.scroll_y>1.001:
                val= self.bodyLayout.height - inst.scroll_y * (self.bodyLayout.height - self.bodyView.height)
                print(val)
                return val
            elif inst.scroll_y<0:
                return -self.background.size[1]-(inst.scroll_y * (self.bodyLayout.height-self.bodyView.height))
            else:
                return -1000000
        self.bind(width=lambda inst,width: setattr(self.background, "size", (width, self.background.size[1])))
        self.bodyView.bind(scroll_y=lambda inst,val: setattr(self.background,"pos",(self.background.pos[0],getBackgroundHeight(self,inst))))
        # Propagate resize to children below
        self.innerLayout.bind(size=lambda inst, size: setattr(self.backgroundImage, "size", size))
        self.innerLayout.bind(pos=lambda inst, pos: setattr(self.backgroundImage, "pos", pos))
        self.bind(size=lambda inst, size: setattr(self.outerLayout, "size", size))
        self.outerLayout.bind(width=lambda inst, width: setattr(self.innerLayout, "width", width))
        if self.days > 1:
            self.innerLayout.bind(
                size=lambda inst, size: setattr(self.bodyView, "height", self.innerLayout.height))
        # self.dayBarLayout.bind(size=lambda _,__: setattr(self.innerLayout,"y",self.height - self.dayBarLayout.height))
        else:  # If it's one day, you can remove the top bar.
            self.innerLayout.height = self.height
            self.innerLayout.bind(size=lambda inst, size: setattr(self.bodyView, "size", (size[0], self.height)))
        self.bodyView.bind(width=lambda inst, width: setattr(self.bodyLayout, "width", width))

        # Forces the relativeLayout to size the dayBar to a constant(-ish) width
        self.hourBar.realWidth = 100
        self.hourBar.bind(size=lambda inst, size: setattr(inst, "size_hint_x", float(inst.realWidth) / Window.width))
        # Adds labels for each hour to the hourbar
        for i in range(24):
            lbl = Button(text=str((i + 11) % 12 + 1) + " " + ("AM" if i < 12 else "PM"), color=(0, 0, 0, 1),
                background_normal="CalendarActive.png", background_down="CalendarActive.png", halign="center",
                valign="top", text_size=(100, 2048 / 24))
            # Resize text_size to the text is aligned correctly
            lbl.bind(size=lambda inst, size: setattr(lbl, "text_size", size))
            self.hourBar.add_widget(lbl)
        self.changeDate(self.originalStartDate)
        self.bind(originalStartDate=lambda self, date: self.changeDate(date))

        # Adding layout structure below...
        self.add_widget(self.outerLayout)
        self.outerLayout.add_widget(self.innerLayout)
        self.innerLayout.add_widget(self.bodyView)
        self.bodyView.add_widget(self.bodyLayout)
        self.bodyLayout.add_widget(self.hourBar)
        self.bodyLayout.add_widget(self.innerBodyLayout)

        self.bodyView._viewport.bind(size=lambda inst, size: setattr(self.background, "size", size))
        self.bodyView._viewport.bind(pos=lambda inst, pos: setattr(self.background, "pos", pos))

    def changeDate(self, date):
        self.originalStartDate = date
        self.startDate = self.originalStartDate
        # If it's 7 days, start on sunday, otherwise put it in the middle
        if self.days == 7:
            self.startDate -= timedelta(days=self.startDate.isoweekday())
        else:
            self.startDate -= timedelta(days=self.days // 2)
        WidgetsToAddOnAGivenDay = []  # This is for demo purposes, it will be replaced with a central event storage.

        self.dayBarLayout.clear_widgets()
        self.innerBodyLayout.clear_widgets()
        dayNames = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")
        for i in range(self.days):
            # Label for the date of each column
            btn = Button(background_normal="CalendarInactive.png", halign="center",
                background_down="CalendarInactive.png",
                text=dayNames[(self.startDate.isocalendar()[2] + i) % 7] + "\n" + str(
                    (self.startDate + timedelta(days=i)).month) + "/" + str(
                    (self.startDate + timedelta(days=i)).day))
            # Color days before today gray, today the PrimaryColor, and days after today black.
            if self.days != 7:
                if i == self.days // 2:
                    # Make sure it updates with PrimaryColor
                    currentColor = lambda: Globals.PrimaryColor
                    Globals.redraw.append((btn, lambda btn: setattr(btn, "color", Globals.PrimaryColor)))
                elif i < self.days // 2:
                    currentColor = lambda: (.45, .45, .45, 1)
                else:
                    currentColor = lambda: (0, 0, 0, 1)
            else:
                if i == self.originalStartDate.isoweekday() % 7:
                    # Make sure it updates with PrimaryColor
                    currentColor = lambda: Globals.PrimaryColor
                    Globals.redraw.append((btn, lambda btn: setattr(btn, "color", Globals.PrimaryColor)))
                elif i < self.originalStartDate.isoweekday() % 7:
                    currentColor = lambda: (.45, .45, .45, 1)
                else:
                    currentColor = lambda: (0, 0, 0, 1)
            btn.color = currentColor()
            self.dayBarLayout.add_widget(btn)
            dayLayout = RelativeLayout()  # Layout for the events in the calendar
            # Add the white background behind the layout
            dayLayout.canvas.before.add(Color(1, 1, 1, 1))
            rect = Rectangle(pos=dayLayout.to_widget(0, 0), size=dayLayout.size)
            # Resize the layout on size change
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
                background_down="CalendarInactive.png", background_color=Globals.PrimaryColor,
                color=(1, 1, 1, 1) if shouldUseWhiteText(Globals.PrimaryColor) else (0, 0, 0, 1),
                on_press=self.openEventGUI)
            event.bind(width=lambda inst, width: setattr(inst, "width", inst.parent.width - 1))
            Globals.redraw.append((event, lambda inst: setattr(inst, "background_color", Globals.PrimaryColor)))
            Globals.redraw.append((event, lambda inst: setattr(inst, "color", (1, 1, 1, 1) if shouldUseWhiteText(
                Globals.PrimaryColor) else (0, 0, 0, 1))))
            self.dayList[i].add_widget(event)
            for event in WidgetsToAddOnAGivenDay:  # Sort them out by date before here
                event.pos_hint = {"center_y": timeToPos(event.time)}
                self.dayList[i].add_widget(event)

        if self.days > 1:  # Add the hour bar if it's not one day
            if not self.dayBarLayout in self.outerLayout.children:
                self.outerLayout.add_widget(self.dayBarLayout)
            # This button has the current week of the year
            self.weekButton = Button(text=str(self.originalStartDate.isocalendar()[1]), size_hint_x=None,
                color=(0, 0, 0, 1), width=self.hourBar.width,
                background_normal="CalendarActive.png", background_down="CalendarActive.png")
            self.hourBar.bind(width=lambda inst, width: setattr(self.weekButton, "width", width))
            self.dayBarLayout.add_widget(self.weekButton, len(self.dayBarLayout.children))

    def openEventGUI(self, event):  # Not yet implemented
        pass


def timeToPos(time):  # Returns the time to be given to pos_hint={"center_y".
    return 1 - (1.6 / 24 + float(time.hour - 1. + time.minute / 60) / 24.)
