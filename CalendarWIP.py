from datetime import datetime, date
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from kivy.properties import BoundedNumericProperty, ObjectProperty


class CalendarLessThan30Days(Widget):
    outerLayout = BoxLayout(orientation="vertical", size=Window.size)  # Contains the top bar "head" and body.
    innerLayout = BoxLayout(orientation="horizontal", size=Window.size)  # Sizes the bodyView
    hourBar = BoxLayout(orientation="vertical", size=Window.size, size_hint_x=.2)  # Has the time being viewed
    bodyLayout = GridLayout(rows=1, width=Window.width, size_hint_y=None, height=2048)  # Has the hourbar and inner body
    innerBodyLayout = GridLayout(rows=1, size=Window.size)  # Contains the actual body
    bodyView = ScrollView(size_hint_y=None, width=Window.width,
                          height=Window.height * .8)  # Scrollable bits, dayBar and actual body
    days = BoundedNumericProperty(7, min=1, max=7)
    dayBarLayout = RelativeLayout(size_hint_y=.2)  # Layout for the dayBar, if it exists, and body
    dayBarLayout.realWidth = dayBarLayout.width  # Forces the relativeLayout to make the width constant.
    dayList = []
    eventHeight = 65
    startDate = ObjectProperty(date.today())

    def __init__(self, **kwargs):
        super(CalendarLessThan30Days, self).__init__()
        # Propagate resize to children below
        self.bind(size=lambda inst, size: setattr(self.outerLayout, "size", size))
        self.outerLayout.bind(width=lambda inst, width: setattr(self.innerLayout, "width", width))
        self.innerLayout.bind(size=lambda inst, size: setattr(self.bodyView, "size", (size[0],Window.height*.8)))
        self.bodyView.bind(width=lambda inst, width: setattr(self.bodyLayout, "width", width))

        # Forces the relativeLayout to size the dayBar to a constant(-ish) width

        self.hourBar.realWidth = 100  # Test width, should be width of the largest time label when done
        self.hourBar.bind(size=lambda inst, size: setattr(inst, "size_hint_x", float(inst.realWidth) / Window.width))

        # Adding layout structure below...
        self.add_widget(self.outerLayout)
        self.outerLayout.add_widget(self.innerLayout)
        self.innerLayout.add_widget(self.bodyView)
        self.bodyView.add_widget(self.bodyLayout)
        self.bodyLayout.add_widget(self.hourBar)
        self.bodyLayout.add_widget(self.innerBodyLayout)

        self.hourBar.add_widget(Image(source="Circle.png", allow_stretch=True, keep_ratio=False))
        # Test widget
        WidgetsToAddOnAGivenDay = []  # This is for demo purposes, it will be removed.
        if self.days > 1:  # Add the hour bar if it's not one day
            self.outerLayout.add_widget(self.dayBarLayout, len(self.outerLayout.children))
            self.dayBarLayout.add_widget(
                Image(source="Circle3.png", allow_stretch=True, keep_ratio=False))  # Test Widget
        for i in range(self.days):
            # Place your events using pos_hint and size_hint!
            self.dayList.append(RelativeLayout())  # Put a layout for each day, so the columns are separate.
            self.innerBodyLayout.add_widget(self.dayList[i])
            self.dayList[i].add_widget(Button(size_hint_y=float(self.eventHeight) / self.bodyLayout.height,
                                              pos_hint={"center_y": 1 - timeToPos(datetime.now())}))  # Test Widget
            for event in WidgetsToAddOnAGivenDay:  # Sort them out by date before here
                event.pos_hint["center_y"] = 1 - timeToPos(event.time)
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
