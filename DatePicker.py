from datetime import date, timedelta

from functools import partial
from random import randrange
from kivy.app import App

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget


class DatePicker(BoxLayout):
    def __init__(self, *args, **kwargs):
        super(DatePicker, self).__init__(**kwargs)
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
        previous_month = Button(text="[color=000000][size=36]<[/color][/size]", on_press=partial(self.move_previous_month),
                            background_down="CalendarActive.png", background_normal="CalendarActive.png", markup=True)
        next_month = Button(text="[color=000000][size=36]>[/color][/size]", on_press=self.move_next_month,
                            background_down="CalendarActive.png", background_normal="CalendarActive.png", markup=True)
        month_year_text = self.month_names[self.date.month - 1] + ' ' + str(self.date.year)
        current_month = Button(text="[color=000000][size=36]"+month_year_text+"[/color][/size]", size_hint=(2, 1),
                              markup=True, background_down="CalendarActive.png", background_normal="CalendarActive.png")

        self.header.add_widget(previous_month)
        self.header.add_widget(current_month)
        self.header.add_widget(next_month)

    def populate_body(self, *args, **kwargs):
        self.body.clear_widgets()
        date_cursor = date(self.date.year, self.date.month, 1)
        if date_cursor.isoweekday()!=7:
            for filler in range(date_cursor.isoweekday()):
                self.body.add_widget(Widget())
        while date_cursor.month == self.date.month:
            date_label = Button(text="[color=000000][size=36]"+str(date_cursor.day)+"[/color][/size]",
                                markup=True, background_color=[1, 1, 1, 1],
                                background_down="Circle.png", background_normal="CalendarInactive.png")
            date_label.bind(on_press=partial(self.set_date, day=date_cursor.day, btn=date_label))
            if self.date.day == date_cursor.day:
                date_label.background_normal, date_label.background_down = date_label.background_down, date_label.background_normal
            self.body.add_widget(date_label)
            date_cursor += timedelta(days=1)

    def pressButton(self, *args, **kwargs):
        if "btn" in kwargs:
            kwargs["btn"].background_color = (randrange(0, 1), randrange(0, 1), randrange(0, 1), randrange(0, 1))
        self.set_date(*args, **kwargs)

    def set_date(self, *args, **kwargs):
        self.date = date(self.date.year, self.date.month, kwargs['day'])
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


class MyApp(App):
    def build(self):
        return DatePicker()


if __name__ == '__main__':
    MyApp().run()
