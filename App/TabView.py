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
from kivy.uix.button import Button, ButtonBehavior
from kivy.uix.carousel import Carousel
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.togglebutton import ToggleButton

from Calendar import Calendar

topBarSize = 75
# The size of the top bar
tabSize = 50
# The size of the tabs vertically.
tabMargin = 2
# The space between the top bar and the tab bar.
numTabs = 4
# The number of tabs displayed at once
floatBarRatio = float(1) / 8
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
online = True
# Get images from the internet
screenManager = ScreenManager()
# The screen manager object
carousel = None
# The carousel object
screens = ["1 Day", "3 Day", "Week", "Month"]
# The name of all of the screens
screenList = []
# A list containing all of the screens
CurrentMonth = date.today().month - 1  # It's table indices (0-11), not month count (1-12)
# The current month
overrideTab = None
# Forces the tab to be used to be this one.
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


# Redraw the whole thing on resize
def redraw(win, width, height):
    layout = CalWidget.parent.parent.parent.parent
    CalWidget.parent.parent.parent.size = (width, height - topBarSize - tabMargin - tabSize)
    topBarBackground.clear()
    drawTopBarBackground()
    for i in layout.children:  # Reset the size of the all the widgets that make up the top bar
        if i == FloatBar:
            i.size = [Window.width / numTabs, tabSize * floatBarRatio]
            i.pos = [currentTab * Window.width / numTabs, Window.height - topBarSize - tabSize - tabMargin]
        elif isinstance(i, Button):
            i.pos = (getTabButtonPos(i.i, width, height))
            i.size = (getTabButtonSize(width))
        elif isinstance(i, Label):
            i.pos = (-1, height - topBarSize)
            i.size = (width, topBarSize)
        elif isinstance(i, ScreenManager):
            i.pos = (0, 0)
            i.size = (width, height - topBarSize - tabSize - tabMargin)
    CalParent = CalWidget.parent
    CalParent.remove_widget(CalWidget)
    global CalWidget
    CalWidget = makeCalWidget()
    CalParent.add_widget(CalWidget)


# Switches the screen to the one pressed by the button without transition
def switchCalScreen(*args):
    global overrideTab
    for i in screenList:
        if args[0].text[
           len("[color=ffffff][size=24]"):-len("[/size][/color]")] == i.name and i.name != carousel.current_slide.name:
            overrideTab = screens.index(i.name)
            # Animate the floatbar
            carousel.load_slide(i)
            # Animates the whole screen except the bar on top


def animateFloatBar(tab, dur):
    global currentTab
    currentTab = tab
    Animation().stop_all(FloatBar)
    Animation(x=Window.width / numTabs * currentTab, y=FloatBar.pos[1], duration=dur if dur else .25,
              transition=AnimationTransition.out_sine).start(FloatBar)
    # out_sine looks pretty good, I think.


def getTabButtonPos(i, width, height):
    return i * width / numTabs, height - topBarSize - tabMargin - tabSize * (1 - floatBarRatio)


