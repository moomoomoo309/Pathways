# A normal asyncimage with an on_press function!
class AsyncImageButton(ButtonBehavior, AsyncImage):
    def on_press(self):
        self.source = getImageSource(self.source)
