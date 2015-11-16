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
from kivy.properties import AliasProperty, BoundedNumericProperty, ListProperty, BooleanProperty, DictProperty, partial, \
    ObjectProperty
from kivy.uix.button import Button
from kivy.uix.carousel import Carousel
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from Calendar import Calendar30Days

# Length of each month
Months = {"January": 31, "February": 28, "March": 31, "April": 30, "May": 31, "June": 30, "July": 31, "August": 31,
          "September": 31, "October": 31, "November": 30, "December": 31}
# Name of each month
MonthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
              "November", "December"]


class TabView(Widget):
    Images = DictProperty(
        {10: ["http://images2.wikia.nocookie.net/__cb20120728022911/monsterhigh/images/1/1d/Skeletons.jpg",
              "https://images.duckduckgo.com/iu/?u=http%3A%2F%2Fimages.fineartamerica.com%2Fimages-medium-large-5%2Fdancing-skeletons-liam-liberty.jpg&f=1",
              "http://ih1.redbubble.net/image.24320851.9301/flat,550x550,075,f.jpg",
              "http://icons.iconseeker.com/png/fullsize/creeps/skeleton-1.png",
              "//hs4.hs.ptschools.org/data_student$/2016/My_Documents/1009877/Documents/My Pictures/simple_skeleton.png",
              "//hs4.hs.ptschools.org/data_student$/2016/My_Documents/1009877/Documents/My Pictures/RainbowPenguins.jpg"]})  # Replace these with pictures of your choice

    screenNames = ListProperty(["1 Day", "3 Day", "Week", "Month"])
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
    numTabs = BoundedNumericProperty(4, min=1)
    # The number of tabs displayed at once
    floatBarRatio = BoundedNumericProperty(float(1) / 8, min=0, max=1)
    # How much of the tab bar should be taken up by the float bar
    tabBarColor = ListProperty([1, 0, 0])
    # Color of the tab bar
    floatBarColor = ListProperty([.75, 0, 0, 1])
    # Color of the thin bar below the tabs on the tab bar
    currentTab = BoundedNumericProperty(3, min=0)
    # The tab currently selected
    screenList = ListProperty([])
    # A list of the screens in the carousel.
    CalWidget = ObjectProperty(None)
    # The calendar widget object, so it can be referenced on resize.

    def __init__(self, **kwargs):
        super(TabView, self).__init__()  # I need this line for reasons.
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
        self.MonthLength = calendar.monthrange(datetime.now().year, datetime.now().month)[1]
        self.carousel = FloatCarousel(
            size=(self.size[0], self.size[1] - self.topBarSize - self.tabMargin - self.tabSize),
            direction="left", min_move=.1, screenNames=self.screenNames)
        # Put everything in a GridLayout
        self.topBarBackground = InstructionGroup()
        self._drawGui(Month=MonthNames[self.CurrentMonth])
        # Draw the top bar
        self.CalWidget = self.CalWidget if self.CalWidget is not None else self._makeCalWidget()
        # Use this for resizing
        MonthScreen = Screen(name=self.screenNames[3])
        MonthScreen.add_widget(self.CalWidget)
        self.carousel.add_widget(MonthScreen)
        self.screenList.append(MonthScreen)
        for i in range(2, -1, -1):
            testScreen = Screen(name=self.screenNames[i])
            testScreen.add_widget(Label(text="Test"))
            # You need a second screen for testing!
            self.screenList.append(testScreen)
            self.carousel.add_widget(testScreen)
        self.add_widget(self.carousel)

    # Redraw the whole thing on resize
    def resize(self):
        self.topBarBackground.clear()
        self._drawTopBarBackground()
        for i in self.children:  # Reset the size of the all the widgets that make up the top bar
            if i == self.FloatBar:
                i.size = [self.size[0] / self.numTabs, self.tabSize * self.floatBarRatio]
                i.pos = [self.currentTab * self.size[0] / self.numTabs,
                         self.size[1] - self.topBarSize - self.tabSize - self.tabMargin]
            elif isinstance(i, Button):
                i.pos = (self._getTabButtonPos(i.i))
                i.size = (self._getTabButtonSize())
            elif isinstance(i, Label):
                i.pos = (-1, self.size[1] - self.topBarSize)
                i.size = (self.size[0], self.topBarSize)
            elif isinstance(i, FloatCarousel):
                i.pos = (0, 0)
                i.size = (self.size[0], self.size[1] - self.topBarSize - self.tabMargin - self.tabSize)
        CalParent = self.CalWidget.parent
        CalParent.remove_widget(self.CalWidget)
        self.CalWidget = self._makeCalWidget()
        CalParent.add_widget(self.CalWidget)

    def add_widget(self, widget, index=0):
        if isinstance(widget, Screen):
            if index == 0:
                self.screenList.append(widget)
            else:
                self.screenList.insert(widget, index)
        super(TabView, self).add_widget(widget, index)

    # Switches the screen to the one pressed by the button without transition
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

    def _drawTopBarBackground(self):
        self.topBarBackground.add(Rectangle(source="CalendarInactive.png", pos=(0, self.size[1] - self.topBarSize),
                                            size=(self.size[0], self.topBarSize)))  # Draw the top bar
        self.topBarBackground.add(Color(*self.tabBarColor))
        self.topBarBackground.add(Rectangle(pos=(0, self.size[1] - self.topBarSize - self.tabSize - self.tabMargin),
                                            size=(self.size[0], self.tabSize)))  # Draw the tabs bar
        self.topBarBackground.add(Color(1, 1, 1))

        # Draw the top bar

    def _drawGui(self, Month):
        self._drawTopBarBackground()
        self.canvas.before.add(self.topBarBackground)
        # Add text for tabs
        for i in range(0, 4):
            btn = Button(text_size=self._getTabButtonSize(), size=self._getTabButtonSize(),
                         text="[color=ffffff][size=24]" + self.screenNames[i] + "[/size][/color]",
                         background_color=(1, 1, 1, 0), pos=self._getTabButtonPos(i),
                         markup=True, halign="center", valign="middle", on_press=self._switchCalScreen)
            btn.i = i
            self.add_widget(btn)

        self.add_widget(Label(text_size=(self.size[0], self.topBarSize), size=(self.size[0], self.topBarSize),
                              text="[color=000000][size=36]" + Month + "[/color][/size]",
                              pos=(-1, self.size[1] - self.topBarSize), markup=True, halign="center",
                              valign="middle"))
        # It's got markup in it for color and size, and the text is centered vertically and horizontally.
        # The text is from the keyword argument "Month".
        self.FloatBar = AsyncImage(source="FloatBar.png",
                                   size=(self.size[0] / self.numTabs, self.tabSize * self.floatBarRatio),
                                   pos=(self.currentTab * self.size[0] / self.numTabs,
                                        self.size[1] - self.topBarSize - self.tabSize - self.tabMargin),
                                   allow_stretch=True, keep_ratio=False)

        self.add_widget(self.FloatBar)
        # Add the float bar

    def _makeCalWidget(self):
        return Calendar30Days(MonthLength=self.MonthLength, pos=(0, 0),
                              MonthStart=(date.today().replace(day=1).weekday() + 1) % 7,
                              size=(self.size[0], self.size[1] - self.topBarSize - self.tabSize - self.tabMargin),
                              online=self.online, randomImages=self.randomImages, getImageSource=self._getImageSource)
        # The monthwidget did nothing, so it's gone!

    def _getImageSource(self, blockedImage):
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
        if self.parent.overrideTab is None:
            if new_offset > 0:
                self.parent.currentTab = self.parent.screenNames.index(
                    self.next_slide.name) if self.next_slide is not None else self.parent.currentTab
            elif new_offset < 0:
                self.parent.currentTab = self.parent.screenNames.index(
                    self.previous_slide.name) if self.previous_slide is not None else self.parent.currentTab
        else:
            self.parent.currentTab = self.parent.overrideTab
            self.parent.overrideTab = None
        self.parent._animateFloatBar(self.parent.currentTab, dur)


def resize(self, _, width, height):
    self.size = (width, height)
    self.resize()


class tabview(App):
    def build(self):
        app = TabView(size=(Window.width, Window.height),
                      screenList=(Label(text="Test"), Label(text="Test"), Label(text="Test")))
        #        app.CalWidget = app._makeCalWidget()
        Window.bind(on_resize=partial(resize, app))
        return app


if __name__ == "__main__":
    tabview().run()
