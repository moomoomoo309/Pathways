from datetime import datetime
from kivy.properties import BoundedNumericProperty, ObjectProperty
from plyer import gps
from functools import partial


class GPSLocation: # Temp, will be replaced with the implementation of a better GPS lib
    longitude=BoundedNumericProperty(0,min=-180,max=180)
    latitude=BoundedNumericProperty(0,min=-90,max=90)
    altitude=BoundedNumericProperty(0,min=-6371,max=200) # The center of earth to 100 km outside of earth's atmosphere
    bearing=BoundedNumericProperty(0,min=0,max=360)
    speed=BoundedNumericProperty(0,min=0)
    def __init__(self):
        super(GPSLocation,self).__init__() # Reasons, reasons, reasons.
        gps.configure(on_location=partial(callback,fct="on_location:"),on_status=partial(callback,fct="on_status:"))
        gps.start()
        print(kwargs)

def callback(fct,*args,**kwargs):
    print(fct)
    print"args={}".format(args)
    print"kwargs={}".format(kwargs)

class GPSRun(App):
    def build(self):
        loc=GPSLocation()
        print(loc.speed)

