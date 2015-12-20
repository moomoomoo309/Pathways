from calendar import monthrange
from datetime import date, timedelta
from functools import partial
from random import randint

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Canvas, Rectangle, Color
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget

# A sample of colors from https://www.google.com/design/spec/style/color.html
PrimaryColors = (
    (0.957, 0.263, 0.212, 1),
    (0.914, 0.118, 0.388, 1),
    (0.612, 0.153, 0.69, 1),
    (0.404, 0.227, 0.718, 1),
    (0.247, 0.318, 0.71, 1),
    (0.129, 0.588, 0.953, 1),
    (0.012, 0.663, 0.957, 1),
    (0, 0.737, 0.831, 1),
    (0, 0.588, 0.533, 1),
    (0.298, 0.686, 0.314, 1),
    (0.545, 0.765, 0.29, 1),
    (0.804, 0.863, 0.224, 1),
    (1, 0.922, 0.231, 1),
    (1, 0.757, 0.027, 1),
    (1, 0.596, 0, 1),
)


# From http://stackoverflow.com/questions/3942878/
def shouldUseWhiteText(color):
    fct = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * fct(color[0]) + 0.7152 * fct(color[1]) + 0.0722 * fct(color[2]) < 0.179


def getMonthLength(month, year):
    return monthrange(year, month)[1]


def getStartDay(month, year):
    return monthrange(year, month)[0]


class DatePicker(BoxLayout):
    def __init__(self, *args, **kwargs):
        super(DatePicker, self).__init__(**kwargs)
        self.bind(size=self.resize)
        self.bind(parent=lambda self, parent: self.populate_header())
        self.SelectedColor = PrimaryColors[randint(0, len(PrimaryColors) - 1)]
        self.SelectedDate = date.today()
        #        self.bind(SelectedDate=lambda inst, newDate: setattr(inst.parent, "SelectedDate", newDate))
        self.date = date.today()
        self.orientation = "vertical"
        self.month_names = ('January',
                            'February',
                            'March',
                            'April',
                            'May',
                            'June',
                            'July',
                            'August',
                            'September',
                            'October',
                            'November',
                            'December')
        if "month_names" in kwargs:
            self.month_names = kwargs['month_names']
        self.body = GridLayout(cols=7)
        self.add_widget(self.body)

        self.populate_body()
        if self.parent is not None:
            self.populate_header()

    def resize(self, _, size):
        self.parent.header.size = (Window.width, size[1] * .2)
        self.body.size = (Window.width, size[1] * .8)
        self.populate_body()
        if self.parent is not None:
            self.populate_header()

    def populate_header(self, *args, **kwargs):
        textSize = 36
        self.parent.header.clear_widgets()
        previous_month = Button(
            text="[color=000000][size=" + str(textSize) + "]<[/color][/size]" if not shouldUseWhiteText(
                self.SelectedColor) else "[color=ffffff][size=" + str(textSize) + "]<[/color][/size]",
            on_press=partial(self.move_previous_month),
            background_down="", background_normal="", background_color=self.SelectedColor,
            markup=True)

        next_month = Button(text="[color=000000][size=" + str(textSize) + "]>[/color][/size]" if not shouldUseWhiteText(
            self.SelectedColor) else "[color=ffffff][size=" + str(textSize) + "]>[/color][/size]",
                            on_press=self.move_next_month,
                            background_down="", background_normal="", background_color=self.SelectedColor, markup=True)

        month_year_text = self.month_names[self.date.month - 1] + ' ' + str(self.date.year)

        current_month = Button(
            text="[color=000000][size=" + str(
                textSize) + "]" + month_year_text + "[/color][/size]" if not shouldUseWhiteText(
                self.SelectedColor) else "[color=ffffff][size=" + str(
                textSize) + "]" + month_year_text + "[/color][/size]",
            markup=True, background_down="", background_normal="",
            background_color=self.SelectedColor)

        self.parent.header.add_widget(previous_month)
        self.parent.header.add_widget(current_month)
        self.parent.header.add_widget(next_month)

    def populate_body(self, *args, **kwargs):
        textSize = 28
        self.body.clear_widgets()
        date_cursor = date(self.date.year, self.date.month, 1)
        if date_cursor.isoweekday() != 7:
            for filler in range(date_cursor.isoweekday()):
                self.body.add_widget(Widget())
        while date_cursor.month == self.date.month:

            date_label = Button(
                text="[color=000000][size=" + str(textSize) + "]" + str(date_cursor.day) + "[/color][/size]",
                markup=True, background_down="Circle3.png", allow_stretch=True, keep_ratio=False,
                background_color=(0, 0, 0, 0), halign="center", valign="middle", mipmap=True)
            date_label.on_press = partial(self.set_date, day=date_cursor.day, fromPress=True, btn=date_label)
            date_label.bind(size=lambda inst, x: setattr(inst, "text_size", inst.size))
            date_label.size = (self.body.size[0] / self.body.cols,
                               self.body.size[0] / (6 if monthrange(self.date.year,
                                                                    self.date.month)[1] +
                                                         date_cursor.isoweekday() % 7 >= 35 else 5))
            date_label.texture_size = (min(*date_label.size), min(*date_label.size))

            if self.SelectedDate == date_cursor:
                if shouldUseWhiteText(self.SelectedColor):
                    date_label.text = "[color=ffffff]" + date_label.text[14:]
                date_label.background_normal, date_label.background_down = date_label.background_down, date_label.background_normal
                date_label.background_color = self.SelectedColor
            self.body.add_widget(date_label)
            date_cursor += timedelta(days=1)

    def set_date(self, *args, **kwargs):
        if "btn" in kwargs and self.SelectedDate.month == self.date.month and self.SelectedDate.year == self.date.year \
                and int(kwargs["btn"].text[23:kwargs["btn"].text[23:].find("[") + 23]) == self.SelectedDate.day:
            self.parent.dismiss()
        self.date = date(self.date.year, self.date.month, kwargs['day'])
        if "fromPress" in kwargs and kwargs["fromPress"]:
            self.SelectedDate = self.date
        self.populate_body()
        self.populate_header()

    def move_next_month(self, *args, **kwargs):
        if self.date.month == 12:
            self.date = date(self.date.year + 1, 1, self.date.day)
        else:
            self.date = date(self.date.year, self.date.month + 1, 1)
        self.populate_header()
        self.populate_body()

    def move_previous_month(self, *args, **kwargs):
        if self.date.month == 1:
            self.date = date(self.date.year - 1, 12, self.date.day)
        else:
            self.date = date(self.date.year, self.date.month - 1, self.date.day)
        self.populate_header()
        self.populate_body()


