from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from collections import namedtuple
from collections import deque
from kivy.graphics import *
from math import sqrt
#We'll import these when they're needed.
#from kivy.uix.button import Button
#from kivy.uix.relativelayout import RelativeLayout
#from kivy.uix.splitter import Splitter

SquareSize = 32  #Size of each Square
MarginSize = 2  #Size of space between the Squares
SquareList = []
Point = namedtuple("Point", "x y")
lastSquare = {"pos": (0, 0), "size": (0, 0), "colored": False}  #Not as pretty as a Lua table, but it works.
lastColor = True

#The color format is in RGB, 1 being 255, 0 being 0.
StartSquarePos = None  #Position values are set when App builds and runs, based on window size. 
EndSquarePos = None
LastStartSquarePos = None
LastEndSquarePos = None
#rgb values in tuples for various rectangle states
StartColorNormal = (0, 1, 0)
StartColorMargin = (0, .75, 1)
EndColorNormal = (1, 0, 0)
EndColorMargin = (0, .75, 1)
MarginColorNormal = (0, .75, 1)
MarginColorToggled = (.5, .5, .5)
RectColorToggled = (.4, .4, .4)
RectColorNormal = (1, 1, 1)
RectSize = (SquareSize + MarginSize, SquareSize + MarginSize)
GrabbedEndPoint = None  #True for start, False for end, None for neither
ManualMonitorSize = (1600,1200)  #Size of your monitor, so when the window is maximized, the grid will scale.
#Set to None if you want it to just use the default window size
#1600x1200 is a high enough resolution that the grid fills a 17" diagonal laptop monitor


def findSquare(pos, allowRepeats):  #Finds the Square at the given coords
    global lastSquare
    for i in SquareList:
        if i["pos"].x < pos[0] <= i["pos"].x + i["size"].x and i["pos"].y <= pos[1] < i["pos"].y + i["size"].y and (
                i != lastSquare or allowRepeats):
            lastSquare = i
            return i


def getSquareCoords(pos):    #finds x, y of a square's center position
    return pos[0] - pos[0] % (MarginSize + SquareSize), pos[1] - pos[1] % (MarginSize + SquareSize)


def updateRect(self, touch, isTouchDown, foundSquare):
    if foundSquare is None:
        foundSquare = findSquare(touch.pos, isTouchDown)
    if foundSquare is not None and StartSquarePos != foundSquare["pos"] != EndSquarePos:  #If it found a NEW square
        foundSquare["colored"] = lastColor  #Color them the same color as the one from on_touch_down
        with self.canvas:  #Re-draw the rectangle to be changed
            if foundSquare["colored"]:
                Color(*MarginColorToggled)  #Unpack the tuple the color is stored in
            else:
                Color(*MarginColorNormal)
            Rectangle(pos=(foundSquare["pos"].x, foundSquare["pos"].y),
                      size=(foundSquare["size"].x, foundSquare["size"].y))
            #Draw the margins of the rectangle
            if foundSquare["colored"]:
                Color(*RectColorToggled)
            else:
                Color(*RectColorNormal)
            Rectangle(pos=(foundSquare["pos"].x, foundSquare["pos"].y),
                      size=(foundSquare["size"].x - MarginSize, foundSquare["size"].y - MarginSize))
            #Draw the actual rectangle


def drawStartAndEnd(self):
    global LastStartSquarePos, LastEndSquarePos
    with self.canvas:
        Color(*StartColorMargin)  #Draw Margin of start point
        Rectangle(pos=StartSquarePos, size=RectSize)
        Color(*StartColorNormal)  #Draw actual start point
        Rectangle(pos=StartSquarePos, size=(SquareSize, SquareSize))
        Color(*EndColorMargin)  #Draw Margin of end point
        Rectangle(pos=EndSquarePos, size=RectSize)
        Color(*EndColorNormal)  #Draw actual end point
        Rectangle(pos=EndSquarePos, size=(SquareSize, SquareSize))
    if GrabbedEndPoint is not None:
        if GrabbedEndPoint:  #Save the location of the last start/end point so you can re-draw the rectangle underneath
            LastStartSquarePos = StartSquarePos
        else:
            LastEndSquarePos = EndSquarePos


