from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from math import ceil
from collections import namedtuple
from kivy.graphics import *
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

SquareSize = 32  # Size of each Square
MarginSize = 2  # Size between the Squares
SquareList = []
Point = namedtuple("Point", "x y")
lastSquare = {"pos":(0, 0), "size":(0, 0), "colored":False}  # Not as pretty as a Lua table, but it works.
lastColor = True

# The color format is in RGB, 1 being 255, 0 being 0.
StartSquarePos=None #It'll be initialized later.
EndSquarePos=None
LastStartSquarePos=None
LastEndSquarePos=None
StartColorNormal=(0,1,0)
StartColorMargin=(.65,1,.65)
EndColorNormal=(1,0,0)
EndColorMargin=(1,.65,.65)
MarginColorNormal = (1, 1, 1)
MarginColorToggled = (.5, .5, .5)
RectColorToggled = (.25, .25, .25)
RectColorNormal = (0, 0, 0)
RectSize=(SquareSize+MarginSize,SquareSize+MarginSize)
GrabbedEndPoint=None #True for start, false for end
ManualMonitorSize = None  # Size of your monitor, so when the window is maximized, the grid will scale. Set to None if you want it to just use the default window size
   
def findSquare(pos, allowRepeats):  # Finds the Square at the given coords
    global lastSquare
    for i in SquareList:
        if i["pos"].x < pos[0] <= i["pos"].x + i["size"].x and i["pos"].y <= pos[1] < i["pos"].y + i["size"].y and (i != lastSquare or allowRepeats):
            lastSquare = i
            return i

def getSquareCoords(pos):
    return (pos[0]-pos[0]%(MarginSize+SquareSize),pos[1]-pos[1]%(MarginSize+SquareSize))
        
def updateRect(self, touch, isTouchDown, foundSquare):
    if foundSquare is None:
        foundSquare = findSquare(touch.pos, isTouchDown)
    if foundSquare is not None and StartSquarePos!=foundSquare["pos"]!=EndSquarePos:  # If it found a NEW square (if it's the same, it returns None)
        foundSquare["colored"] = lastColor  # Color them the same color as the one from on_touch_down
        with self.canvas:  # Re-draw the rectangle to be changed
            if foundSquare["colored"]:
                Color(*MarginColorToggled)  # Unpack the tuple the color is stored in
            else:
                Color(*MarginColorNormal)
            Rectangle(pos=(foundSquare["pos"].x, foundSquare["pos"].y), size=(foundSquare["size"].x, foundSquare["size"].y))
            # Draw the margins of the rectangle
            if foundSquare["colored"]:
                Color(*RectColorToggled)
            else:
                Color(*RectColorNormal)
            Rectangle(pos=(foundSquare["pos"].x, foundSquare["pos"].y), size=(foundSquare["size"].x - MarginSize, foundSquare["size"].y - MarginSize))
            # Draw the actual rectangle

def drawStartAndEnd(self):
    global LastStartSquarePos,LastEndSquarePos
    with self.canvas:
        Color(*StartColorMargin) #Draw Margin of start point
        Rectangle(pos=StartSquarePos,size=RectSize)
        Color(*StartColorNormal) #Draw actual start point
        Rectangle(pos=StartSquarePos,size=(SquareSize,SquareSize))
        Color(*EndColorMargin) #Draw Margin of end point
        Rectangle(pos=EndSquarePos,size=RectSize)
        Color(*EndColorNormal) #Draw actual end point
        Rectangle(pos=EndSquarePos,size=(SquareSize,SquareSize))
    if GrabbedEndPoint is not None:
        if GrabbedEndPoint: #Save the location of the last start/end point so you can re-draw the rectangle underneath
            LastStartSquarePos=StartSquarePos 
        else:
            LastEndSquarePos=EndSquarePos

def updateStartAndEnd(self,touch):
    global StartSquarePos,EndSquarePos
    foundSquare=findSquare(touch.pos,False)
    if foundSquare is not None and not foundSquare["colored"]:
        if GrabbedEndPoint==True and foundSquare["pos"]!=EndSquarePos:
            StartSquarePos=getSquareCoords(touch.pos)
        elif GrabbedEndPoint==False and foundSquare["pos"]!=StartSquarePos:
            EndSquarePos=getSquareCoords(touch.pos)
    if GrabbedEndPoint is not None: #Re-draw the rectangle misplaced by the start/end point last time it moved
        if GrabbedEndPoint:
            with self.canvas:
                if foundSquare is not None and foundSquare["colored"]:
                    Color(*MarginColorToggled) #Draw Margin of start point
                    Rectangle(pos=LastStartSquarePos,size=RectSize)
                    Color(*RectColorToggled) #Draw actual start point
                    Rectangle(pos=LastStartSquarePos,size=(SquareSize,SquareSize))
                elif foundSquare is not None:
                    Color(*MarginColorNormal) #Draw Margin of start point
                    Rectangle(pos=LastStartSquarePos,size=RectSize)
                    Color(*RectColorNormal) #Draw actual start point
                    Rectangle(pos=LastStartSquarePos,size=(SquareSize,SquareSize))
        else:
            with self.canvas:
                if foundSquare is not None and foundSquare["colored"]:
                    Color(*MarginColorToggled) #Draw Margin of start point
                    Rectangle(pos=LastEndSquarePos,size=RectSize)
                    Color(*RectColorToggled) #Draw actual start point
                    Rectangle(pos=LastEndSquarePos,size=(SquareSize,SquareSize))
                elif foundSquare is not None:
                    Color(*MarginColorNormal) #Draw Margin of start point
                    Rectangle(pos=LastEndSquarePos,size=RectSize)
                    Color(*RectColorNormal) #Draw actual start point
                    Rectangle(pos=LastEndSquarePos,size=(SquareSize,SquareSize))
            
    

