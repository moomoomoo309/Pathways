from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.behaviors import DragBehavior
from kivy.input.motionevent import MotionEvent
from kivy.uix.widget import Widget
from kivy.graphics import *
from math import ceil
from collections import namedtuple

squareSize=32
marginSize=1
buttonList=[]
Point=namedtuple("Point", "x y")
lastButton={"pos":(0,0),"size":(0,0),"colored":False}
lastColor=True
   

def findButton(pos,allowRepeats):
    x=pos[0]
    y=pos[1]
    global lastButton
    for i in buttonList:
        if i["pos"].x<=x<=i["pos"].x+i["size"].x and i["pos"].y<=y<=i["pos"].y+i["size"].y and (i!=lastButton or allowRepeats):
            lastButton=i
            return i
        
class GridWidget(Widget):
    def __init__(self,**kwargs):
        super(GridWidget,self).__init__(**kwargs)
        for x in range(0,int(ceil(Window.width/squareSize))+1):
            for y in range(0,int(ceil(Window.height/squareSize))+1):
                with self.canvas:
                    Color(1,1,1)
                    buttonList.append({"pos":Point(x*(squareSize+marginSize),y*(squareSize+marginSize)),"size":Point(squareSize+marginSize,squareSize+marginSize),"colored":False})
                    Rectangle(pos=(x*(squareSize+marginSize),y*(squareSize+marginSize)),size=(squareSize+marginSize,squareSize+marginSize))
                    Color(0,0,0)
                    Rectangle(pos=(x*(squareSize+marginSize),y*(squareSize+marginSize)),size=(squareSize,squareSize))

    def on_touch_down(self, touch):
        global lastButton
        global lastColor
        foundButton=findButton(touch.pos,True)
        if foundButton is not None:
            foundButton["colored"]=not foundButton["colored"]
            lastColor=foundButton["colored"]
            with self.canvas:
                if foundButton["colored"]:
                    Color(.5,.5,.5)
                else:
                    Color(1,1,1)
                Rectangle(pos=(foundButton["pos"].x,foundButton["pos"].y),size=(foundButton["size"].x,foundButton["size"].y))
                if foundButton["colored"]:
                    Color(.25,.25,.25)
                else:
                    Color(0,0,0)
                Rectangle(pos=(foundButton["pos"].x,foundButton["pos"].y),size=(foundButton["size"].x-marginSize,foundButton["size"].y-marginSize))

        
    def on_touch_move(self, touch):
        global lastButton
        foundButton=findButton(touch.pos,False)
        if foundButton is not None:
            foundButton["colored"]=lastColor
            with self.canvas:
                if foundButton["colored"]:
                    Color(.5,.5,.5)
                else:
                    Color(1,1,1)
                Rectangle(pos=(foundButton["pos"].x,foundButton["pos"].y),size=(foundButton["size"].x,foundButton["size"].y))
                if foundButton["colored"]:
                    Color(.25,.25,.25)
                else:
                    Color(0,0,0)
                Rectangle(pos=(foundButton["pos"].x,foundButton["pos"].y),size=(foundButton["size"].x-marginSize,foundButton["size"].y-marginSize))
        
class OtherGrid(App):
    def build(self):
        return GridWidget()

if __name__== "__main__":
    OtherGrid().run()