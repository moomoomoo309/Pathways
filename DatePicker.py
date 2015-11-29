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


class DatePicker(BoxLayout):
    def __init__(self, *args, **kwargs):
        super(DatePicker, self).__init__(**kwargs)
        self.isSelected = True
        self.SelectedColor = PrimaryColors[randint(0, len(PrimaryColors) - 1)]
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
        if kwargs.has_key("month_names"):
            self.month_names = kwargs['month_names']
        self.header = BoxLayout(orientation='horizontal',
                                size_hint=(1, 0.2))
        self.body = GridLayout(cols=7)
        self.add_widget(self.header)
        self.add_widget(self.body)

        self.populate_body()
        self.populate_header()

    def populate_header(self, *args, **kwargs):
        self.header.clear_widgets()
        previous_month = Button(text="[color=000000][size=36]<[/color][/size]" if not shouldUseWhiteText(
            self.SelectedColor) else "[color=ffffff][size=36]<[/color][/size]",
                                on_press=partial(self.move_previous_month),
                                background_down="", background_normal="", background_color=self.SelectedColor,
                                markup=True)

        next_month = Button(text="[color=000000][size=36]>[/color][/size]" if not shouldUseWhiteText(
            self.SelectedColor) else "[color=ffffff][size=36]>[/color][/size]", on_press=self.move_next_month,
                            background_down="", background_normal="", background_color=self.SelectedColor, markup=True)

        month_year_text = self.month_names[self.date.month - 1] + ' ' + str(self.date.year)

        current_month = Button(
            text="[color=000000][size=36]" + month_year_text + "[/color][/size]" if not shouldUseWhiteText(
                self.SelectedColor) else "[color=ffffff][size=36]" + month_year_text + "[/color][/size]",
            size_hint=(2, 1),
            markup=True, background_down="", background_normal="",
            background_color=self.SelectedColor)

        self.header.add_widget(previous_month)
        self.header.add_widget(current_month)
        self.header.add_widget(next_month)

    def populate_body(self, *args, **kwargs):
        self.body.clear_widgets()
        date_cursor = date(self.date.year, self.date.month, 1)
        if date_cursor.isoweekday() != 7:
            for filler in range(date_cursor.isoweekday()):
                self.body.add_widget(Widget())
        while date_cursor.month == self.date.month:
            date_label = Button(text="[color=000000][size=36]" + str(date_cursor.day) + "[/color][/size]",
                                markup=True, background_down="Circle2.png", background_normal="CalendarInactive.png",
                                on_press=partial(self.set_date, day=date_cursor.day))
            if self.isSelected and self.date.day == date_cursor.day:
                if shouldUseWhiteText(self.SelectedColor):
                    date_label.text = "[color=ffffff]" + date_label.text[14:]
                date_label.background_normal, date_label.background_down = date_label.background_down, date_label.background_normal
                date_label.background_color = self.SelectedColor
            self.body.add_widget(date_label)
            date_cursor += timedelta(days=1)

    def set_date(self, *args, **kwargs):
        self.isSelected = True
        self.date = date(self.date.year, self.date.month, kwargs['day'])
        self.populate_body()
        self.populate_header()

    def move_next_month(self, *args, **kwargs):
        if self.date.month == 12:
            self.date = date(self.date.year + 1, 1, self.date.day)
        else:
            self.date = date(self.date.year, self.date.month + 1, 1)
            self.isSelected = False
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
    def __init__(self, **kwargs):
        super(DatePickerWidget, self).__init__(**kwargs)
        self.size = kwargs["size"] if "size" in kwargs else (100, 100)
        self.pos = kwargs["pos"] if "pos" in kwargs else (0, 0)
        self.canvas = Canvas()
        self.canvas.before.clear()
        self.canvas.before.add(Color(1, 1, 1, 1))
        self.canvas.before.add(Rectangle(pos=(0, 0), size=(Window.width, Window.height)))
        self.add_widget(DatePicker(size=self.size, pos=self.pos))


class MyApp(App):
    def build(self):
        return DatePickerWidget(size=Window.size)


if __name__ == '__main__':
    MyApp().run()
