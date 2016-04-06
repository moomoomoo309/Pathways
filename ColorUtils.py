from kivy.graphics.texture import Texture

# A sample of colors from https://www.google.com/design/spec/style/color.html
PrimaryColors = (
    (0.62, 0.62, 0.62, 1),
    (0.38, 0.49, 0.55, 1),
    (0.47, 0.33, 0.28, 1),
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
    (1, 0.596, 0, 1)
)


# From http://stackoverflow.com/questions/3942878/
def shouldUseWhiteText(color):
    fct = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * fct(color[0]) + 0.7152 * fct(color[1]) + 0.0722 * fct(color[2]) < 0.179


class Gradient(object):
    @staticmethod
    def horizontal(rgba_left, rgba_right):
        texture = Texture.create(size=(2, 1), colorfmt="rgba")
        pixels = rgba_left + rgba_right
        pixels = [chr(int(v * 255)) for v in pixels]
        buf = ''.join(pixels)
        texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
        return texture

    @staticmethod
    def vertical(rgba_top, rgba_bottom):
        texture = Texture.create(size=(1, 2), colorfmt="rgba")
        pixels = rgba_bottom + rgba_top
        pixels = [chr(int(v * 255)) for v in pixels]
        buf = ''.join(pixels)
        texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
        return texture
