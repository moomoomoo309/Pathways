from datetime import datetime, timedelta
from functools import partial

from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty


class Event:
    start = ObjectProperty(datetime.now(), baseclass=datetime)
    end = ObjectProperty(baseclass=datetime, allow_none=True)
    description = StringProperty("")
    name = StringProperty("Unnamed Event")
    #    Location = ObjectProperty(baseclass=GPSLocation)
    # We will use this when we can do some better testing with GPSLocation.
    attachments = ListProperty([])
    allDay = BooleanProperty(False)

    def __init__(self):
        super(Event, self).__init__()  # Another line needed for reasons.
        self.dateChanged()
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