class DatePickerWidget(Widget):
    header = None
    originalWidth = 0
    originalX = 0
    child = None
    lastX, lastWidth = 0, 0

    def __init__(self, **kwargs):
        super(DatePickerWidget, self).__init__(**kwargs)
        self.header = BoxLayout(orientation='horizontal', size=(Window.width, 0), pos=(0, Window.height))
        self.bind(size=self.resize)
        self.bind(on_dismiss=lambda inst, x: setattr(inst.children[0], "dismiss", inst.dismiss),
                  pos=self.resize)
        self.originalWidth = kwargs["size"][0] if "size" in kwargs else Window.width
        self.originalX = kwargs["pos"][0] if "pos" in kwargs else 0
        self.size = (Window.width, kwargs["size"][1]) if "size" in kwargs else (100, 100)
        self.pos = (0, kwargs["pos"][1]) if "pos" in kwargs else (0, 0)
        self.dismiss = kwargs["dismiss"] if "dismiss" in kwargs else self.dismiss
        self.lastX = self.originalX
        self.lastWidth = self.originalWidth
        self.resize(*self.size)
        self.add_widget(self.header)
        rows = 6 if getStartDay(date.today().month, date.today().year) % 7 + getMonthLength(
            date.today().month, date.today().year) < 35 else 7
        self.header.size[1] = self.height / (rows + 1)
        self.header.pos[1] = Window.height - self.header.height
        self.child = DatePicker(size=(self.originalWidth, self.height * rows / (rows + 1)),
                                pos=(self.originalX, self.pos[1]), wdg=self)
        self.add_widget(self.child)
        self.drawBackground()
        self.SelectedDate = self.child.SelectedDate

    def resize(self, _, size):
        self.lastWidth = self.originalWidth
        self.lastX = self.originalX
        self.drawBackground()
        self.header.width = Window.width
        self.header.pos[1] = Window.height - self.header.height
        if len(self.children) > 0:
            rows = 6 if getStartDay(self.child.date.month, self.child.date.year) % 7 + getMonthLength(
                self.child.date.month, self.child.date.year) < 35 else 7
            self.child.width = self.originalWidth + self.pos[0] - 100
            self.child.pos = ((Window.width - self.child.width) / 2, self.pos[1])
            self.child.height = self.height * rows / (rows + 1)

    def drawBackground(self):
        if min(*self.size) > 0:
            self.canvas = self.canvas if self.canvas is not None else Canvas()
            self.canvas.before.clear()
            self.canvas.before.add(Color(0, 0, 0, 1))
            self.canvas.before.add(Rectangle(pos=(0, self.pos[1]), size=(Window.width, self.size[1])))
            self.canvas.before.add(Color(1, 1, 1, 1))
            self.canvas.before.add(
                Rectangle(pos=(0, self.pos[1] + 1), size=(Window.width, self.size[1] - 1)))

    def dismiss(self):
        pass


class MyApp(App):
    def build(self):
        widget = DatePickerWidget(size=Window.size)
        Window.bind(on_resize=lambda inst, width, height: setattr(widget, "size", inst.size))
        return widget


if __name__ == '__main__':
    MyApp().run()
