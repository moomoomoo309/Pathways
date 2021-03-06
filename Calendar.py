from __future__ import print_function

from calendar import monthrange
from copy import deepcopy
from datetime import date, timedelta
from math import sqrt, ceil
from os.path import isfile
from random import randint

from kivy.core.window import Window
from kivy.graphics import Rectangle, Color
from kivy.graphics.instructions import InstructionGroup
from kivy.lang import Builder
from kivy.properties import BooleanProperty, BoundedNumericProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import AsyncImage
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Widget

import Globals
from AsyncImageButton import AsyncImageButton
from ColorUtils import shouldUseWhiteText
from Event import Event, EventGUI
from eventCreationGUI import eventCreationGUI


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

    # Replace these with pictures of your choice.

    def __init__(self, **kwargs):
        super(Calendar30Days, self).__init__(**kwargs)  # I need this line for reasons.
        Globals.eventCallbacks.append(lambda *args: self.populate_body())
        self.originalImages = deepcopy(Globals.images)
        self.bind(selectedDate=lambda self, date: self.changeDate(date))
        self.bind(size=self._resize)

        # Keep it within its bounds.
        self.spacing = 1

        # Put the children in a gridLayout
        self.Layout = GridLayout(pos=self.pos, size=self.size, cols=7, spacing=self.spacing)
        self.Layout.bind(rows=lambda inst, rows: setattr(self, "rows", rows))

        # Populate the body and add the layout to the widget
        self.populate_body()
        btn = Button(size=self.size, on_press=lambda inst: eventCreationGUI().open(), background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0))
        self.bind(size=lambda inst, size: setattr(btn, "size", size))
        self.add_widget(btn)
        self.add_widget(self.Layout)

        Globals.onlineCallback.append(lambda val: setattr(self, "online", val))
        Globals.randomImagesCallback.append(lambda val: setattr(self, "randomImages", val))
        Globals.onlineCallback.append(lambda val: self.populate_body())
        Globals.randomImagesCallback.append(lambda val: self.populate_body())

    def populate_body(self):
        current_date = self.selectedDate.replace(day=1)
        _updateOnline(self, Globals.online)
        self.Layout.clear_widgets()
        # The grid is 7x7 because 7x6 isn't enough for months which start on Saturday
        if self.MonthLength + self.MonthStart < 36:
            self.Layout.rows = 6
        else:
            self.Layout.rows = 7

        # Add the names of the days of the week
        dayNames = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")
        for i in range(7):
            btn = Button(texture=None, background_normal="CalendarInactive.png",
                background_down="CalendarActive.png", height=75, size_hint_y=None,
                # Used the first letter of each dayName
                text="[color=000000][size=36]" + dayNames[i][0:3] + "[/color][/size]",
                markup=True, halign="center", valign="middle", on_press=lambda inst: eventCreationGUI().open())
            btn.bind(size=lambda btn, newVal: setattr(btn, "text_size", newVal))
            # Keep the text_size correct so the text lines up correctly on resize
            self.Layout.add_widget(btn)
        for i in range(0, self.MonthStart):
            self.Layout.add_widget(
                AsyncImageButton(source=_getImageSource(self, None), allow_stretch=True,
                    keep_ratio=False, anim_delay=1. / 7.5,
                    on_press=lambda inst: setattr(inst, "source", _getImageSource(self, inst.source))))

        # If the month doesn't start on a Monday, you need empty days.

        def openDayGUI(widgetRef):
            if widgetRef() is not None and len(widgetRef().children) > 1:
                DayGUI(widgetRef).open()

        # Add all of the days
        for i in range(0, self.MonthLength):
            btn = Button(texture=None, background_normal="CalendarInactive.png", background_down="",
                text="[color=000000][size=36]" + str(i + 1) + "[/color][/size]", markup=True, halign="left",
                valign="top", size_hint=(None, None), on_press=lambda inst: openDayGUI(lambda: inst.parent))
            # Limit the button size to the size of the text
            btn.size = btn.texture_size
            btn.bind(texture_size=lambda inst, size: setattr(inst, "size", size))

            dayLayout = StackLayout(spacing=(5, 2))
            dayLayout.add_widget(btn)
            dayLayout.background_color = Color(rgba=btn.background_color)
            dayLayout.background_color.rgba[3] = 1 if btn.background_color[0] == btn.background_color[1] == \
                                                      btn.background_color[2] == 1 else .5
            btn.bind(background_color=lambda inst, color: setattr(inst.parent.background_color, "rgba",
                color[0:3] + [(1 if color[0:3] == (1, 1, 1) else .5)]))
            dayLayout.background = Rectangle(size=dayLayout.size, pos=dayLayout.pos)
            dayLayout.bind(size=lambda inst, size: setattr(inst.background, "size", size))
            dayLayout.bind(pos=lambda inst, pos: setattr(inst.background, "pos", pos))
            dayLayout.canvas.before.add(dayLayout.background_color)
            dayLayout.canvas.before.add(dayLayout.background)

            def addDayEvent(event):
                event.fullSize = False
                event.shorten = True
                event.size = [i + 5 for i in event.texture_size]
                event.bind(texture_size=lambda inst, texture_size: setattr(inst, "size", [i + 5 for i in texture_size]))
                dayLayout.add_widget(event)

            if current_date in Globals.eventList:
                for event in Globals.eventList[current_date]:
                    copiedEvent = event.copy(fullSize=False, autoSize=False)
                    copiedEvent.size_hint = (None, None)
                    addDayEvent(copiedEvent)
            if self.startDate + timedelta(days=i) == self.selectedDate:
                btn.text = "[color=" + (
                    "FFFFFF" if shouldUseWhiteText(Globals.PrimaryColor[0:3] + [.5]) else "000000") + btn.text[
                           13:]
                btn.background_color = Globals.PrimaryColor[0:3] + [0]
                Globals.redraw.append(
                    (btn, lambda inst: setattr(inst, "background_color", Globals.PrimaryColor[0:3] + [0])))
                Globals.redraw.append((btn, lambda inst: setattr(inst, "text", "[color=" + (
                    "FFFFFF" if shouldUseWhiteText(Globals.PrimaryColor[0:3] + [.5]) else "000000") + inst.text[13:])))
            # Keep text lined up on resize
            self.Layout.add_widget(dayLayout)
            current_date += timedelta(days=1)

        # Add filler days at the end of the month if necessary
        for i in range(0, self.Layout.rows * self.Layout.cols - self.MonthLength - self.MonthStart - 7):
            # Subtract 7 to remove dayNames
            self.Layout.add_widget(
                AsyncImageButton(source=_getImageSource(self, None), allow_stretch=True,
                    keep_ratio=False,
                    on_press=lambda x: setattr(x, "source", _getImageSource(self, x.source))))

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


