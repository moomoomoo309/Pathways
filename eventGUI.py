from __future__ import print_function
from datetime import datetime

from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ListProperty, ObjectProperty
from circulardatetimepicker import CircularTimePicker
from datetimepicker import DatetimePicker
from tzlocal import get_localzone

from Event import Event
from roulette import CyclicSlot, CyclicRoulette


class eventGUI(Popup):
    start=ObjectProperty(baseclass=datetime)
    startTimezone=StringProperty("")
    end=ObjectProperty(baseclass=datetime)
    endTimezone=StringProperty("")
    name=StringProperty("")
    description=StringProperty("")
    location=StringProperty("")
    repeat=StringProperty("")
    reminders=StringProperty("")
    allDay=BooleanProperty(False)
    def __init__(self,*args,**kwargs):
        super(eventGUI,self).__init__(*args,**kwargs)
        self.size_hint_y=None
        self.event=None
        self.title="Create an event"
        self.outerLayout=BoxLayout(orientation="vertical")
        self.nameDialog=inputLine(text="Name")
        self.nameDialog.bind(output=lambda inst,name: setattr(self,"name",name))
        self.startDialog=picker(text="Start Time")
        self.start=self.startDialog.date
        self.startDialog.bind(date=lambda inst, date: setattr(self,"start",date))
        self.startTimezone=get_localzone().zone
        self.endDialog=picker(text="End time")
        self.end=self.endDialog.date
        self.endDialog.bind(date=lambda inst, date: setattr(self,"end",date))
        self.endTimezone=get_localzone().zone
        self.descriptionDialog=inputLine(text="Description")
        self.descriptionDialog.bind(output=lambda inst,description: setattr(self,"description",description))
        self.locationDialog=inputLine(text="location")
        self.locationDialog.bind(output=lambda inst,location: setattr(self,"location",location))
        self.repeatDialog=dropDown()
        self.repeatDialog.bind(output=lambda inst,text: setattr(self,"repeat",text))
        self.repeat=self.repeatDialog.output
        self.remindersDialog=inputLine(text="reminders")
        self.remindersDialog.bind(output=lambda inst,reminders: setattr(self,"reminders",reminders))

        for i in [self.nameDialog,self.startDialog,self.endDialog,self.descriptionDialog,self.locationDialog,self.repeatDialog,self.remindersDialog]:
            self.outerLayout.add_widget(i)
        self.add_widget(self.outerLayout)

    def on_dismiss(self):
        for i in ["start","startTimezone","end","endTimezone","name","description","location","repeat","reminders","allDay"]:
            if not (hasattr(self,i) and getattr(self,i)!=""):
                print(i)
                return True

        self.event=Event(start=self.start,startTimezone=self.startTimezone,end=self.end,
            endTimezone=self.endTimezone,name=self.name,description=self.description,location=self.location,
            repeat=self.repeat,reminders=self.reminders,allDay=self.allDay)



class inputLine(BoxLayout):
    text=StringProperty("")
    def __init__(self, **kwargs):
        super(inputLine,self).__init__(**kwargs)

class picker(BoxLayout):
    text=StringProperty("")

class listCyclicSlot(CyclicSlot):
    def slot_value(self, index):
        if isinstance(self.values,(list,tuple,dict)) and len(self.values)>0:
            val = self.values[int(abs(index))%max(len(self.values),1)]
        else:
            val = None
        return val

class listCyclicRoulette(CyclicRoulette):
    tick_cls = listCyclicSlot
    values=ListProperty()
    def __init__(self,**kwargs):
        super(listCyclicRoulette,self).__init__(**kwargs)
        self.tick.values=self.values

    def round_(self, val):
        return int(round(self.get_index_mid()))

    def values(self):
        return self.tick.values

class MonthCyclicRoulette(listCyclicRoulette):
    values=["January","February","March","April","May","June","July","August","September","October","November","December"]

class DayCyclicRoulette(CyclicRoulette):
    def on_cycle(self, selfAgain, cycle):
        if self.tick.cycle>cycle:
            self.select_and_center(min(cycle,self.selected_value))
        self.tick.cycle=self.cycle

class dropDown(BoxLayout):
    output=StringProperty("")

class timeCyclicRoulette(listCyclicRoulette):
    values=["Year(s)","Month(s)","Week(s)","Day(s)","Hour(s)","Minute(s)"]

Builder.load_file("./eventGUI.kv")

"""
    start = ObjectProperty(datetime.now(), baseclass=datetime)
    startTimezone = StringProperty(str(get_localzone()))
    end = ObjectProperty(datetime.now() + timedelta(hours=1), baseclass=datetime, allow_none=True)
    endTimeZone = StringProperty(str(get_localzone()))
    name = StringProperty("Unnamed Event")
    description = StringProperty()
    location = StringProperty()
    repeat = StringProperty()
    attendees = StringProperty()
    defaultReminder = BooleanProperty(False)
    reminders = ListProperty()
    fullSize = BooleanProperty(False)
    backgroundColor = ListProperty()
    allDay = BooleanProperty(False)
"""