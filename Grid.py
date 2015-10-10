from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.behaviors import DragBehavior
from kivy.input.motionevent import MotionEvent

squareSize=40
buttonList=[]
print(Window.width)

def updateLastButton(self):
    lastButton=self
    
def findButton(pos):
    for i in buttonList:
        if i.collide_point(pos):
            return i
    
class Grid(App):
    def build(self):
        layout=GridLayout(cols=Window.width/squareSize)
        for x in range(0,Window.width/squareSize):
            for y in range(0,Window.height/squareSize):
                buttonList.append(ToggleButton(on_press=updateLastButton))
        for i in (buttonList):
            layout.add_widget(i)
        return layout

#Does not work yet, but the idea is to make them toggle on drag like pathfinding.js.   
    def on_touch_move(self, touch):
        if findButton(pos=touch.pos)!=lastButton:
            findButton(pos=touch.pos).toggle()
            return true
        
        
if __name__== "__main__":
    Grid().run()