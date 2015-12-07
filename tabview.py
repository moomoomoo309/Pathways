import calendar
from datetime import date, datetime
from os.path import isfile
from random import randint

from kivy.animation import Animation, AnimationTransition
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics.vertex_instructions import Rectangle
from kivy.properties import AliasProperty, BoundedNumericProperty, ListProperty, BooleanProperty, DictProperty, partial
from kivy.uix.button import Button
from kivy.uix.carousel import Carousel
from kivy.uix.dropdown import DropDown
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.uix.settings import Settings

from Calendar import Calendar30Days
from DatePicker import DatePickerWidget, getMonthLength, getStartDay

# Name of each month

MonthNames = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
              "November", "December")


class TabView(Widget):
    Images = DictProperty(
        {10: ["http://images2.wikia.nocookie.net/__cb20120728022911/monsterhigh/images/1/1d/Skeletons.jpg",
              "https://images.duckduckgo.com/iu/?u=http%3A%2F%2Fimages.fineartamerica.com%2Fimages-medium-large-5%2Fdancing-skeletons-liam-liberty.jpg&f=1",
              "http://ih1.redbubble.net/image.24320851.9301/flat,550x550,075,f.jpg",
              "http://icons.iconseeker.com/png/fullsize/creeps/skeleton-1.png",
              "//hs4.hs.ptschools.org/data_student$/2016/My_Documents/1009877/Documents/My Pictures/simple_skeleton.png",
              "//hs4.hs.ptschools.org/data_student$/2016/My_Documents/1009877/Documents/My Pictures/RainbowPenguins.jpg"]})
    # Replace these with pictures of your choice.

    screenNames = ListProperty(["Schedule", "1 Day", "3 Day", "Week", "Month"])
    # The name of all of the screens
    randomImages = BooleanProperty(False)
    # Use random images to fill the empty days of the calendar
    online = BooleanProperty(True)
    # Get images from the internet
    topBarSize = BoundedNumericProperty(75, min=0)
    # The size of the top bar
    tabSize = BoundedNumericProperty(50, min=0)
    # The size of the tabs vertically.
    tabMargin = BoundedNumericProperty(2, min=0)
    # The space between the top bar and the tab bar.
    numTabs = BoundedNumericProperty(5, min=1)
    # The number of tabs displayed at once
    floatBarRatio = BoundedNumericProperty(float(1) / 8, min=0, max=1)
    # How much of the tab bar should be taken up by the float bar
    tabBarColor = ListProperty([1, 0, 0])
    # Color of the tab bar
    floatBarColor = ListProperty([.75, 0, 0, 1])
    # Color of the thin bar below the tabs on the tab bar
    currentTab = BoundedNumericProperty(4, min=0)

    # The tab currently selected

    def __init__(self, **kwargs):
        super(TabView, self).__init__()  # I need this line for reasons.
        # Set the properties above
        self.screenNames = kwargs["screenNames"] if "screenNames" in kwargs else self.screenNames
        self.randomImages = kwargs["randomImages"] if "randomImages" in kwargs else self.randomImages
        self.online = kwargs["online"] if "online" in kwargs else self.online
        self.topBarSize = kwargs["topBarSize"] if "topBarSize" in kwargs else self.topBarSize
        self.tabSize = kwargs["tabSize"] if "tabSize" in kwargs else self.tabSize
        self.tabMargin = kwargs["tabMargin"] if "tabMargin" in kwargs else self.tabMargin
        self.numTabs = kwargs["numTabs"] if "numTabs" in kwargs else self.numTabs
        self.floatBarRatio = kwargs["floatBarRatio"] if "floatBarRatio" in kwargs else self.floatBarRatio
        self.tabBarColor = kwargs["tabBarColor"] if "tabBarColor" in kwargs else self.tabBarColor
        self.floatBarColor = kwargs["floatBarColor"] if "floatBarColor" in kwargs else self.floatBarColor
        self.currentTab = kwargs["currentTab"] if "currentTab" in kwargs else self.currentTab

        self.screenList = []
        # A list of the screens in the carousel.

        # Remove any images which don't exist or are online if online is false
        self.FloatBar = None
        # The float bar object
        self.carousel = None
        # The carousel object
        self.screenList = []
        # A list containing all of the screens
        self.CurrentMonth = date.today().month - 1  # It's table indices (0-11), not month count (1-12)
        # The current month
        self.overrideTab = None
        # Forces the tab to be used to be this one.
        self.size = kwargs["size"] if "size" in kwargs else (100, 100)
        self.pos = kwargs["pos"] if "pos" in kwargs else (0, 0)
        # Draw black background
        for i in self.Images:
            if isinstance(i, (int, long)):
                j = 0
                while j < self.Images[i].__len__():
                    if not self.online:
                        if not isfile(self.Images[i][j]):
                            self.Images[i].remove(self.Images[i][j])
                        else:
                            j += 1
                    else:
                        if not (self.Images[i][j][0:4] == "http" or self.Images[i][j][0:3] == "ftp") and not isfile(
                                self.Images[i][j]):
                            self.Images[i].remove(self.Images[i][j])
                        else:
                            j += 1
        self.carousel = FloatCarousel(
            size=(self.size[0], self.size[1] - self.topBarSize - self.tabMargin - self.tabSize),
            direction="left", min_move=.05, screenNames=self.screenNames)
        # Put everything in a GridLayout
        self.topBarBackground = InstructionGroup()
        self._drawGui(Month=str(MonthNames[self.CurrentMonth])+" "+str(date.today().year))
        # Draw the top bar
        for i in range(self.numTabs - 1, -1, -1):
            testScreen = Screen(name=self.screenNames[i],
                                size=(Window.width, Window.height - self.topBarSize - self.tabSize - self.tabMargin))
            testScreen.add_widget(Label(text="Add a widget here with the add_screen method!"))
            testScreen.isDefault = True
            # You need a second screen for testing!
            self.screenList.append(testScreen)
            self.carousel.add_widget(testScreen)
        self.add_widget(self.carousel)
        self.bind(size=self.resize)  # Resize children too!
        for i in self.children:
            if isinstance(i, Button) and hasattr(i, "i") and i.i == self.currentTab:
                self._switchCalScreen(i)

    # Redraw the whole thing on resize
    def resize(self, width, height):
        self.topBarBackground.clear()
        self._drawTopBarBackground()
        for i in self.children:  # Reset the size of the all the widgets that make up the top bar
            if i == self.FloatBar:
                i.size = [self.size[0] / self.numTabs, self.tabSize * self.floatBarRatio]
                i.pos = [self.currentTab * self.size[0] / self.numTabs,
                         self.size[1] - self.topBarSize - self.tabSize - self.tabMargin]
            elif i == self.MonthButton:
                i.pos = (-1, self.size[1] - self.topBarSize)
                i.size = (self.size[0], self.topBarSize)
            elif hasattr(self, "datePicker") and i == self.datePicker:
                rows = 6 if getStartDay(i.children[0].date.month, i.children[0].date.year) % 7 + getMonthLength(
                    i.children[0].date.month,
                    i.children[0].date.year) < 35 else 7
                i.size = (min(Window.width, Window.height), min(Window.width, Window.height) * 2 / 3 *
                                   (rows + 1) / rows)
                i.pos = (Window.width / 2 - min(Window.width, Window.height) / 2,
                      Window.height - min(Window.width, Window.height) * 2 / 3 * (
                      rows + 1) / rows)
            elif isinstance(i, Button):
                i.pos = (self._getTabButtonPos(i.i))
                i.size = (self._getTabButtonSize())
            elif isinstance(i, FloatCarousel):
                i.pos = (0, 0)
                i.size = (self.size[0], self.size[1] - self.topBarSize - self.tabMargin - self.tabSize)

    # Adds a widget to the tabview (Don't use add_widget!)
    def add_screen(self, widget, index=0):  # Index is from right to left, not left to right!
        if self.screenList[index].isDefault:
            self.screenList[index].clear_widgets()
            self.screenList[index].isDefault = False
        widget.size = self.screenList[index].size
        self.screenList[index].add_widget(widget)

    # Switches the screen to the one pressed by the button
    def _switchCalScreen(self, *args):
        for i in self.screenList:
            if args[0].text[
               len("[color=ffffff][size=24]"):-len(
                   "[/size][/color]")] == i.name and i.name != self.carousel.current_slide.name:
                self.overrideTab = self.screenNames.index(i.name)
                # Animate the floatbar
                self.carousel.load_slide(i)
                # Animates the whole screen except the bar on top

    def _animateFloatBar(self, tab, dur):
        self.currentTab = tab
        Animation().stop_all(self.FloatBar)
        Animation(x=self.size[0] / self.numTabs * self.currentTab, y=self.FloatBar.pos[1], duration=dur if dur else .25,
                  transition=AnimationTransition.out_sine).start(self.FloatBar)
        # out_sine looks pretty good, I think.

    def _getTabButtonPos(self, i):
        return i * self.size[0] / self.numTabs, self.height - self.topBarSize - self.tabMargin - self.tabSize * (
            1 - self.floatBarRatio)

    def _getTabButtonSize(self):
        return self.size[0] / self.numTabs, self.tabSize

    def _drawTopBarBackground(self):  # Draws the boxes behind the buttons and label
        self.topBarBackground.add(Color(0, 0, 0))
        self.topBarBackground.add(Rectangle(pos=self.pos, size=self.size))
        self.topBarBackground.add(Rectangle(source="CalendarInactive.png", pos=(0, self.size[1] - self.topBarSize),
                                            size=(self.size[0], self.topBarSize)))  # Draw the top bar
        self.topBarBackground.add(Color(*self.tabBarColor))
        self.topBarBackground.add(Rectangle(pos=(0, self.size[1] - self.topBarSize - self.tabSize - self.tabMargin),
                                            size=(self.size[0], self.tabSize)))  # Draw the tabs bar
        self.topBarBackground.add(Color(0, 0, 0))

        # Draw the top bar

    def _drawGui(self, Month):  # Draws the tab view (besides the boxes behind the buttons and label)
        self._drawTopBarBackground()
        self.canvas.add(self.topBarBackground)
        # Draw top bar
        # Add text for tabs
        for i in range(0, self.numTabs):
            btn = Button(text_size=self._getTabButtonSize(), size=self._getTabButtonSize(),
                         text="[color=ffffff][size=24]" + self.screenNames[i] + "[/size][/color]",
                         background_color=(1, 1, 1, 0), pos=self._getTabButtonPos(i),
                         markup=True, halign="center", valign="middle", on_press=self._switchCalScreen)
            btn.i = i
            self.add_widget(btn)
        self.dropDown = DropDown()

        self.MonthButton = Button(text_size=(self.size[0], self.topBarSize), size=(self.size[0], self.topBarSize),
                                  text="[color=000000][size=36]" + Month + "[/color][/size]",
                                  pos=(-1, self.size[1] - self.topBarSize), markup=True, halign="center",
                                  valign="middle", on_press=showDate, background_color=(1,0,1,1),
                                  background_normal="CalendarInactive.png", background_down="CalendarInactive.png")

        self.add_widget(self.MonthButton)

        # It's got markup in it for color and size, and the text is centered vertically and horizontally.
        # The text is from the keyword argument "Month".
        self.FloatBar = AsyncImage(source="FloatBar.png",
                                   size=(self.size[0] / self.numTabs, self.tabSize * self.floatBarRatio),
                                   pos=(self.currentTab * self.size[0] / self.numTabs,
                                        self.size[1] - self.topBarSize - self.tabSize - self.tabMargin),
                                   allow_stretch=True, keep_ratio=False)

        self.add_widget(self.FloatBar)
        # Add the float bar

    def _getImageSource(self, blockedImage):  # Changes the images on the empty days on click
        if self.randomImages and self.CurrentMonth in self.Images is not None and self.Images[
            self.CurrentMonth].__len__() > 0:
            img = self.Images[self.CurrentMonth][randint(0, self.Images[self.CurrentMonth].__len__() - 1)]
            if self.Images[self.CurrentMonth].__len__() > 1 and blockedImage is not None:
                while img == blockedImage:
                    img = self.Images[self.CurrentMonth][randint(0, self.Images[self.CurrentMonth].__len__() - 1)]
            elif self.Images[self.CurrentMonth].__len__() <= 1:
                return img
            if isfile(img) or img[0:4] == "http" or img[0:3] == "ftp":
                return img
        return "CalendarInactive.png"

    def changeDate(self, date):
        self.remove_widget(self.datePicker)
        # TODO: Actually change the date here


