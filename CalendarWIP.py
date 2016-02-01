from __future__ import print_function
from datetime import datetime, date
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from Event import Event

from kivy.properties import BoundedNumericProperty, ObjectProperty
from kivy.graphics import Rectangle, Color


class CalendarLessThan30Days(Widget):
    outerLayout = BoxLayout(orientation="vertical", size=Window.size, spacing=1)  # Contains the top bar "head" and body.
    innerLayout = BoxLayout(orientation="horizontal", size=Window.size)  # Sizes the bodyView
    hourBar = BoxLayout(orientation="vertical", size=Window.size, size_hint_x=.2)  # Has the time being viewed
    bodyLayout = GridLayout(rows=1, width=Window.width, size_hint_y=None, height=2048)  # Has the hourbar and inner body
    innerBodyLayout = GridLayout(rows=1)  # Contains the actual body
    bodyView = ScrollView(size_hint_y=None, width=Window.width,
                          height=Window.height * .8)  # Scrollable bits, dayBar and actual body
    days = BoundedNumericProperty(7, min=1, max=7)
    dayBarLayout = GridLayout(rows=1, size_hint_y=.25)  # Layout for the dayBar, if it exists, and body
    dayList = []
    eventHeight = 65
    startDate = ObjectProperty(date.today())

    def __init__(self, **kwargs):
        super(CalendarLessThan30Days, self).__init__()
        # Propagate resize to children below
        self.bind(size=lambda inst, size: setattr(self.outerLayout, "size", size))
        self.outerLayout.bind(width=lambda inst, width: setattr(self.innerLayout, "width", width))
        self.innerLayout.bind(size=lambda inst, size: setattr(self.bodyView, "size", (size[0], self.height * .8)))
        self.bodyView.bind(width=lambda inst, width: setattr(self.bodyLayout, "width", width))

        # Forces the relativeLayout to size the dayBar to a constant(-ish) width

        self.hourBar.realWidth = 100  # Test width, should be width of the largest time label when done
        self.hourBar.bind(size=lambda inst, size: setattr(inst, "size_hint_x", float(inst.realWidth) / Window.width))
        for i in range(24):
            lbl = Button(text=str((i + 11) % 12 + 1) + " " + ("AM" if i < 12 else "PM"), color=(0, 0, 0, 1),
                         background_normal="CalendarActive.png", background_down="CalendarActive.png", halign="center",
                         valign="top", text_size=(100,2048/24))
            lbl.bind(size=lambda inst,size: setattr(lbl,"text_size",size))
            self.hourBar.add_widget(lbl)

        # Adding layout structure below...
        self.add_widget(self.outerLayout)
        self.outerLayout.add_widget(self.innerLayout)
        self.innerLayout.add_widget(self.bodyView)
        self.bodyView.add_widget(self.bodyLayout)
        self.bodyLayout.add_widget(self.hourBar)
        self.bodyLayout.add_widget(self.innerBodyLayout)
        # Test widget
        WidgetsToAddOnAGivenDay = []  # This is for demo purposes, it will be removed.
        if self.days > 1:  # Add the hour bar if it's not one day
            self.outerLayout.add_widget(self.dayBarLayout, len(self.outerLayout.children))
            self.weekButton=Button(text=str(self.startDate.isocalendar()[1]))
            self.hourBar.bind(width=lambda inst, width: setattr(self.weekButton, "width", width))
            self.hourBar.bind(size_hint_x=lambda inst, size_hint_x: setattr(self.weekButton, "size_hint_x", size_hint_x))
            self.hourBar.bind(size_hint_x=lambda inst, size_hint_x: print(size_hint_x))
            self.dayBarLayout.add_widget(self.weekButton)

        for i in range(self.days):
#            self.dayBarLayout.add_widget(Image(source="CalendarInactive.png", allow_stretch=True, keep_ratio=False))  # Test Widget
            # Place your events using pos_hint and size_hint!
            dayLayout = RelativeLayout()
            dayLayout.canvas.before.add(Color(1, 1, 1, 1))
            rect = Rectangle(pos=Widget.to_widget(dayLayout, 0, 0), size=dayLayout.size)
            dayLayout.bind(
                size=lambda inst, size: setattr(inst.canvas.before.children[len(inst.canvas.before.children) - 1],
                                                "size", (size[0] - 1, size[1])))
            dayLayout.bind(
                pos=lambda inst, pos: setattr(inst.canvas.before.children[len(inst.canvas.before.children) - 1], "pos",
                                              inst.to_local(pos[0] + 1, pos[1])))
            dayLayout.canvas.before.add(rect)
            self.dayList.append(dayLayout)  # Put a layout for each day, so the columns are separate.

            self.innerBodyLayout.add_widget(self.dayList[i])
            # Test Widget
            event = Event(size_hint_y=float(self.eventHeight) / self.bodyLayout.height, x=1,
                          pos_hint={"center_y": 1 - (140./2048) - timeToPos(datetime.now())},
                          name="TestButton" + str(i), background_normal="CalendarInactive.png",
                          background_down="CalendarInactive.png", background_color=(0, .5, 0, 1),
                          color=(0, 0, 0, 1))
            event.bind(width=lambda inst, width: setattr(inst, "width", inst.parent.width - 1))
            self.dayList[i].add_widget(event)
            for event in WidgetsToAddOnAGivenDay:  # Sort them out by date before here
                event.pos_hint = {"center_y": 1 - timeToPos(event.time)}
                self.dayList[i].add_widget(event)


def timeToPos(time):  # Returns the time normalized between 0 and 1.
    return float(time.hour - 1 + time.minute / 60) / 24


class MyApp(App):  # Test for the datePicker
    def build(self):
        widget = CalendarLessThan30Days(days=7, size=Window.size)
        Window.bind(on_resize=lambda inst, width, height: setattr(widget, "size", inst.size))
        return widget


if __name__ == '__main__':
    MyApp().run()