def drawGrid(self, width, height):
    global SquareList
    for x in range(0, int(ceil(width / SquareSize))):
        for y in range(0, int(ceil(height / SquareSize)) + 1):
            with self.canvas:
                testSquare = findSquare((x * SquareSize * 3 / 2, y * SquareSize * 3 / 2), True)  # Make sure there isn't already a square at the given coordinates
                if testSquare is None:
                    Color(*MarginColorNormal)
                    SquareList.append({"pos":Point(x * (SquareSize + MarginSize), y * (SquareSize + MarginSize)), "size":Point(*RectSize), "colored":False})
                    # Add a square to the given location (Margin included)
                    Rectangle(pos=(x * (SquareSize + MarginSize), y * (SquareSize + MarginSize)), size=RectSize)
                    Color(*RectColorNormal)
                    Rectangle(pos=(x * (SquareSize + MarginSize), y * (SquareSize + MarginSize)), size=(SquareSize, SquareSize))
                    # Draw the actual rectangle

Builder.load_string('''  
<test>:
    Label:
        text: "Hi!"
''')         # used for accessing .kv file for manual editing of various class attributes          

class GridWidget(Widget):
    def __init__(self, **kwargs):
        super(GridWidget, self).__init__(**kwargs)  # Don't ask why you need this line. You just do.
        global StartSquarePos,EndSquarePos
        rawStartCoord=Window.width/3 #Put it 1/3 the way in visual space horizontally
        rawEndCoord=Window.width*2/3 #Same as above, but 2/3 horizontally
        rawHeight=Window.height/2 #Put both halfway in visual space
        StartSquarePos=Point(*getSquareCoords((rawStartCoord,rawHeight)))
        EndSquarePos=Point(*getSquareCoords((rawEndCoord,rawHeight)))
        if ManualMonitorSize is None:
            drawGrid(self, Window.width, Window.height)  # Use the window size if a resolution is not provided
        else:
            drawGrid(self, *ManualMonitorSize)  # Otherwise, use the window size given.
        drawStartAndEnd(self)
        
        
    def on_touch_down(self, touch):
        global lastColor,GrabbedEndPoint
        if getSquareCoords(touch.pos)==StartSquarePos:
            GrabbedEndPoint=True
        elif getSquareCoords(touch.pos)==EndSquarePos:
            GrabbedEndPoint=False
        foundSquare = findSquare(touch.pos, True)
        if foundSquare is not None:
            lastColor = not foundSquare["colored"]  # This mimics Pathfinding.js's behavior.
        # It's a bit awkward because I had two nearly identical functions, which I made into one, so this logic had to be put here.
        if GrabbedEndPoint is None:
            updateRect(self, touch, True, foundSquare)  # The foundSquare is given so it doesn't have to search for it twice.
        drawStartAndEnd(self) #The start and end points always go over everything!

    def on_touch_move(self, touch):
        if GrabbedEndPoint is not None:
            updateStartAndEnd(self,touch)
        else:
            updateRect(self, touch, False, None)
        drawStartAndEnd(self)

    def on_touch_up(self, touch):
        global GrabbedEndPoint
        GrabbedEndPoint=None
#This will eventually be used for the buttons to switch the algorithm or start pathfinding using RelativeLayout

'''class myLayout(BoxLayout):     #Lays out two buttons horizontally, takes up entire window
    def __init__(self, **kwargs):
        super(myLayout, self).__init__(**kwargs)   #Still don't know why you need this, but you do.
        
        btn1 = Button(text="Place Start Point",       #Button 1 for start point
                       background_color=(0, 2, 0, 1))
        btn2 = Button(text="Place End Point",         #Button 2 for end point
                       background_color=(1, 0, 2, 1))
        btn1.bind(on_press=self.clk)   #Runs clk on mouse down
        btn2.bind(on_press=self.clk)
        self.add_widget(btn1)
        self.add_widget(btn2)
       
    def clk(self, obj):     #clk should allow a special point to appear that can be dragged
        print("Hello!")
''' 


class Grid(App):
    def build(self):
        return GridWidget()

if __name__ == "__main__":
    Grid().run()
