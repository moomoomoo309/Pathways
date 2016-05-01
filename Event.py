from __future__ import print_function

from datetime import datetime, timedelta

from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from tzlocal import get_localzone

import Globals
from ColorUtils import shouldUseWhiteText


class Event(BoxLayout, ButtonBehavior):
    start = ObjectProperty(datetime.now(), baseclass=datetime)
    startTimezone = StringProperty(str(get_localzone()))
    end = ObjectProperty(datetime.now() + timedelta(hours=1), baseclass=datetime, allow_none=True)
    endTimezone = StringProperty(str(get_localzone()))
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

    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)  # Another line needed for reasons.
        self.orientation = "vertical"
        self.on_press = kwargs["on_press"] if "on_press" in kwargs else self.on_press
        self.titleLabel = Button(text=self.name, size_hint_y=(.75 if self.fullSize else 1),
            on_press=lambda inst: self.on_press(self), halign="left", valign="top", shorten=True,
            color=(1, 1, 1, 1) if shouldUseWhiteText(Globals.PrimaryColor) else (0, 0, 0, 1),
            background_normal="CalendarInactive.png", background_down="CalendarInactive.png")
        self.titleLabel.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        self.descriptionLabel = Button(text=self.description, size_hint_y=.25, on_press=lambda inst: self.on_press(self),
            color=(1, 1, 1, 1) if shouldUseWhiteText(Globals.PrimaryColor) else (0, 0, 0, 1), halign="left", shorten=True,
            background_normal="CalendarInactive.png", background_down="CalendarInactive.png", valign="bottom")
        self.descriptionLabel.bind(size=lambda inst, size: setattr(inst, "text_size", size))
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
        self.titleLabel.bind(background_color=lambda inst, color: setattr(self.titleLabel, "color",
            (1, 1, 1, 1) if shouldUseWhiteText(color) else (0, 0, 0, 1)))
        self.descriptionLabel.bind(background_color=lambda inst, color: setattr(self.descriptionLabel, "color",
            (1, 1, 1, 1) if shouldUseWhiteText(color) else (0, 0, 0, 1)))
        self.add_widget(self.titleLabel)
        if self.fullSize:
            self.add_widget(self.descriptionLabel)

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

    def asDict(self):
        event = {
            "summary": self.description,
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
        return event
