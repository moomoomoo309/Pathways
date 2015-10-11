from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.uix.toggleSquare import ToggleSquare
from kivy.uix.behaviors import DragBehavior
from kivy.input.motionevent import MotionEvent
from kivy.uix.widget import Widget
from kivy.graphics import *
from math import ceil
from collections import namedtuple

SquareSize=32 #Size of each Square
marginSize=1 #Size between the Squares
SquareList=[]
Point=namedtuple("Point", "x y")
lastSquare={"pos":(0,0),"size":(0,0),"colored":False} #Not as pretty as a Lua table, but it works.
lastColor=True
#The color format is in RGB, 1 being 255, 0 being 0.
MarginColorNormal=(1,1,1)
MarginColorToggled=(.5,.5,.5)
RectColorToggled=(.25,.25,.25)
RectColorNormal=(0,0,0)
   

def findSquare(pos,allowRepeats): #Finds the Square at the given coords
    x=pos[0]
    y=pos[1]
    global lastSquare
    for i in SquareList:
        if i["pos"].x<=x<=i["pos"].x+i["size"].x and i["pos"].y<=y<=i["pos"].y+i["size"].y and (i!=lastSquare or allowRepeats):
            lastSquare=i
            return i
        
class GridWidget(Widget):
    def __init__(self,**kwargs):
        super(GridWidget,self).__init__(**kwargs) #Don't ask why you need this line. You just do.
        for x in range(0,int(ceil(Window.width/SquareSize))+1):
            for y in range(0,int(ceil(Window.height/SquareSize))+1):
                with self.canvas:
                    Color(*MarginColorNormal)
                    SquareList.append({"pos":Point(x*(SquareSize+marginSize),y*(SquareSize+marginSize)),"size":Point(SquareSize+marginSize,SquareSize+marginSize),"colored":False})
                    Rectangle(pos=(x*(SquareSize+marginSize),y*(SquareSize+marginSize)),size=(SquareSize+marginSize,SquareSize+marginSize))
                    Color(*RectColorNormal)
                    Rectangle(pos=(x*(SquareSize+marginSize),y*(SquareSize+marginSize)),size=(SquareSize,SquareSize))

    def on_touch_down(self, touch):
        global lastSquare,lastColor,MarginColorNormal,MarginColorToggled,RectColorNormal,RectColorToggled
        foundSquare=findSquare(touch.pos,True)
        if foundSquare is not None: #If it found a NEW square (if it's the same, it returns None
            foundSquare["colored"]=not foundSquare["colored"]
            lastColor=foundSquare["colored"] #This mimics Pathfinding.js's behavior. It works nicely.
            with self.canvas: #Re-draw the rectangle to be changed
                if foundSquare["colored"]:
                    Color(*MarginColorToggled)
                else:
                    Color(*MarginColorNormal)
                Rectangle(pos=(foundSquare["pos"].x,foundSquare["pos"].y),size=(foundSquare["size"].x,foundSquare["size"].y))
                if foundSquare["colored"]:
                    Color(*RectColorToggled)
                else:
                    Color(*RectColorNormal)
                Rectangle(pos=(foundSquare["pos"].x,foundSquare["pos"].y),size=(foundSquare["size"].x-marginSize,foundSquare["size"].y-marginSize))

        
    def on_touch_move(self, touch): #See on_touch_down, the only change is below.
        global lastSquare
        foundSquare=findSquare(touch.pos,False) #This boolean means it will not let you hit the same square twice.
        if foundSquare is not None:
            foundSquare["colored"]=lastColor 
            with self.canvas:
                if foundSquare["colored"]:
                    Color(*MarginColorToggled)
                else:
                    Color(*MarginColorNormal)
                Rectangle(pos=(foundSquare["pos"].x,foundSquare["pos"].y),size=(foundSquare["size"].x,foundSquare["size"].y))
                if foundSquare["colored"]:
                    Color(*RectColorToggled)
                else:
                    Color(*RectColorNormal)
                Rectangle(pos=(foundSquare["pos"].x,foundSquare["pos"].y),size=(foundSquare["size"].x-marginSize,foundSquare["size"].y-marginSize))
        
class OtherGrid(App):
    def build(self):
        return GridWidget()

if __name__== "__main__":
    OtherGrid().run()