def updateStartAndEnd(self, touch):
    global StartSquarePos, EndSquarePos
    foundSquare = findSquare(touch.pos, False)
    if foundSquare is not None and not foundSquare["colored"]:  #Don't put the start/end point on a colored square
        if GrabbedEndPoint and foundSquare["pos"] != EndSquarePos:
            StartSquarePos = getSquareCoords(touch.pos)
        elif not GrabbedEndPoint and foundSquare["pos"] != StartSquarePos:
            EndSquarePos = getSquareCoords(touch.pos)
    if GrabbedEndPoint is not None:  #Re-draw the rectangle misplaced by the start/end point last time it moved
        if GrabbedEndPoint:
            with self.canvas:
                if foundSquare is not None and foundSquare["colored"]:
                    Color(*MarginColorToggled)  #Draw Margin of start point
                    Rectangle(pos=LastStartSquarePos, size=RectSize)
                    Color(*RectColorToggled)  #Draw actual start point
                    Rectangle(pos=LastStartSquarePos, size=(SquareSize, SquareSize))
                elif foundSquare is not None:
                    Color(*MarginColorNormal)  #Draw Margin of start point
                    Rectangle(pos=LastStartSquarePos, size=RectSize)
                    Color(*RectColorNormal)  #Draw actual start point
                    Rectangle(pos=LastStartSquarePos, size=(SquareSize, SquareSize))
        else:
            with self.canvas:
                if foundSquare is not None and foundSquare["colored"]:
                    Color(*MarginColorToggled)  #Draw Margin of start point
                    Rectangle(pos=LastEndSquarePos, size=RectSize)
                    Color(*RectColorToggled)  #Draw actual start point
                    Rectangle(pos=LastEndSquarePos, size=(SquareSize, SquareSize))
                elif foundSquare is not None:
                    Color(*MarginColorNormal)  #Draw Margin of start point
                    Rectangle(pos=LastEndSquarePos, size=RectSize)
                    Color(*RectColorNormal)  #Draw actual start point
                    Rectangle(pos=LastEndSquarePos, size=(SquareSize, SquareSize))


def drawGrid(self, width, height):
    global SquareList
    for x in range(0, int(width / SquareSize)):
        for y in range(0, int(height / SquareSize)):
            with self.canvas:
                testSquare = findSquare((x * SquareSize * 3 / 2, y * SquareSize * 3 / 2),
                                        True)  #Make sure there isn't already a square at the given coordinates
                if testSquare is None:
                    Color(*MarginColorNormal)
                    SquareList.append({"pos": Point(x * (SquareSize + MarginSize), y * (SquareSize + MarginSize)),
                                       "size": Point(*RectSize), "colored": False})
                    #Add a square to the given location (Margin included)
                    Rectangle(pos=(x * (SquareSize + MarginSize), y * (SquareSize + MarginSize)), size=RectSize)
                    Color(*RectColorNormal)
                    Rectangle(pos=(x * (SquareSize + MarginSize), y * (SquareSize + MarginSize)),
                              size=(SquareSize, SquareSize))
                    #Draw the actual rectangle


