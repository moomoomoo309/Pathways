from __future__ import print_function

from datetime import date, datetime, timedelta
from operator import attrgetter

from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line
from kivy.properties import ObjectProperty, DictProperty
from kivy.clock import Clock

import Globals
from Event import Event
from eventCreationGUI import eventCreationGUI


class ScheduleView(ScrollView):
    currentDate = ObjectProperty(date.today())
    events = DictProperty()

    def __init__(self, **kwargs):
        super(ScheduleView, self).__init__(**kwargs)
        Globals.eventCallbacks.append(lambda eventList, event: self.add_event(event.copy(fullSize=True, autoSize=True)))
        self.scroll_wheel_distance = 75
        self.outerLayout = BoxLayout(orientation="vertical", size=self.size, size_hint_y=None)
        self.add_widget(self.outerLayout)

        for i in range(10):
            event = Event(name="testEvent" + str(i), description="testDescription" + str(i), fullSize=True,
                size_hint_y=None,
                autoSize=True)
            self.add_event(event)

        for i in range(1, 4):
            for j in range(5):
                event = Event(name="testEvent_" + str(i) + "_" + str(j),
                    description="testDescription_" + str(i) + "_" + str(j), fullSize=True, size_hint_y=None,
                    autoSize=True,
                    start=datetime.now() + timedelta(days=i), end=datetime.now() + timedelta(days=i, minutes=15))
                self.add_event(event)

        for eventDate in Globals.eventList:
            for localEvent in Globals.eventList[eventDate]:
                newEvent = localEvent.copy(fullSize=True, autoSize=True)
                newEvent.size_hint_y = None
                self.add_event(newEvent)

        self._updateTotalHeight()
        self.bind(height=self._updateTotalHeight)
        Clock.schedule_once(self._updateTotalHeight, 1)

    def _updateTotalHeight(self, *args):
        self.outerLayout.height = sum([sum(lst) for lst in
            map(lambda i: map(lambda k: k.height, i.children), self.outerLayout.children)]) + sum(
            [len(i.children) for i in self.outerLayout.children])
        for i in self.events:
            self.events[i].header.updateLine()
        for i in self.outerLayout.children:
            i.height = sum(map(lambda i: i.height + 1, i.children))

    def add_event(self, event):
        eventDate = date(year=event.start.year, month=event.start.month, day=event.start.day)
        if not eventDate in self.events:
            self.events[eventDate] = dayLayout(date=eventDate)
        event.bind(height=self._updateTotalHeight)
        self.events[eventDate].add_widget(event)
        if self.events[eventDate].parent is None:
            self.outerLayout.add_widget(self.events[eventDate])
        for i in self.children:
            i.children.sort(lambda inst, inst2: inst.date < inst2.date)
        self.events[eventDate].children[:-1] = sorted(self.events[eventDate].children[:-1],
            key=attrgetter("start", "name", "description"),
            reverse=True)
        self._updateTotalHeight()
        for i in self.events:
            self.events[i].header.updateLine()



class dateHeader(BoxLayout):
    def __init__(self, **kwargs):
        super(dateHeader, self).__init__(**kwargs)
        self.on_press = lambda *args: eventCreationGUI().open()
        self.orientation = "horizontal"
        self.spacing = 1
        self.size_hint_y = None
        self.date = kwargs["date"] if "date" in kwargs and kwargs["date"] is not None else date.today()
        self.label = Button(text=self.date.strftime("%a, %b %d"), color=(1, 1, 1, 1), font_size=36,
            text_size=(None, None), background_color=(0,0,0,0), size_hint_x=None, on_press=self.on_press)
        self.label.bind(texture_size=lambda inst, texture_size: setattr(self.label, "size", texture_size))
        self.label.bind(texture_size=lambda inst, texture_size: setattr(self, "height", texture_size[1]))
        self.lineColor = kwargs["lineColor"] if "lineColor" in kwargs else (1, 1, 1, 1)
        self.lineWidget = Button(background_color=(0, 0, 0, 0), on_press=self.on_press)
        self.lineWidget.canvas.add(Color(*self.lineColor))
        self.lineInstruction = Line(cap='none', width=5,
            points=[self.lineWidget.x + 10, self.lineWidget.y + self.lineWidget.height / 2,
                self.lineWidget.x + self.lineWidget.width, self.lineWidget.y + self.lineWidget.height / 2])
        self.lineWidget.canvas.add(self.lineInstruction)
        self.lineWidget.bind(size=lambda inst, size: setattr(self.lineInstruction, "points",
            [self.lineWidget.x + 10, self.lineWidget.y + self.lineWidget.height / 2,
                self.lineWidget.x + self.lineWidget.width, self.lineWidget.y + self.lineWidget.height / 2]))
        self.add_widget(Widget(size_hint_x=.05))
        self.add_widget(self.label)
        self.add_widget(self.lineWidget)

        self.bind(size=self.updateLine)
        Clock.schedule_once(self.updateLine, 1.2)

    def updateLine(self, *args):
        self.lineInstruction.points = [self.lineWidget.x + 9, self.lineWidget.y + self.lineWidget.height / 2,
            self.lineWidget.x + self.lineWidget.width, self.lineWidget.y + self.lineWidget.height / 2]
        Clock.schedule_once(lambda _: setattr(self.lineInstruction,"points",[self.lineWidget.x + 10, self.lineWidget.y + self.lineWidget.height / 2,
            self.lineWidget.x + self.lineWidget.width, self.lineWidget.y + self.lineWidget.height / 2]),.1)


class dayLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(dayLayout, self).__init__(**kwargs)
        self.size_hint_y = None
        self.date = kwargs["date"] if "date" in kwargs else None
        self.orientation = "vertical"
        self.spacing = 1
        self.header = dateHeader(date=self.date if hasattr(self, "date") else None)
        self.add_widget(self.header)
