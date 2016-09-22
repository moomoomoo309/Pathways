from __future__ import print_function

from datetime import datetime, timedelta, date

from dateutil import parser
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from tzlocal import get_localzone

import Globals
from ColorUtils import shouldUseWhiteText


class Event(BoxLayout, ButtonBehavior):
    start = ObjectProperty(datetime.now(), baseclass=(datetime,date))
    startTimezone = StringProperty(str(get_localzone()))
    end = ObjectProperty(datetime.now() + timedelta(hours=1), baseclass=(date,datetime), allow_none=True)
    endTimezone = StringProperty(str(get_localzone()))
    name = StringProperty("Unnamed Event")
    description = StringProperty("")
    location = StringProperty("", allow_none=True)
    repeat = StringProperty("", allow_none=True)
    attendees = StringProperty("", allow_none=True)
    defaultReminder = BooleanProperty(False)
    reminders = ListProperty(allow_none=True)
    fullSize = BooleanProperty(False)
    backgroundColor = ListProperty()
    allDay = BooleanProperty(False)
    texture_size = ObjectProperty(baseclass=(tuple, list), defaultvalue=(0, 0))
    autoSize = BooleanProperty(True)

    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)  # Another line needed for reasons.
        if self.start>self.end:
            self.start,self.end=self.end,self.start
        self.orientation = "vertical"
        self.on_press = kwargs["on_press"] if "on_press" in kwargs else self.on_press
        self.titleLabel = Button(text=self.name, size_hint_y=(.75 if self.fullSize else 1),
            on_press=lambda inst: self.on_press(self), halign="center", valign="top", shorten=True,
            background_normal="", background_down="", background_color=(0,0,0,1))
        if self.fullSize:
            self.titleLabel.text = str((self.start.hour - 1) % 12 + 1) + ":" + (
                "0" if self.start.minute < 10 else "") + str(self.start.minute) + " " + \
                                   str("PM" if self.start.hour > 12 else "AM") + "\n" + self.titleLabel.text
            if len(self.location)>0:
                self.titleLabel.text += " at " + self.location
        if self.autoSize:
            self.titleLabel.bind(texture_size=lambda inst, size: setattr(inst, "size", size))
            self.size_hint_y = None
        else:
            self.size_hint=(None,None)
            self.titleLabel.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        self.titleLabel.bind(background_color=lambda inst, background_color: setattr(inst, "color",
            (1, 1, 1, 1) if shouldUseWhiteText(background_color) else (0, 0, 0, 1)))
        self.descriptionLabel = Button(text=self.description, size_hint_y=.25,
            on_press=lambda inst: self.on_press(self), halign="left", shorten=True,
            background_normal="", background_down="", valign="top", background_color=(0,0,0,1))
        if self.autoSize:
            self.descriptionLabel.bind(texture_size=lambda inst, size: setattr(inst, "size", size))
        else:
            self.descriptionLabel.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        self.descriptionLabel.bind(background_color=lambda inst, background_color: setattr(inst, "color",
            (1, 1, 1, 1) if shouldUseWhiteText(background_color) else (0, 0, 0, 1)))

        def updateTextureSize(*args):
            if self.autoSize:
                self.texture_size = self.titleLabel.texture_size
            else:
                self.texture_size = (max(self.titleLabel.texture_size[0], self.descriptionLabel.texture_size[0]),
                self.titleLabel.texture_size[1] + self.descriptionLabel.texture_size[1])

        self.descriptionLabel.bind(texture_size=updateTextureSize)
        self.titleLabel.bind(texture_size=updateTextureSize)
        self.bind(fullSize=updateTextureSize)
        if len(self.backgroundColor) == 0:
            self.titleLabel.background_color = Globals.PrimaryColor
            self.titleLabel.isPrimary = True
            self.descriptionLabel.background_color = Globals.PrimaryColor
            self.descriptionLabel.isPrimary = True
        else:
            self.titleLabel.background_color = self.backgroundColor
            self.titleLabel.isPrimary = False
            self.descriptionLabel.background_color = self.backgroundColor
            self.descriptionLabel.isPrimary = False

        Globals.redraw.append((self.descriptionLabel, lambda inst: setattr(inst, "background_color",
            Globals.PrimaryColor if self.titleLabel.isPrimary else inst.background_color)))
        Globals.redraw.append((self.titleLabel, lambda inst: setattr(inst, "background_color",
            Globals.PrimaryColor if self.titleLabel.isPrimary else inst.background_color)))
        self.bind(name=lambda inst, name: setattr(inst.titleLabel, "text", name))
        self.bind(description=lambda inst, description: setattr(inst.descriptionLabel, "text", description))
        self.add_widget(self.titleLabel)
        if self.fullSize:
            self.add_widget(self.descriptionLabel)

        self.background = Color(*self.backgroundColor)
        self.bind(backgroundColor=lambda inst, color: setattr(self.background, "rgba", color))
        self.backgroundRect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda inst, pos: setattr(inst.backgroundRect, "pos", pos))
        self.bind(size=lambda inst, size: setattr(inst.backgroundRect, "size", size))

        self.titleLabel.bind(background_color=lambda inst, color: setattr(self.titleLabel, "color",
            (1, 1, 1, 1) if shouldUseWhiteText(color) else (0, 0, 0, 1)))
        self.descriptionLabel.bind(background_color=lambda inst, color: setattr(self.descriptionLabel, "color",
            (1, 1, 1, 1) if shouldUseWhiteText(color) else (0, 0, 0, 1)))

        updateTextureSize()

    def changeColor(self, color):
        self.titleLabel.background_color = color
        self.descriptionLabel.background_color = color
        self.titleLabel.isPrimary = False
        self.descriptionLabel.isPrimary = False

    def makePrimary(self):
        self.titleLabel.background_color = Globals.PrimaryColor
        self.descriptionLabel.background_color = Globals.PrimaryColor
        self.titleLabel.isPrimary = True
        self.descriptionLabel.isPrimary = True

    def isNow(self, time):
        return self.start < time < self.end

    def on_press(self, *args):
        EventGUI(lambda: self).open()

    def copy(self, **kwargs):
        return Event(name=self.name if not "name" in kwargs else kwargs["name"],
            start=self.start if not "start" in kwargs else kwargs["start"],
            startTimezone=self.startTimezone if not "startTimezone" in kwargs else kwargs["startTimezone"],
            end=self.end if not "end" in kwargs else kwargs["end"],
            endTimezone=self.endTimezone if not "endTimezone" in kwargs else kwargs["endTimezone"],
            description=self.description if not "description" in kwargs else kwargs["description"],
            location=self.location if not "location" in kwargs else kwargs["location"],
            repeat=self.repeat  if not "repeat" in kwargs else kwargs["repeat"],
            fullSize=self.fullSize  if not "fullSize" in kwargs else kwargs["fullSize"])

    @staticmethod
    def fromDict(eventDict):

        newEvent = Event(name=eventDict["summary"], location=eventDict["location"] if "location" in eventDict else "",
            description=eventDict["description"] if "description" in eventDict else "",
            start=parser.parse(eventDict["start"]["dateTime"]) if "dateTime" in eventDict["start"] else
            date(*[int(i) for i in eventDict["start"]["date"].split("-")]),
            startTimezone=eventDict["start"]["timeZone"] if "timeZone" in eventDict["start"] else "",
            end=parser.parse(eventDict["end"]["dateTime"]) if "dateTime" in eventDict["end"] else
            date(*[int(i) for i in eventDict["end"]["date"].split("-")]),
            endTimezone=eventDict["end"]["timeZone"] if "timeZone" in eventDict["end"] else "",
            repeat=eventDict["recurrence"] if "recurrence" in eventDict else "",
            attendees=eventDict["attendees"] if "attendees" in eventDict else "",
            reminders=eventDict["reminders"] if "reminders" in eventDict else "", background_color=Globals.PrimaryColor)
        return newEvent

    def asDict(self):
        event = {
            "summary": self.name,
            "location": self.location,
            "description": self.description,
            "start": {
                "dateTime": self.start.isoformat(),
                "timeZone": self.startTimezone
            },
            "end": {
                "dateTime": self.end.isoformat(),
                "timeZone": self.endTimezone
            },
            "recurrence": self.repeat,
            "attendees": self.attendees,
            "reminders": {
                "useDefault": self.defaultReminder,
                "overrides": self.reminders
            }
        }
        if self.allDay:
            event["start"]["date"] = event["start"]["dateTime"]
            event["start"].pop("dateTime")
            event["end"]["date"] = event["end"]["dateTime"]
            event["end"].pop("dateTime")

        for i in event:
            if event[i]=="":
                event.pop(i)
        return event


class EventGUI(Popup):
    eventReference = ObjectProperty()

    def __init__(self, *args, **kwargs):
        if len(args) > 0:
            self.eventReference = args[0]
        else:
            self.eventReference = kwargs["eventReference"]
        super(EventGUI, self).__init__(**kwargs)
        if "dismiss" in kwargs:
            self.dismiss = kwargs["dismiss"]


class DoubleLabel(BoxLayout):
    firstText = StringProperty("")
    secondText = StringProperty("")

    def __init__(self, *args, **kwargs):
        super(DoubleLabel, self).__init__(**kwargs)
        if len(args) > 1:
            self.firstText = args[0]
            self.secondText = args[1]


Builder.load_file("./Event.kv")