def _updateOnline(self, *args):
    for i in args:
        if bool(i) is not None:
            val = bool(i)
            break
    Globals.images = deepcopy(self.originalImages)
    for i in Globals.images:
        if isinstance(i, (int, long)):
            j = 0
            while j < len(Globals.images[i]):
                if not Globals.online:
                    if not isfile(Globals.images[i][j]):
                        Globals.images[i].remove(Globals.images[i][j])
                    else:
                        j += 1
                else:
                    if not "://" in Globals.images[i][j] and not isfile(Globals.images[i][j]):
                        Globals.images[i].remove(Globals.images[i][j])
                    else:
                        j += 1


def _getImageSource(self, blockedImage):  # Changes the images on the empty days on click
    img = None
    if Globals.randomImages and self.startDate.month - 1 in Globals.images is not None and len(Globals.images[
                self.startDate.month - 1]) > 0:
        img = Globals.images[self.startDate.month - 1][randint(0, len(Globals.images[self.startDate.month - 1]) - 1)]
        if len(Globals.images[self.startDate.month - 1]) >= 1 or img is None:
            iterations = 0
            while img == blockedImage or (not isfile(img) and not (Globals.online and "://" in img)):
                iterations += 1
                img = Globals.images[self.startDate.month - 1][
                    randint(0, len(Globals.images[self.startDate.month - 1]) - 1)]
                if iterations > 100:
                    return "CalendarInactive.png"
                elif isfile(img) or (Globals.online and "://" in img):
                    return img
    if img is not None and (isfile(img) or (Globals.online and "://" in img)):
        return img
    return "CalendarInactive.png"


class DayGUI(Popup):
    def __init__(self, *args, **kwargs):
        super(DayGUI, self).__init__(**kwargs)
        self.title = ""
        self.layout = GridLayout(rows=2)
        self.layout.bind(children=lambda inst, children: setattr(self.layout, "rows", int(ceil(sqrt(len(children))))))
        self.children[0].children[0].add_widget(self.layout)
        for i in args[0]().children:
            if isinstance(i, Event):
                self.layout.add_widget(EventGUI(lambda: i, size_hint=(.85, 1), dismiss=self.dismiss))


