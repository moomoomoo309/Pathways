from datetime import date
from functools import partial
from os.path import isfile
from random import randint

from kivy.animation import Animation, AnimationTransition
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics.vertex_instructions import Rectangle
from kivy.properties import AliasProperty
from kivy.properties import BooleanProperty, BoundedNumericProperty
from kivy.uix.button import Button, ButtonBehavior
from kivy.uix.carousel import Carousel
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.togglebutton import ToggleButton

from AsyncImageButton import AsyncImageButton

online = False
CurrentMonth = date.today().month - 1  # It's table indices (0-11), not month count (1-12)
Images = {10: ["http://images2.wikia.nocookie.net/__cb20120728022911/monsterhigh/images/1/1d/Skeletons.jpg",
               "https://images.duckduckgo.com/iu/?u=http%3A%2F%2Fimages.fineartamerica.com%2Fimages-medium-large-5%2Fdancing-skeletons-liam-liberty.jpg&f=1",
               "http://ih1.redbubble.net/image.24320851.9301/flat,550x550,075,f.jpg",
               "http://icons.iconseeker.com/png/fullsize/creeps/skeleton-1.png",
               "//hs4.hs.ptschools.org/data_student$/2016/My_Documents/1009877/Documents/My Pictures/simple_skeleton.png",
               "//hs4.hs.ptschools.org/data_student$/2016/My_Documents/1009877/Documents/My Pictures/RainbowPenguins.jpg"]}  # Replace these with pictures of your choice

topBarBackground = InstructionGroup()

# Remove any images which don't exist or are online if online is false
for i in Images:
    if isinstance(i, (int, long)):
        j = 0
        while j < Images[i].__len__():
            if not online:
                if not isfile(Images[i][j]):
                    Images[i].remove(Images[i][j])
                else:
                    j += 1
            else:
                if not (Images[i][j][0:4] == "http" or Images[i][j][0:3] == "ftp") and not isfile(Images[i][j]):
                    Images[i].remove(Images[i][j])
                else:
                    j += 1


# A normal asyncimage with an on_press function!
class AsyncImageButton(ButtonBehavior, AsyncImage):
    def on_press(self):
        self.source = getImageSource(self.source)


# The grid which contains the 30(ish) days for each month
class Calendar(GridLayout):
    randomImages = BooleanProperty(False)
    online = BooleanProperty(True)
    topBarSize = BoundedNumericProperty(0, min=0)

    def __init__(self, **kwargs):
        super(Calendar, self).__init__()  # I need this line for reasons.
        MonthLength = kwargs["MonthLength"]
        # The length of the current month
        MonthStart = kwargs["MonthStart"]
        # The day of the week the month starts on
        self.pos = kwargs["pos"]
        # Get the position of the widget
        self.cols = 7
        self.rows = 6
        if MonthLength + MonthStart < 36:
            self.rows = 5
        # The grid is 7x6 because 7x5 isn't enough for months which start on Saturday
        self.size = kwargs["size"]
        # Keep it within its bounds.
        self.spacing = 1
        # The size of each box in the grid
        for i in range(0, MonthStart):
            self.add_widget(AsyncImageButton(source=getImageSource(None), allow_stretch=True, keep_ratio=False,
                                             size=gridSize))  # If the month doesn't start on a Monday, you need empty days.

        for i in range(0, MonthLength):
            self.add_widget(ToggleButton(texture=None, background_normal="CalendarInactive.png",
                                         background_down="CalendarActive.png", group="CalendarGrid_Days",
                                         text="[color=000000][size=36]" + str(i + 1) + "[/color][/size]",
                                         markup=True, halign="right", valign="top", text_size=self.size))
            # The group means they act as radio buttons, so only one is toggleable at a time.
        for i in range(0, self.rows * self.cols - MonthLength - MonthStart):
            self.add_widget(
                AsyncImageButton(source=getImageSource(None), allow_stretch=True, keep_ratio=False, size=gridSize))
            # The empty images after the month in the calendar
