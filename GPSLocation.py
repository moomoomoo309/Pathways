from datetime import datetime
from kivy.properties import BoundedNumericProperty, ObjectProperty


class GPSLocation:
    longitude=BoundedNumericProperty(0,min=-180,max=180)
    latitude=BoundedNumericProperty(0,min=-90,max=90)
    altitude=BoundedNumericProperty(0,min=-6371,max=200) # The center of earth to 100 km outside of earth's atmosphere
    time=ObjectProperty(datetime.now(),baseclass=(datetime))
    def __init__(self):
        super(GPSLocation,self).__init__() # Reasons, reasons, reasons.
