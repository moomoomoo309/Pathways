class CalendarSingleDay(Widget):  # This will be very similar to CalendarLessThan30Days.
    pass


class CalendarLessThan30Days(Widget):
    outerLayout = BoxLayout(orientation="horizontal")
    dayBarLayout = BoxLayout(orientation="vertical")
    bodyLayout = BoxLayout(orientation="vertical")
    bodyView = ScrollView(size_hint_y=None)
    days = BoundedNumericProperty(7, min=1, max=7)
    HourBar = RelativeLayout()
    dayList = []

    def __init__(self):
        super(CalendarLessThan30Days, self).__init__()
        self.outerLayout.add_widget(self.dayBarLayout)
        self.outerLayout.add_widget(self.bodyView)
        self.bodyView.add_widget(self.bodyLayout)
        if self.days > 1:
            self.bodyLayout.add_widget(self.HourBar)
        for i in range(self.days):
            self.dayList[i] = RelativeLayout()
            self.bodyLayout.add_widget(self.dayList[i])
