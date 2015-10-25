from kivy.app import App
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.graphics.vertex_instructions import Rectangle
from kivy.uix.label import Label

topBarSize = 75
#The size of the top bar


class CalendarGrid(GridLayout):
    def __init__(self):
        super(CalendarGrid, self).__init__() #I need this line for reasons.
        self.cols = 7
        self.rows = 6
        #The grid is 7x6 because 7x5 isn't enough for months which start on Saturday
        self.spacing = 0
        #No spacing between each grid element is necessary.
        self.size = (Window.width, Window.height - topBarSize)
        #Keep it within its bounds.
        self.pos[1] -= 3
        self.pos[0] += 1
        #Center it a little nicer than kivy does by default.
        for i in range(0, 6):
            self.add_widget(Widget()) #If the month doesn't start on a Monday, you need an empty day.
        for i in range(0, 31):
            self.add_widget(ToggleButton(text=str(i + 1), group="CalendarGrid_Days"))
            #The group means they act as radio buttons, so only one is toggleable at a time.


class CalendarWidget(Widget):
    def __init__(self, **kwargs):
        super(CalendarWidget, self).__init__() #Still need this, apparently.
        with self.canvas:
            Rectangle(pos=(0, Window.height - topBarSize), size=(Window.width, topBarSize)) #Draw the top bar

        self.add_widget(Label(text_size=(Window.width, topBarSize), size=(Window.width, topBarSize),
                              text="[color=000000][size=36]" + kwargs["Month"] + "[/color][/size]",
                              pos=(0, Window.height - topBarSize), markup=True, halign="center", valign="middle"))
        #It's got markup in it for color and size, and the text is centered vertically and horizontally.
        #The text is from the keyword argument "Month".
        self.add_widget(CalendarGrid())\
        #And this adds the grid.


class Calendar(App):
    def build(self):
        return CalendarWidget(Month="September")


if __name__ == "__main__":
    Calendar().run()
