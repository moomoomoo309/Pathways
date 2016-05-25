from __future__ import print_function

import collections

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget

import Globals
from Event import Event
from roulette import CyclicSlot, CyclicRoulette


class eventCreationGUI(Popup):
    allDay = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(eventCreationGUI, self).__init__(**kwargs)

    def on_dismiss(self):
        for i in ["start", "startTimezone", "end", "endTimezone", "name", "description", "location", "repeat",
            "allDay"]:
            if not (hasattr(self, i)):
                print(i)
                return True
        if self.submitted:
            if isinstance(Globals.eventCreationListener, collections.Callable):
                Globals.eventCreationListener(Event(start=self.start if self.start != "" else "Unnamed Event",
                    startTimezone=self.startTimezone, end=self.end, endTimezone=self.endTimezone, name=self.name,
                    description=self.description if self.description != "" else "No description",
                    location=self.location, repeat=self.repeat, reminders="", allDay=self.allDay))

    def submit(self):
        self.submitted = True
        self.dismiss()


class InputLine(BoxLayout):
    text = StringProperty("")


class Picker(BoxLayout):
    text = StringProperty("")
    minute_offset = NumericProperty(0)


class listCyclicSlot(CyclicSlot):
    def slot_value(self, index):
        if isinstance(self.values, (list, tuple, dict)) and len(self.values) > 0:
            val = self.values[int(abs(index)) % max(len(self.values), 1)]
        else:
            val = None
        return val


class listCyclicRoulette(CyclicRoulette):
    tick_cls = listCyclicSlot
    values = ListProperty()

    def __init__(self, **kwargs):
        super(listCyclicRoulette, self).__init__(**kwargs)
        self.tick.values = self.values

    def round_(self, val):
        return int(round(self.get_index_mid()))

    def values(self):
        return self.tick.values


class MonthCyclicRoulette(listCyclicRoulette):
    values = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
        "November", "December"]


class DayCyclicRoulette(CyclicRoulette):
    def on_cycle(self, selfAgain, cycle):
        if self.tick.cycle > cycle:
            self.select_and_center(min(cycle, self.selected_value))
        self.tick.cycle = self.cycle


class TimeCyclicRoulette(listCyclicRoulette):
    values = ["Year(s)", "Month(s)", "Week(s)", "Day(s)", "Hour(s)", "Minute(s)"]


class Divider(Widget):
    pass


class repeatPrompt(BoxLayout):
    output = StringProperty("")

    def __init__(self, **kwargs):
        super(repeatPrompt, self).__init__(**kwargs)
        Clock.schedule_once(self.late_init, .2)
        self.filler1 = None
        self.filler2 = None

    def late_init(self, *args):
        print("test")
        self.filler1 = Widget(size_hint_x=self.ids["every"].size_hint_x)
        self.ids["every"].bind(size_hint_x=lambda inst, hint: setattr(self.filler1, "size_hint_x", hint))
        self.filler2 = Widget(size_hint_x=self.ids["unitpicker"].size_hint_x)
        self.ids["unitpicker"].bind(size_hint_x=lambda inst, hint: setattr(self.filler2, "size_hint_x", hint))
        self.on_active(self.ids["checkbox"].active)

    def on_active(self, active):
        if active and not self.ids["every"] in self.children and not self.ids["unitpicker"] in self.children:
            self.remove_widget(self.filler1)
            self.remove_widget(self.filler2)
            self.add_widget(self.ids["every"])
            self.add_widget(self.ids["unitpicker"])
        else:
            self.remove_widget(self.ids["every"])
            self.remove_widget(self.ids["unitpicker"])
            self.add_widget(self.filler1)
            self.add_widget(self.filler2)

def getRepeatText(text):
    if text=="":
        return text
    numbers=text.split(" ")
    text="Every " + (numbers[0] + " " if numbers[0]!="1" else "") + TimeCyclicRoulette.values[int(numbers[1])][0:-3] + (
    "" if int(numbers[0]) == 1 else "s")
    print("Repeat = %s" % text)
    return text


Builder.load_file("./eventCreationGUI.kv")