class AStar:            #this class will generate the optimal path between two points using heuristics
    def distBetween(self,current,neighbor):     #helps to choose neighboring square that is closest to goal
        return sqrt((current.x - neighbor.x)**2 + (current.y - neighbor.y)**2)

    def heuristicEstimate(self,start,goal):     #euclidean heuristic; focuses on shorter path but runs longer
        dx = abs(start.x - goal.x)
        dy = abs(start.y - goal.y)
        return (dx + dy) + (sqrt(2) - 2) * min(dx, dy)

    def neighborNodes(self,current):   #pass must be replaced with code
        pass
    
    def constructPath(self,cameFrom,goal):    #generates path from most recent neighbor
        path = deque()  #double-ended queue; can pop values on either end
        node = goal
        path.appendleft(node)
        while node in cameFrom:     #keep track of nodes already reached
            node = cameFrom[node]
            path.appendleft(node)
        return path
    
    def getLowest(self,openSet,fScore):     #compares distances and selects shortest path
        lowest = float("inf")
        lowestNode = None
        for node in openSet:
            if fScore[node] < lowest:
                lowest = fScore[node]
                lowestNode = node
        return lowestNode

    def aStar(self,start,goal):     #updates sets and continues to compare paths between neighbors
        cameFrom = {}
        openSet = set([start])
        closedSet = set()
        gScore = {} #distance of square from start node
        fScore = {} #distance of square from end node
        gScore[start] = 0
        #heuristic estimates the straight line distance between start and goal
        fScore[start] = gScore[start] + self.heuristicEstimate(start,goal)
        while len(openSet) != 0:
            current = self.getLowest(openSet,fScore)
            if current == goal:
                return self.constructPath(cameFrom,goal)
            openSet.remove(current)     #when node is reached, added to closedSet
            closedSet.add(current)      #and removed from openSet
            #compares gScore, fScore to select nodes closest to goal
            for neighbor in self.neighborNodes(current):
                tentative_gScore = gScore[current] + self.distBetween(current,neighbor)
                if neighbor in closedSet and tentative_gScore >= gScore[neighbor]:
                    continue
                if neighbor not in closedSet or tentative_gScore < gScore[neighbor]:
                    cameFrom[neighbor] = current
                    gScore[neighbor] = tentative_gScore
                    fScore[neighbor] = gScore[neighbor] + self.heuristicEstimate(neighbor,goal)
                    if neighbor not in openSet:
                        openSet.add(neighbor)
        return 0


class GridWidget(Widget):
    def __init__(self, **kwargs):
        super(GridWidget, self).__init__(**kwargs)  #Don't ask why you need this line. You just do.
        
        global StartSquarePos, EndSquarePos
        rawStartCoord = Window.width / 3  #Put it 1/3 the way in visual space horizontally
        rawEndCoord = Window.width * 2 / 3  #Same as above, but 2/3 horizontally
        rawHeight = Window.height / 2  #Put both halfway in visual space
        StartSquarePos = getSquareCoords((rawStartCoord, rawHeight))
        EndSquarePos = getSquareCoords((rawEndCoord, rawHeight))
        if ManualMonitorSize is None:
            drawGrid(self, Window.width, Window.height)  #Use the window size if a resolution is not provided
        else:
            drawGrid(self, *ManualMonitorSize)  #Otherwise, use the window size given.
        drawStartAndEnd(self)
        

    def on_touch_down(self, touch):
        global lastColor, GrabbedEndPoint
        if getSquareCoords(touch.pos) == StartSquarePos:  #If the start point was clicked on.
            GrabbedEndPoint = True
        elif getSquareCoords(touch.pos) == EndSquarePos:  #If the end point was clicked on.
            GrabbedEndPoint = False

        foundSquare = findSquare(touch.pos, True)
        if foundSquare is not None:
            lastColor = not foundSquare["colored"]  #This mimics Pathfinding.js's behavior.

        if GrabbedEndPoint is None:
            updateRect(self, touch, True,
                       foundSquare)  #The foundSquare is given so it doesn't have to search for it twice.
        drawStartAndEnd(self)  #The start and end points always must be drawn.

    def on_touch_move(self, touch):
        if GrabbedEndPoint is not None:
            updateStartAndEnd(self, touch)  #If you're moving the start/end point
        else:
            updateRect(self, touch, False, None)  #If you're changing the color of rectangle(s)
        drawStartAndEnd(self)

    def on_touch_up(self, touch):
        global GrabbedEndPoint  #Resets var so the program doesn't assume the start/end point is grabbed.
        GrabbedEndPoint = None


class Grid(App):
    def build(self):
        #The following segment of code was supposed to overlay buttons on top as child widgets, but
        #this did not work because of the way GridWidget was written; we will discuss this later.
            '''GridWidget.add_widget(GridWidget(), Button(size = (100,75), 
                         pos = (50, 50),                #the GridWidget is the parent widget and the Buttons
                         text = "A* Search",            #exist as its children and should spawn only when
                         color = (0, 1, 0, 1),          #GridWidget is built
                         font_size = 45), index = 0, canvas = 'after')
            GridWidget.add_widget(GridWidget(), Button(size = (100,75),
                         pos = (50, 40),
                         text = "Best-First Search",
                         color = (1, 1, 0, 1),
                         font_size = 45), index = 1, canvas = 'after')'''
            return GridWidget()


if __name__ == "__main__":
    Grid().run()