def getTabButtonSize(width):
    return width / numTabs, tabSize


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
        btn = Button(text_size=getTabButtonSize(Window.width), size=getTabButtonSize(Window.width),
                     text="[color=ffffff][size=24]" + screens[i] + "[/size][/color]",
                     background_color=(1, 1, 1, 0), pos=getTabButtonPos(i, Window.width, Window.height),
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
    FloatBar = AsyncImage(source="FloatBar.png", size=(Window.width / numTabs, tabSize * floatBarRatio),
                          pos=(currentTab * Window.width / numTabs, Window.height - topBarSize - tabSize - tabMargin),
                          allow_stretch=True, keep_ratio=False)

    self.add_widget(FloatBar)
    # Add the float bar


def makeCalWidget():
    return Calendar(MonthLength=Months[MonthNames[CurrentMonth]], pos=(0, -tabMargin),
                    MonthStart=(date.today().replace(day=1).weekday() + 1) % 7,
                    size=(Window.width, Window.height - topBarSize - tabSize - tabMargin + 1),
                    online=True, randomImages=True)
    # The monthwidget did nothing, so it's gone!


class TabView(App):
    def build(self):
        global carousel
        carousel = FloatCarousel(size=(Window.width, Window.height - topBarSize - tabMargin - tabSize),
                                 direction="left", min_move=.1)
        layout = GridLayout()
        # Put everything in a GridLayout
        drawGui(layout, Month=MonthNames[CurrentMonth])
        # Draw the top bar
        Window.bind(on_resize=redraw)
        # Redraw the whole thing on resize
        global CalWidget
        CalWidget = makeCalWidget()
        # Use this for resizing
        layout2 = GridLayout()
        MonthScreen = Screen(name=screens[3])
        MonthScreen.add_widget(CalWidget)
        MonthScreen.add_widget(layout2)
        carousel.add_widget(MonthScreen)
        screenList.append(MonthScreen)
        for i in range(2, -1, -1):
            testScreen = Screen(name=screens[i])
            testScreen.add_widget(AsyncImage(source=getImageSource(None), allow_stretch=True, keep_ratio=False))
            # You need a second screen for testing!
            screenList.append(testScreen)
            carousel.add_widget(testScreen)
        layout.add_widget(screenManager)
        layout.add_widget(carousel)
        return layout


class FloatCarousel(Carousel):
    def _prev_slide(self):
        slides = self.slides
        len_slides = len(slides)
        index = self.index
        if len_slides < 2:  # None, or 1 slide
            return None
        if len_slides == 2:
            if index == 0:
                return None
            if index == 1:
                return slides[0]
        if self.loop and index == 0:
            return slides[-1]
        if index > 0:
            return slides[index - 1]

    previous_slide = AliasProperty(_prev_slide, None, bind=('slides', 'index'))

    def _next_slide(self):
        if len(self.slides) < 2:  # None, or 1 slide
            return None
        if len(self.slides) == 2:
            if self.index == 0:
                return self.slides[1]
            if self.index == 1:
                return None
        if self.loop and self.index == len(self.slides) - 1:
            return self.slides[0]
        if self.index < len(self.slides) - 1:
            return self.slides[self.index + 1]

    next_slide = AliasProperty(_next_slide, None, bind=('slides', 'index'))

    def on_touch_move(self, touch):
        if self._get_uid('cavoid') in touch.ud:
            return
        if self._touch is not touch:
            super(FloatCarousel, self).on_touch_move(touch)
            return self._get_uid() in touch.ud
        if touch.grab_current is not self:
            return True
        ud = touch.ud[self._get_uid()]
        direction = self.direction
        if ud['mode'] == 'unknown':
            if direction[0] in ('r', 'l'):
                distance = abs(touch.ox - touch.x)
            else:
                distance = abs(touch.oy - touch.y)
            if distance > self.scroll_distance:
                Clock.unschedule(self._change_touch_mode)
                ud['mode'] = 'scroll'
        else:
            if direction[0] in ('r', 'l'):
                self._offset += touch.dx
                FloatBar.x -= touch.dx / numTabs  # Changed line!
            if direction[0] in ('t', 'b'):
                self._offset += touch.dy
                FloatBar.y -= touch.dy / numTabs  # Changed line!
        return True

    def _start_animation(self, *args, **kwargs):
        # compute target offset for ease back, next or prev
        new_offset = 0
        direction = kwargs.get('direction', self.direction)
        is_horizontal = direction[0] in ['r', 'l']
        extent = self.width if is_horizontal else self.height
        min_move = kwargs.get('min_move', self.min_move)
        _offset = kwargs.get('offset', self._offset)

        if _offset < min_move * -extent:
            new_offset = -extent
        elif _offset > min_move * extent:
            new_offset = extent

        # if new_offset is 0, it wasnt enough to go next/prev
        dur = self.anim_move_duration
        if new_offset == 0:
            dur = self.anim_cancel_duration

        # detect edge cases if not looping
        len_slides = len(self.slides)
        index = self.index
        if not self.loop or len_slides == 1:
            is_first = (index == 0)
            is_last = (index == len_slides - 1)
            if direction[0] in ['r', 't']:
                towards_prev = (new_offset > 0)
                towards_next = (new_offset < 0)
            else:
                towards_prev = (new_offset < 0)
                towards_next = (new_offset > 0)
            if (is_first and towards_prev) or (is_last and towards_next):
                new_offset = 0

        anim = Animation(_offset=new_offset, d=dur, t=self.anim_type)
        anim.cancel_all(self)

        def _cmp(*l):
            if self._skip_slide is not None:
                self.index = self._skip_slide
                self._skip_slide = None

        anim.bind(on_complete=_cmp)
        anim.start(self)
        # Changed lines come after here.
        global currentTab, overrideTab
        if overrideTab is None:
            if new_offset > 0:
                currentTab = screens.index(self.next_slide.name) if self.next_slide is not None else currentTab
            elif new_offset < 0:
                currentTab = screens.index(self.previous_slide.name) if self.previous_slide is not None else currentTab
        else:
            currentTab = overrideTab
            overrideTab = None
        animateFloatBar(currentTab, dur)


if __name__ == "__main__":
    TabView().run()
