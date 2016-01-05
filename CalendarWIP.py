from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import BoundedNumericProperty
from kivy.uix.relativelayout import RelativeLayout
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.button import Button

class CalendarSingleDay(Widget):  # This will be very similar to CalendarLessThan30Days.
    pass


class CalendarLessThan30Days(Widget):
    outerLayout = BoxLayout(orientation="vertical", size=Window.size) # Contains the top bar "head" and body.
    innerLayout = BoxLayout(orientation="horizontal", size=Window.size) # Sizes the bodyView
    dayBarLayout = BoxLayout(orientation="vertical", size=Window.size, size_hint_x=.2)
    bodyLayout = BoxLayout(orientation="horizontal", size=Window.size) # Layout for the dayBar, if it exists, and body
    innerBodyLayout = BoxLayout(orientation="horizontal", size=Window.size) # Contains the actual body
    bodyView = ScrollView(size_hint_y=None, size=Window.size) # Scrollable bits, dayBar and actual body
    days = BoundedNumericProperty(7, min=1, max=7)
    HourBar = RelativeLayout(size_hint_y=.2) # Has the time being viewed
    dayBarLayout.realWidth=dayBarLayout.width # Forces the relativeLayout to make the width constant.
    dayList = []

    def __init__(self, **kwargs):
        super(CalendarLessThan30Days, self).__init__()
        # Propogate resize to children below
        self.bind(size=lambda inst, size: setattr(self.outerLayout,"size",size))
        self.outerLayout.bind(size=lambda inst, size: setattr(self.innerLayout,"size",size))
        self.innerLayout.bind(size=lambda inst, size: setattr(self.bodyLayout,"size",size))
        self.bodyLayout.bind(size=lambda inst, size: setattr(self.bodyView,"size",size))

        # Forces the relativeLayout to size the dayBar to a constant(-ish) width
        self.dayBarLayout.bind(size=lambda inst, size: setattr(inst,"size_hint_x",float(inst.realWidth)/Window.width))

        self.dayBarLayout.realWidth=100 # Test width, should be width of the largest time label when done

        # Adding layout structure below...
        self.outerLayout.add_widget(self.innerLayout)
        self.innerLayout.add_widget(self.bodyView)
        self.bodyView.add_widget(self.bodyLayout)
        self.bodyLayout.add_widget(self.dayBarLayout)
        self.bodyLayout.add_widget(self.innerBodyLayout)

        self.dayBarLayout.add_widget(Image(source="CalendarActive.png", allow_stretch=True, keep_ratio=False))
        # Test widget
        if self.days > 1: # Add the hour bar if it's not one day
            self.outerLayout.add_widget(self.HourBar, len(self.outerLayout.children))
            self.HourBar.add_widget(Image(source="Circle3.png", allow_stretch=True, keep_ratio=False))  # Test Widget
        for i in range(self.days):
            self.dayList.append(RelativeLayout()) # Put a layout for each day, so the columns are separate.
            self.innerBodyLayout.add_widget(self.dayList[i])
            self.dayList[i].add_widget(Button()) # Test Widget
        self.add_widget(self.outerLayout)


class MyApp(App):  # Test for the datePicker
    def build(self):
        widget = CalendarLessThan30Days(days=7, size=Window.size)
        Window.bind(on_resize=lambda inst, width, height: setattr(widget, "size", inst.size))
        return widget


if __name__ == '__main__':
    MyApp().run()
