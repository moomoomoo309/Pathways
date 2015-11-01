from kivy.app import App
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button import Button, ButtonBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from random import randint
from datetime import date
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color
from os.path import isfile
from kivy.animation import Animation, AnimationTransition

from kivy.graphics.instructions import InstructionGroup
from kivy.graphics.vertex_instructions import Rectangle

topBarSize = 75
# The size of the top bar
tabSize = 50
# The size of the tabs vertically.
tabMargin = 2
# The space between the top bar and the tab bar.
numTabs = 4
# The number of tabs displayed at once
floatBarRatio = float(1) / 16
# How much of the tab bar should be taken up by the float bar
tabBarColor = (1, 0, 0)
# Color of the tab bar
floatBarColor = (.75, 0, 0, 1)
# Color of the thin bar below the tabs on the tab bar
currentTab = 3
# The tab currently selected
CalWidget = None
# The calendar widget object, so it can be referenced on resize.
FloatBar = None
# The float bar object
randomImages = True
# Use random images to fill the empty days of the calendar
online = False
# Get images from the internet
screenManager = ScreenManager(size=(Window.width, Window.height - topBarSize - tabMargin - tabSize))
# The screen manager object
screens = ["1 Day", "3 Day", "Week", "Month"]
# The name of all of the screens
screenList = []
# A list containing all of the screens
CurrentMonth = date.today().month - 1  # It's table indices (0-11), not month count (1-12)
# The current month
Images = {9: ["http://images2.wikia.nocookie.net/__cb20120728022911/monsterhigh/images/1/1d/Skeletons.jpg",
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

# Length of each month
Months = {"January": 31, "February": 28, "March": 31, "April": 30, "May": 31, "June": 30, "July": 31, "August": 31,
          "September": 31, "October": 31, "November": 30, "December": 31}
# Name of each month
MonthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
              "November", "December"]


# Changes the image on the empty days on press
def getImageSource(blockedImage):
    if randomImages and CurrentMonth in Images is not None and Images[CurrentMonth].__len__() > 0:
        img = Images[CurrentMonth][randint(0, Images[CurrentMonth].__len__() - 1)]
        if Images[CurrentMonth].__len__() > 1 and blockedImage is not None:
            while img == blockedImage:
                img = Images[CurrentMonth][randint(0, Images[CurrentMonth].__len__() - 1)]
        elif Images[CurrentMonth].__len__() <= 1:
            return img

        if isfile(img) or img[0:4] == "http" or img[0:3] == "ftp":
            return img

    return "CalendarInactive.png"


# A normal asyncimage with an on_press function!
class AsyncImageButton(ButtonBehavior, AsyncImage):
    def on_press(self):
        self.source = getImageSource(self.source)


# The grid which contains the 30(ish) days for each month
class CalendarGrid(GridLayout):
    def __init__(self, **kwargs):
        super(CalendarGrid, self).__init__()  # I need this line for reasons.
        MonthLength = kwargs["MonthLength"]
        # The length of the current month
        MonthStart = kwargs["MonthStart"]
        # The day of the week the month starts on
        self.pos = kwargs["pos"]
        # Get the position of the widget
        self.cols = 7
        self.rows = 6
        if int(MonthLength) + int(MonthStart) < 36:
            self.rows = 5
        # The grid is 7x6 because 7x5 isn't enough for months which start on Saturday
        self.size = kwargs["size"]
        # Keep it within its bounds.
        self.spacing = 1
        gridSize = (float(Window.width) / 7, float(Window.height - topBarSize) / 6)
        # The size of each box in the grid
        for i in range(0, MonthStart):
            self.add_widget(AsyncImageButton(source=getImageSource(None), allow_stretch=True, keep_ratio=False,
                                             size=gridSize))  # If the month doesn't start on a Monday, you need empty days.

        for i in range(0, MonthLength):
            self.add_widget(ToggleButton(texture=None, background_normal="CalendarInactive.png",
                                         background_down="CalendarActive.png", group="CalendarGrid_Days",
                                         text="[color=000000][size=36]" + str(i + 1) + "[/color][/size]",
                                         pos=(0, Window.height - topBarSize), markup=True, halign="right",
                                         valign="top", text_size=gridSize))
            # The group means they act as radio buttons, so only one is toggleable at a time.
        for i in range(0, self.rows * self.cols - MonthLength - MonthStart):
            self.add_widget(
                AsyncImageButton(source=getImageSource(None), allow_stretch=True, keep_ratio=False, size=gridSize))
            # The empty images after the month in the calendar


# Redraw the whole thing on resize
def redraw(*args):
    layout = CalWidget.parent.parent.parent
    layout.size = (Window.width, Window.height)
    topBarBackground.clear()
    drawTopBarBackground()
    for i in layout.children:  #Reset the size of the all the widgets that make up the top bar
        if i == FloatBar:
            i.size = [Window.width / numTabs, tabSize * floatBarRatio]
            i.pos = [currentTab * Window.width / numTabs, Window.height - topBarSize - tabSize - tabMargin]
        elif isinstance(i, Button):
            i.pos = (getTabButtonPos(i.i))
            i.size = (getTabButtonSize())
        elif isinstance(i, Label):
            i.pos = (-1, Window.height - topBarSize)
            i.size = (Window.width, topBarSize)
        elif isinstance(i, ScreenManager):
            i.pos = (0, 0)
            i.size = (Window.width, Window.height - topBarSize - tabSize - tabMargin)
    CalParent = CalWidget.parent
    CalParent.remove_widget(CalWidget)
    global CalWidget
    CalWidget = makeCalWidget()
    CalParent.add_widget(CalWidget)


# Used to figure out whether a tab is to the left or right of the current one.
def getScreenIndex(name):
    for i in range(0, screens.__len__()):
        if name == screens[i]:
            return i


# Switches the screen to the one pressed by the button without transition
def switchCalScreen(*args):
    global currentTab
    for i in screenList:
        if args[0].text[
           len("[color=ffffff][size=24]"):-len("[/size][/color]")] == i.name and i.name != screenManager.current:
            if getScreenIndex(i.name) > getScreenIndex(screenManager.current):
                screenManager.transition.direction = "left"
            else:
                screenManager.transition.direction = "right"
            animateFloatBar(getScreenIndex(i.name))
            # Animate the floatbar
            screenManager.current = i.name
            # Animates the whole screen except the bar on top


def animateFloatBar(tab):
    global currentTab
    currentTab = tab
    Animation(x=Window.width / numTabs * currentTab, y=FloatBar.pos[1], duration=.25,
              transition=AnimationTransition.out_sine).start(FloatBar)
    # out_sine looks pretty good, I think.


def getTabButtonPos(i):
    return i * Window.width / numTabs, Window.height - topBarSize - tabMargin - tabSize * (1 - floatBarRatio)


def getTabButtonSize():
    return Window.width / numTabs, tabSize


def drawTopBarBackground():
    topBarBackground.add(Rectangle(source="CalendarInactive.png", pos=(0, Window.height - topBarSize),
                                   size=(Window.width, topBarSize)))  # Draw the top bar
    topBarBackground.add(Rectangle(pos=(0, Window.height - tabMargin), size=(Window.width, tabMargin)))
    topBarBackground.add(Color(*tabBarColor))
    topBarBackground.add(Rectangle(pos=(0, Window.height - topBarSize - tabSize - tabMargin),
                                   size=(Window.width, tabSize)))  # Draw the tabs bar
    topBarBackground.add(Color(1, 1, 1))

    # Draw the top bar


def drawGui(self, **kwargs):
    drawTopBarBackground()
    self.canvas.before.add(topBarBackground)
    # Add text for tabs
    for i in range(0, 4):
        btn = Button(text_size=getTabButtonSize(), size=getTabButtonSize(),
                     text="[color=ffffff][size=24]" + screens[i] + "[/size][/color]",
                     background_color=(1, 1, 1, 0), pos=getTabButtonPos(i),
                     markup=True, halign="center", valign="middle", on_press=switchCalScreen)
        btn.i = i
        self.add_widget(btn)

    self.add_widget(Label(text_size=(Window.width, topBarSize), size=(Window.width, topBarSize),
                          text="[color=000000][size=36]" + kwargs["Month"] + "[/color][/size]",
                          pos=(-1, Window.height - topBarSize), markup=True, halign="center",
                          valign="middle"))
    # It's got markup in it for color and size, and the text is centered vertically and horizontally.
    # The text is from the keyword argument "Month".
    global FloatBar
    FloatBar = Button(background_color=floatBarColor, background_normal="", background_down="",
                      size=(Window.width / numTabs, tabSize * floatBarRatio),
                      pos=(currentTab * Window.width / numTabs, Window.height - topBarSize - tabSize - tabMargin))

    print(FloatBar.size[1])
    self.add_widget(FloatBar)
    # Add the float bar


def makeCalWidget():
    return CalendarGrid(MonthLength=Months[MonthNames[CurrentMonth]], pos=(0, -tabMargin),
                        MonthStart=date.today().replace(day=1).weekday(),
                        size=(Window.width, Window.height - topBarSize - tabSize - tabMargin + 1))


class Calendar(App):
    def build(self):
        layout = GridLayout()
        # Put everything in a GridLayout
        drawGui(layout, Month=MonthNames[CurrentMonth])
        # Draw the top bar
        Window.bind(on_resize=redraw)
        # Redraw the whole thing on resize
        global CalWidget
        CalWidget = makeCalWidget()
        # Use this for resizing
        MonthScreen = Screen(name=screens[3])
        MonthScreen.add_widget(CalWidget)
        screenManager.add_widget(MonthScreen)
        screenList.append(MonthScreen)
        for i in range(2, -1, -1):
            testScreen = Screen(name=screens[i])
            testScreen.add_widget(Label(text="This is a test!"))
            # You need a second screen for testing!
            screenList.append(testScreen)
            screenManager.add_widget(testScreen)
        layout.add_widget(screenManager)
        return layout


if __name__ == "__main__":
    Calendar().run()
