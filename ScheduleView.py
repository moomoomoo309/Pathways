from datetime import date
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line
from kivy.properties import ObjectProperty


class ScheduleView(Widget):
    currentDate = ObjectProperty(date.today())

    def __init__(self, **kwargs):
        super(ScheduleView, self).__init__(**kwargs)
        self.bodyView = ScrollView(size=self.size)
        self.bind(size=lambda inst, size: setattr(self.bodyView, "size", size))
        self.outerLayout = BoxLayout(orientation="vertical", size=self.size)
        self.bind(size=lambda inst, size: setattr(self.outerLayout, "size", size))
        for i in self.outerLayout.children:
            i.children.sort(lambda inst, inst2: inst.date < inst2.date)
        self.add_widget(self.bodyView)
        self.bodyView.add_widget(self.outerLayout)
        self.outerLayout.add_widget(dateHeader())
        self.outerLayout.add_widget(Image(source="Circle.png", keep_ratio=False, allow_stretch=True))


class dateHeader(BoxLayout):
    orientation = "horizontal"

    def __init__(self, **kwargs):
        super(dateHeader, self).__init__(**kwargs)
        self.date = kwargs["date"] if "date" in kwargs else date.today()
        self.size_hint_y = .1
        self.label = Label(text=str(self.date), color=(1, 1, 1, 1), font_size=36, text_size=(None, None),
            size_hint_x=None)
        self.label.bind(texture_size=lambda inst, texture_size: setattr(self.label, "width", texture_size[0]))
        self.lineColor = kwargs["lineColor"] if "lineColor" in kwargs else (1, 1, 1, 1)
        self.lineWidget = Widget()
        self.lineWidget.canvas.add(Color(*self.lineColor))
        self.lineInstruction = Line(cap='none',
            points=[self.lineWidget.x + 10, self.lineWidget.y + self.lineWidget.height / 2,
                self.lineWidget.x + self.lineWidget.width, self.lineWidget.y + self.lineWidget.height / 2],
            width=5)
        self.lineWidget.canvas.add(self.lineInstruction)
        self.lineWidget.bind(size=lambda inst, size: setattr(self.lineInstruction, "points",
            [self.lineWidget.x + 10, self.lineWidget.y + self.lineWidget.height / 2,
                self.lineWidget.x + self.lineWidget.width, self.lineWidget.y + self.lineWidget.height / 2]))
        self.add_widget(Widget(size_hint_x=.05))
        self.add_widget(self.label)
        self.add_widget(self.lineWidget)
