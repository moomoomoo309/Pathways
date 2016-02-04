from datetime import datetime, timedelta
from functools import partial
from kivy.graphics.context_instructions import Color
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics.vertex_instructions import Rectangle
from kivy.uix.button import Button

from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty

class Event(Button):
    start = ObjectProperty(datetime.now(), baseclass=datetime)
    end = ObjectProperty(datetime.now() + timedelta(minutes=15), baseclass=datetime, allow_none=True)
    name = StringProperty("Unnamed Event")
    #    Location = ObjectProperty(baseclass=GPSLocation)
    # We will use this when we can do some better testing with GPSLocation.
    attachments = ListProperty([])
    allDay = BooleanProperty(False)
    def __init__(self, **kwargs):
        super(Event, self).__init__(**kwargs)  # Another line needed for reasons.
        self.dateChanged()
        if self.name!="":
            self.text=self.name
        if self.text!="":
            self.name=self.text
        # Propogate resize to children
        self.bind(color=lambda inst,color: setattr(self,"background_color", color))
        self.bind(name=lambda inst,name: setattr(self,"text",name))
        self.bind(text=lambda inst,text: setattr(self,"name",text))
        self.bind(start=partial(self.dateChanged))  # Partial drops the unneeded arguments
        self.bind(end=partial(self.dateChanged))


    def dateChanged(self):  # It only needs self.
        self.allDay = False
        if self.end is None:
            self.end = self.start + timedelta(days=1)
            self.allDay = True
        elif self.end < self.start:  # If end comes before start, fix it.
            self.end, self.start = self.start, self.end

    def isNow(self, time):
        return self.start < time < self.end
