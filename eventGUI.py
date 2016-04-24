from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from Event import Event
from dropDown import dropDown


class eventGUI(Popup):
    def __init__(self,**kwargs):
        super(eventGUI,self).__init__(**kwargs)
        self.event=None
        self.title="Create an event"
        self.outerLayout=BoxLayout(orientation="vertical")
        self.nameDialog=inputLine(text="Name")
        self.descriptionDialog=inputLine(text="Description")
        self.locationDialog=inputLine(text="location")
#        self.repeatDialog=inputLine(text="repeat")
        self.remindersDialog=dropDown()
        for i in [self.nameDialog,self.descriptionDialog,self.locationDialog,self.repeatDialog,self.remindersDialog]:
            self.outerLayout.add_widget(i)
        self.add_widget(self.outerLayout)

    def on_dismiss(self):
        self.event=Event(start=self.start,startTimezone=self.startTimezone,end=self.end,endTimezone=self.endTimezone,
            name=self.name,description=self.description,location=self.location,repeat=self.repeat,
            reminders=self.reminders,allDay=self.allDay)



class inputLine(BoxLayout):
    def __init__(self, **kwargs):
        super(inputLine,self).__init__(**kwargs)
        self.orientation="horizontal"
        self.add_widget(Label(text=self.text))
        self.add_widget(TextInput())


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