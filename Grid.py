from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from math import ceil
from collections import namedtuple
from kivy.graphics import *

SquareSize=32 #Size of each Square
MarginSize=1 #Size between the Squares
SquareList=[]
Point=namedtuple("Point", "x y")
lastSquare={"pos":(0,0),"size":(0,0),"colored":False} #Not as pretty as a Lua table, but it works.
lastColor=True
#The color format is in RGB, 1 being 255, 0 being 0.
MarginColorNormal=(1,1,1)
MarginColorToggled=(.5,.5,.5)
RectColorToggled=(.25,.25,.25)
RectColorNormal=(0,0,0)
ManualMonitorSize=(1680,1050) #Size of your monitor, so when the window is maximized, the grid will scale. Set to None if you want it to just use the default window size
   
def findSquare(pos,allowRepeats): #Finds the Square at the given coords
    global lastSquare
    for i in SquareList:
        if i["pos"].x<=pos[0]<=i["pos"].x+i["size"].x and i["pos"].y<=pos[1]<=i["pos"].y+i["size"].y and (i!=lastSquare or allowRepeats):
            lastSquare=i
            return i

        
def updateRect(self,touch,isTouchDown,foundSquare):
    if foundSquare is None:
        foundSquare=findSquare(touch.pos,isTouchDown)
    if foundSquare is not None: #If it found a NEW square (if it's the same, it returns None)
        foundSquare["colored"]=lastColor #Color them the same color as the one from on_touch_down
        with self.canvas: #Re-draw the rectangle to be changed
            if foundSquare["colored"]:
                Color(*MarginColorToggled) #Unpack the tuple the color is stored in
            else:
                Color(*MarginColorNormal)
            Rectangle(pos=(foundSquare["pos"].x,foundSquare["pos"].y),size=(foundSquare["size"].x,foundSquare["size"].y))
            #Draw the margins of the rectangle
            if foundSquare["colored"]:
                Color(*RectColorToggled)
            else:
                Color(*RectColorNormal)
            Rectangle(pos=(foundSquare["pos"].x,foundSquare["pos"].y),size=(foundSquare["size"].x-MarginSize,foundSquare["size"].y-MarginSize))
            #Draw the actual rectangle


def drawGrid(self,width,height):
    global SquareList
    for x in range(0,int(ceil(width/SquareSize))):
        for y in range(0,int(ceil(height/SquareSize))+1):
            with self.canvas:
                testSquare=findSquare((x*SquareSize*3/2,y*SquareSize*3/2),True) #Make sure there isn't already a square at the given coordinates
                if testSquare is None:
                    Color(*MarginColorNormal)
                    SquareList.append({"pos":Point(x*(SquareSize+MarginSize),y*(SquareSize+MarginSize)),"size":Point(SquareSize+MarginSize,SquareSize+MarginSize),"colored":False})
                    #Add a square to the given location (Margin included)
                    Rectangle(pos=(x*(SquareSize+MarginSize),y*(SquareSize+MarginSize)),size=(SquareSize+MarginSize,SquareSize+MarginSize))
                    #Draw the margins of the rectangle
                    Color(*RectColorNormal)
                    Rectangle(pos=(x*(SquareSize+MarginSize),y*(SquareSize+MarginSize)),size=(SquareSize,SquareSize))
                    #Draw the actual rectangle
                    

class GridWidget(Widget):
    def __init__(self,**kwargs):
        super(GridWidget,self).__init__(**kwargs) #Don't ask why you need this line. You just do.
        if ManualMonitorSize is None:
            drawGrid(self,Window.width,Window.height) #Use the window size if a resolution is not provided
        else:
            drawGrid(self,*ManualMonitorSize) #Otherwise, use the window size given.
        
    def on_touch_down(self, touch):
        global lastColor
        foundSquare=findSquare(touch.pos,True)
        if foundSquare is not None:
            lastColor=not foundSquare["colored"] #This mimics Pathfinding.js's behavior.
        #It's a bit awkward because I had two nearly identical functions, which I made into one, so this logic had to be put here.
        updateRect(self,touch,True,foundSquare) #The foundSquare is given so it doesn't have to search for it twice.

    def on_touch_move(self, touch):
        updateRect(self,touch,False,None)


class Grid(App):
    def build(self):
        return GridWidget()

if __name__== "__main__":
    Grid().run()