# noinspection PyTypeChecker,PyTypeChecker,PyTypeChecker,PyTypeChecker
class CalendarLessThan30Days(Widget):
    # Number of days in this calendar
    days = BoundedNumericProperty(7, min=1, max=7)
    # Height of each event
    eventHeight = 65
    randomImages = BooleanProperty(True)
    online = BooleanProperty(False)
    originalStartDate = ObjectProperty(date.today())

    def __init__(self, **kwargs):
        super(CalendarLessThan30Days, self).__init__(**kwargs)
        Globals.eventCallbacks.append(lambda *args: self.changeDate(self.originalStartDate))

        self.startDate = self.originalStartDate
        Globals.onlineCallback.append(lambda val: setattr(self, "online", val))
        Globals.randomImagesCallback.append(lambda val: setattr(self, "randomImages", val))
        Globals.randomImagesCallback.append(
            lambda val: setattr(self.backgroundImage, "source", _getImageSource(self, self.backgroundImage.source)))
        Globals.onlineCallback.append(
            lambda val: setattr(self.backgroundImage, "source", _getImageSource(self, self.backgroundImage.source)))
        self.dayBarLayout = GridLayout(rows=1, spacing=1, height=75,
            size_hint_y=None)  # Layout for the dayBar, if it exists, and body
        self.dayList = []  # Has layout for each day
        self.outerLayout = BoxLayout(orientation="vertical", size=Window.size,
            spacing=1)  # Contains the top bar "head" and body.
        self.innerLayout = BoxLayout(orientation="horizontal", size=Window.size)  # Sizes the bodyView
        self.hourBar = BoxLayout(orientation="vertical", size=Window.size, size_hint_x=.2)  # Has the time being viewed
        self.bodyLayout = GridLayout(rows=1, width=Window.width, size_hint_y=None, height=2048)  # Hourbar & inner body
        self.innerBodyLayout = GridLayout(rows=1)  # Contains the actual body
        self.bodyView = ScrollView(size_hint_y=None, width=Window.width,
            scroll_wheel_distance=75)  # Scrollable bits, dayBar and actual body

        # Drawing the image behind the calendar if the user overscrolls
        self.background = Rectangle(size=(self.width, self.bodyLayout.height), pos=(self.bodyView.x, -1000000))
        self.backgroundImage = AsyncImage(size=self.innerLayout.size, pos=self.innerLayout.pos,
            source=_getImageSource(self, None), allow_stretch=True, keep_ratio=False, anim_delay=1. / 7.5)
        self.backgroundImage.visible = self.backgroundImage.source != "CalendarInactive.png"

        def showHide(inst, pos):
            inst.pos = pos if inst.visible else (-100000, -100000)
            inst.source = _getImageSource(self, inst.source) if not inst.visible else self.backgroundImage.source

        self.backgroundImage.showHide = showHide
        self.backgroundImage.overlay = InstructionGroup()
        self.backgroundImage.canvas.add(self.backgroundImage.overlay)
        self.backgroundImage.overlay.add(Color(0, 0, 0, 1))
        self.backgroundImage.overlay.add(self.background)
        self.backgroundImage.visible = False
        self.backgroundImage.showHide(self.backgroundImage, self.bodyView.pos)
        self.bodyView.bind(size=lambda inst, size: setattr(self.backgroundImage, "size", size))
        self.bodyView.bind(pos=self.backgroundImage.showHide)
        self.bind(randomImages=lambda inst, val: setattr(self.backgroundImage, "source",
            _getImageSource(self, None) if Globals.randomImages else "CalendarInactive.png"))

        def getBackgroundHeight(self, inst):
            self.canvas.before.clear()
            self.backgroundImage.overlay.clear()
            if inst.scroll_y > 1.001:
                self.backgroundImage.visible = self.backgroundImage.source != "CalendarInactive.png"
                self.backgroundImage.showHide(self.backgroundImage, self.bodyView.pos)
                self.backgroundImage.overlay.add(Color(0, 0, 0, 1))
                self.backgroundImage.overlay.add(self.background)
                return -self.background.size[1] + self.bodyView.height - (inst.scroll_y - 1) * (
                    self.bodyLayout.height - self.bodyView.height)
            elif inst.scroll_y < 0:
                self.backgroundImage.visible = self.backgroundImage.source != "CalendarInactive.png"
                self.backgroundImage.showHide(self.backgroundImage, self.bodyView.pos)
                self.backgroundImage.overlay.add(Color(0, 0, 0, 1))
                self.backgroundImage.overlay.add(self.background)
                return -inst.scroll_y * (self.bodyLayout.height - self.bodyView.height)
            else:
                self.backgroundImage.overlay.add(Color(0, 0, 0, 1))
                self.backgroundImage.overlay.add(self.background)
                self.backgroundImage.visible = False
                self.backgroundImage.showHide(self.backgroundImage, self.bodyView.pos)
                return -1000000

        self.bind(width=lambda inst, width: setattr(self.background, "size", (width, self.background.size[1])))
        self.bodyView.bind(scroll_y=lambda inst, val: setattr(self.background, "pos",
            (self.background.pos[0], getBackgroundHeight(self, inst))))
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
                valign="top", text_size=(100, 2048 / 24), font_size=20)
            # Resize text_size to the text is aligned correctly
            lbl.bind(size=lambda inst, size: setattr(lbl, "text_size", size))
            self.hourBar.add_widget(lbl)
        self.changeDate(self.originalStartDate)
        self.bind(originalStartDate=lambda self, date: self.changeDate(date))

        # Adding layout structure below...
        self.add_widget(self.backgroundImage)
        self.add_widget(self.outerLayout)
        self.outerLayout.add_widget(self.innerLayout)
        self.innerLayout.add_widget(self.bodyView)
        self.bodyView.add_widget(self.bodyLayout)
        self.bodyLayout.add_widget(self.hourBar)
        self.bodyLayout.add_widget(self.innerBodyLayout)

    def changeDate(self, date):
        self.originalStartDate = date
        self.startDate = self.originalStartDate
        # If it's 7 days, start on sunday, otherwise put it in the middle
        if self.days == 7:
            self.startDate -= timedelta(days=self.startDate.isoweekday())
        else:
            self.startDate -= timedelta(days=self.days // 2)

        self.dayBarLayout.clear_widgets()
        self.innerBodyLayout.clear_widgets()
        dayNames = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")
        for i in range(self.days):
            # Label for the date of each column
            btn = Button(background_normal="CalendarInactive.png", halign="center",
                background_down="CalendarInactive.png", font_size=32,
                text=dayNames[(self.startDate.isocalendar()[2] + i) % 7][0:3] + "\n" + str(
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

            self.dayList[i].add_widget(Button(background_normal="", background_down="", background_color=(0, 0, 0, 0),
                on_press=self.openEventGUI, size_hint_y=None, height=self.bodyLayout.height))

            def timeToPos(time):  # Returns the y value of an event at the given time.
                return 1 - (1.6 / 24 + float(time.hour - 1. + time.minute / 60) / 24.)

            def add_event(event):
                self.dayList[i].bind(width=lambda inst, width: setattr(event, "width", width - 1))
                event.size_hint = (None, None)
                event.width = self.dayList[i].width
                Globals.redraw.append((event, lambda inst: setattr(inst, "background_color", Globals.PrimaryColor)))
                Globals.redraw.append((event, lambda inst: setattr(inst, "color", (1, 1, 1, 1) if shouldUseWhiteText(
                    Globals.PrimaryColor) else (0, 0, 0, 1))))
                event.pos_hint = {"center_y": timeToPos(event.start)}
                event.size_hint_y = float(self.eventHeight) / self.bodyLayout.height
                self.dayList[i].add_widget(event)

            if self.startDate + timedelta(days=i) in Globals.eventList:
                for localEvent in Globals.eventList[self.startDate + timedelta(days=i)]:
                    add_event(localEvent.copy(fullSize=True, autoSize=False))

        if self.days > 1:  # Add the hour bar if it's not one day
            if not self.dayBarLayout in self.outerLayout.children:
                self.outerLayout.add_widget(self.dayBarLayout)
            # This button has the current week of the year
            self.weekButton = Button(text=str(self.originalStartDate.isocalendar()[1]), size_hint_x=None,
                color=(0, 0, 0, 1), width=self.hourBar.width, font_size=20, on_press=self.openEventGUI,
                background_normal="CalendarActive.png", background_down="CalendarActive.png")
            self.hourBar.bind(width=lambda inst, width: setattr(self.weekButton, "width", width))
            self.dayBarLayout.add_widget(self.weekButton, len(self.dayBarLayout.children))

    def openEventGUI(self, *args):  # Not yet implemented
        eventCreationGUI().open()


Builder.load_file("./Calendar.kv")
