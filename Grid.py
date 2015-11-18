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
                lowest
