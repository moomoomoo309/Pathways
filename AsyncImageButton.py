# A normal asyncimage with an on_press function!
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import AsyncImage


class AsyncImageButton(ButtonBehavior, AsyncImage):
    pass