def showDate(self):
    parent = self.parent
    if hasattr(parent, "datePicker"):
        parent.remove_widget(parent.datePicker)
    rows = 6 if getStartDay(date.today().month, date.today().year) % 7 + getMonthLength(date.today().month,
                                                                                        date.today().year) < 35 else 7

    parent.datePicker = DatePickerWidget(size=(min(Window.width, Window.height), parent.topBarSize * (rows+1)),
                                         pos=(Window.width / 2 - min(Window.width, Window.height) / 2,
                                              Window.height - parent.topBarSize * (rows+1)))

    parent.datePicker.dismiss = partial(parent.changeDate, date=parent.datePicker.child.SelectedDate)
    parent.add_widget(parent.datePicker)


class FloatCarousel(Carousel):  # Slightly modified kivy carousel, to integrate with the floatbar.
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

    def on_touch_move(self, touch):  # All lines except the two specified are unchanged.
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
                self.parent.FloatBar.x -= touch.dx / self.parent.numTabs  # Changed line!
            if direction[0] in ('t', 'b'):
                self._offset += touch.dy
                self.parent.FloatBar.y -= touch.dy / self.parent.numTabs  # Changed line!
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
        if self.parent.overrideTab is None:  # If the tabs didn't trigger the move
            if new_offset > 0:  # Let the carousel do its thing!
                self.parent.currentTab = self.parent.screenNames.index(
                    self.next_slide.name) if self.next_slide is not None else self.parent.currentTab
            elif new_offset < 0:
                self.parent.currentTab = self.parent.screenNames.index(
                    self.previous_slide.name) if self.previous_slide is not None else self.parent.currentTab
                # If new_offset is 0, the slide has not changed.
        else:
            self.parent.currentTab = self.parent.overrideTab
            self.parent.overrideTab = None
        self.parent._animateFloatBar(self.parent.currentTab, dur)
        # Yeah, this is accessing a protected member of a parent class. It's supposed to.


def genericResize(*args, **kwargs):  # Resizes the whole tabview (which runs its resize method)
    if isinstance(kwargs["objs"], (list, tuple)):
        for i in kwargs["objs"]:
            if isinstance(kwargs["fct"], (list, tuple)):
                i.size = kwargs["fct"][kwargs["objs"].index(i)]()
            else:
                i.size = kwargs["fct"]()
    else:
        kwargs["objs"].size = kwargs["fct"]()

def makeCalWidget(self):  # Initializes the Calendar grid
    return Calendar30Days(MonthLength=calendar.monthrange(datetime.now().year, datetime.now().month)[1], pos=(0, 0),
                          MonthStart=(date.today().replace(day=1).weekday() + 1) % 7,
                          size=(Window.width, Window.height - self.topBarSize - self.tabSize - self.tabMargin),
                          online=self.online, randomImages=self.randomImages, getImageSource=self._getImageSource)


class tabview(App):
    def build(self):
        app = TabView(size=(Window.width, Window.height), randomImages=True, online=False)
        Window.bind(on_resize=partial(genericResize, objs=app, fct=lambda: Window.size))
        app.add_screen(makeCalWidget(app))
        return app


if __name__ == "__main__":
    tabview().run()
