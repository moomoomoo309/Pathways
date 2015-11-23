from datetime import datetime
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from GPSLocation import GPSLocation

class Event:
    start = ObjectProperty(datetime.today(),baseclass=datetime)
    end = ObjectProperty(baseclass=datetime,allow_none=True)
    description = StringProperty("")
    name = StringProperty("Unnamed Event")
    Location = ObjectProperty(baseclass=GPSLocation)
    attachments = ListProperty([])

    def __init__(self):
        super(Event, self).__init__() # Another line needed for reasons.
        self.dateChanged()
        self.bind(start=self.dateChanged)
        self.bind(end=self.dateChanged)

    def dateChanged(self,*args): # It only needs self.
        self.allDay=False
        if self.end is None:
            self.end=self.start
            self.allDay=True
        elif self.end<self.start: # If end comes before start, fix it.
            self.end,self.start=self.start,self.end
