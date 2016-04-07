from calendar import monthrange
from datetime import date, datetime
from kivy.animation import Animation, AnimationTransition
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.graphics import Color
from kivy.uix.button import Button
from kivy.uix.carousel import Carousel
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from os.path import isfile
from random import randint

from kivy.graphics.instructions import InstructionGroup
from kivy.graphics.vertex_instructions import Rectangle
from kivy.properties import AliasProperty, BoundedNumericProperty, BooleanProperty, DictProperty, partial

import Globals
from Calendar import Calendar30Days
from ColorUtils import shouldUseWhiteText
from DatePicker import DatePickerWidget, getMonthLength, getStartDay

# Name of each month

MonthNames = (
    "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
    "December")


class TabView(Widget):
    # The size of the top bar
    topBarSize = BoundedNumericProperty(75, min=0)
    # The size of the tabs vertically.
    tabSize = BoundedNumericProperty(50, min=0)
    # The space between the top bar and the tab bar.
    tabMargin = BoundedNumericProperty(2, min=0)
    # The number of tabs displayed at once
    numTabs = BoundedNumericProperty(5, min=1)
    # How much of the tab bar should be taken up by the float bar
    floatBarRatio = BoundedNumericProperty(float(1) / 8, min=0, max=1)
    # Color of the tab bar
    tabBarColor = lambda x: Globals.PrimaryColor
    # Color of the thin bar below the tabs on the tab bar
    floatBarColor = lambda x: Globals.PrimaryColor
    # The tab currently selected
    currentTab = BoundedNumericProperty(4, min=0)

    def __init__(self, **kwargs):
        super(TabView, self).__init__(**kwargs)  # I need this line for reasons.
        # The name of all of the screens
        self.screenNames = self.screenNames if hasattr(self, "screenNames") else ["Schedule", "1 Day", "3 Day", "Week",
            "Month"]

        self.date = date.today()

        # A list of the screens in the carousel.
        self.screenList = []

        # The float bar object
        self.FloatBar = None

        # The carousel object
        self.carousel = None

        # A list containing all of the screens
        self.screenList = []

        # The current month
        self.CurrentMonth = date.today().month - 1  # It's table indices (0-11), not month count (1-12)

        # Forces the tab to be used to be this one.
        self.overrideTab = None

        self.randomImages = Globals.config.getboolean("Real Settings", "randomImages")

        self.size = kwargs["size"] if "size" in kwargs else (100, 100)
        self.pos = kwargs["pos"] if "pos" in kwargs else (0, 0)
        self.carousel = FloatCarousel(
            size=(self.size[0], self.size[1] - self.topBarSize - self.tabMargin - self.tabSize), direction="left",
            min_move=.1, screenNames=self.screenNames, scroll_timeout=200, scroll_distance=10, loop=True)
        # Put everything in a GridLayout
        self.topBarBackground = InstructionGroup()
        self._drawGui(Month=str(MonthNames[self.CurrentMonth]) + " " + str(date.today().year))
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
        Globals.redraw.append((self, redraw))

    # Redraw the whole thing on resize
    def resize(self, width, height):
        self.topBarBackground.clear()
        self._drawTopBarBackground()
        for i in self.children:  # Reset the size of the all the widgets that make up the top bar
            if i == self.FloatBar:
                i.size = [self.size[0] / self.numTabs, self.tabSize * self.floatBarRatio]
                i.pos = [self.currentTab * self.size[0] / self.numTabs,
                    self.size[1] - self.topBarSize - self.tabSize - self.tabMargin]
                i.overlay.children[0].rgb = self.floatBarColor()[0:3]
                i.overlay.children[0].a = .5
            elif i == self.MonthButton:
                i.pos = (-1, self.size[1] - self.topBarSize)
                i.size = (self.size[0], self.topBarSize)
            elif hasattr(self, "datePicker") and i == self.datePicker:
                rows = 6 if getStartDay(i.children[0].date.month, i.children[0].date.year) % 7 + getMonthLength(
                    i.children[0].date.month, i.children[0].date.year) < 35 else 7
                i.size = (min(Window.width, Window.height), self.topBarSize * (rows + 1))
                i.pos = (
                    Window.width / 2 - min(Window.width, Window.height) / 2,
                    Window.height - self.topBarSize * (rows + 1))
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
            if args[0].text[len("[color=ffffff][size=24]"):-len(
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
        # Color the top bar, in its own group so the color can be changed by the redraw function.

        if not hasattr(self, "topBarBackgroundColor"):
            self.topBarBackgroundColor = InstructionGroup()
            self.topBarBackgroundColor.add(Color(*self.tabBarColor()[0:3]))

        self.topBarBackground.add(self.topBarBackgroundColor)

        self.topBarBackground.add(Rectangle(pos=(0, self.size[1] - self.topBarSize - self.tabSize - self.tabMargin),
            size=(self.size[0], self.tabSize)))  # Draw the tabs bar
        self.topBarBackground.add(Color(0, 0, 0))

    def _drawGui(self, Month):  # Draws the tab view (besides the boxes behind the buttons and label)
        self._drawTopBarBackground()
        self.canvas.add(self.topBarBackground)
        # Draw top bar
        # Add text for tabs
        for i in range(0, self.numTabs):
            btn = Button(text_size=self._getTabButtonSize(), size=self._getTabButtonSize(),
                text=("[color=ffffff]" if shouldUseWhiteText(self.tabBarColor())
                else "[color=000000]") + "[size=24]" + self.screenNames[i] + "[/size][/color]",
                background_color=(1, 1, 1, 0), pos=self._getTabButtonPos(i), markup=True, halign="center",
                valign="middle", on_press=self._switchCalScreen)
            btn.i = i
            self.add_widget(btn)
        self.MonthButton = Button(text_size=(self.size[0], self.topBarSize), size=(self.size[0], self.topBarSize),
            text="[color=000000][size=36]" + Month + "[/color][/size]", pos=(-1, self.size[1] - self.topBarSize),
            markup=True, halign="center", valign="middle", on_press=showDate, background_color=(1, 1, 1, 1),
            background_normal="CalendarInactive.png", background_down="CalendarInactive.png")

        self.add_widget(self.MonthButton)

        # It's got markup in it for color and size, and the text is centered vertically and horizontally.
        # The text is from the keyword argument "Month".
        self.FloatBar = AsyncImage(source="CalendarInactive.png",
            size=(self.size[0] / self.numTabs, self.tabSize * self.floatBarRatio), pos=(
                self.currentTab * self.size[0] / self.numTabs,
                self.size[1] - self.topBarSize - self.tabSize - self.tabMargin), keep_ratio=False, allow_stretch=True)

        self.FloatBar.overlay = InstructionGroup()
        color = self.floatBarColor()
        if len(color) == 3:
            color.append(.5)
        else:
            color[3] = .5
        self.FloatBar.overlay.clear()
        self.FloatBar.overlay.add(Color(*color))
        self.FloatBar.overlay.add(Rectangle(pos=self.FloatBar.pos, size=self.FloatBar.size))
        self.FloatBar.canvas.add(self.FloatBar.overlay)
        self.FloatBar.bind(pos=lambda inst, pos: setattr(self.FloatBar.overlay.children[2], "pos", pos))
        self.FloatBar.bind(size=lambda inst, size: setattr(self.FloatBar.overlay.children[2], "size", size))

        self.add_widget(self.FloatBar)
        # Add the float bar

    def changeDate(self, date):
        showGradient(self)
        if hasattr(self, "datePicker"):
            self.remove_widget(self.datePicker)
        for i in self.screenList:
            if hasattr(i.children[0], "changeDate"):
                i.children[0].changeDate(date)

        self.date = date
        if hasattr(self, "datePicker"):
            self.MonthButton.text = self.MonthButton.text[0:len("[color=000000][size=XX]")] + MonthNames[
                date.month - 1] + " " + str(date.year) + "[/size][/color]"


def redraw(self):
    self.topBarBackgroundColor.children[0].rgb = self.tabBarColor()
    self.FloatBar.overlay.children[0].rgb = self.floatBarColor()
    self.FloatBar.overlay.children[0].a = .5
    if hasattr(self, "datePicker"):
        self.datePicker.SelectedColor = self.tabBarColor()
        for i in self.datePicker.header.children:
            i.background_color = self.tabBarColor()
        if self.datePicker.children[0].selectedButton is not None:
            self.datePicker.children[0].selectedButton.background_color = self.tabBarColor()
            self.datePicker.children[0].selectedButton.text = ("[color=ffffff" if shouldUseWhiteText(self.tabBarColor())
            else "[color=000000") + self.datePicker.children[0].selectedButton.text[13:]
        self.datePicker.children[0].PreviousMonth.text = ("[color=ffffff" if shouldUseWhiteText(self.tabBarColor())
        else "[color=000000") + self.datePicker.children[0].PreviousMonth.text[13:]

        self.datePicker.children[0].CurrentMonth.text = ("[color=ffffff" if shouldUseWhiteText(self.tabBarColor())
        else "[color=000000") + self.datePicker.children[0].CurrentMonth.text[13:]

        self.datePicker.children[0].NextMonth.text = ("[color=ffffff" if shouldUseWhiteText(self.tabBarColor())
        else "[color=000000") + self.datePicker.children[0].NextMonth.text[13:]
    for i in self.children:
        if isinstance(i, Button) and i != self.MonthButton and i.text[0:7] == "[color=":
            i.text = ("[color=000000]" if not shouldUseWhiteText(self.tabBarColor()) else "[color=ffffff]") + i.text[
            14:]


def showDate(self):  # Pops up the datePicker, adding the widget when it's needed
    parent = self.parent
    # Make sure to remove the old datePicker if it exists
    if hasattr(parent, "datePicker"):
        parent.remove_widget(parent.datePicker)
    rows = 6 if getStartDay(date.today().month, date.today().year) % 7 + getMonthLength(date.today().month,
        date.today().year) < 35 else 7

    # The actual datePicker widget
    parent.datePicker = DatePickerWidget(size=(min(Window.width, Window.height), parent.topBarSize * (rows + 1)),
        date=parent.date,
        pos=(Window.width / 2 - min(Window.width, Window.height) / 2, Window.height - parent.topBarSize * (rows + 1)))

    # Changes the date when the date is picked
    parent.datePicker.dismiss = parent.changeDate

    hideGradient(self)

    # Add the widget, so it shows up.
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
            elif new_offset < 0:  # If new_offset is 0, the slide has not changed.
                self.parent.currentTab = self.parent.screenNames.index(
                    self.previous_slide.name) if self.previous_slide is not None else self.parent.currentTab
        else:
            self.parent.currentTab = self.parent.overrideTab
            self.parent.overrideTab = None
        # Yeah, this is accessing a protected member of a parent class. It's supposed to.
        self.parent._animateFloatBar(self.parent.currentTab, dur)


def genericResize(*args, **kwargs):  # Generic method to resize any object(s) with given function(s)
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
        randomImages=Globals.config.getboolean("Real Settings", "randomImages"),
        online=Globals.config.getboolean("Real Settings", "online"))


def hideGradient(self):
    screen = self
    while screen.parent is not None and not isinstance(screen, Screen):
        screen = screen.parent
    screen.gradient = False
    screen.canvas.after.children[len(screen.canvas.after.children) - 1].pos = (-100000, -100000)


def showGradient(self):
    screen = self
    app = None
    while screen.parent is not None and not isinstance(screen, Screen):
        if isinstance(screen, TabView):
            app = screen
        screen = screen.parent
    if app is None:
        return
    screen.gradient = False
    rectHeight = 20
    screen.canvas.after.children[len(screen.canvas.after.children) - 1].pos = (0,
    screen.height - rectHeight - app.tabSize * app.floatBarRatio - app.topBarSize - app.tabMargin - app.tabSize * (
        1 - app.floatBarRatio))


class tabview(App):
    def build(self):
        app = TabView(size=(Window.width, Window.height))
        Window.bind(on_resize=partial(genericResize, objs=app, fct=lambda: Window.size))
        app.add_screen(makeCalWidget(app))
        return app


if __name__ == "__main__":
    tabview().run()
