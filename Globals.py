from datetime import date


PrimaryColor = []
redraw = []
randomImagesCallback = []
onlineCallback = []
config = None
tabview = None
online = False
randomImages = False
eventCallbacks=[]
def eventCreationListener(event):
    eventDate=date(event.start.year,event.start.month,event.start.day)
    if not eventDate in eventList:
        eventList[eventDate]=[]
    eventList[eventDate].append(event)
    eventList[eventDate].sort(lambda a,b: a.start<b.start)
    for i in eventCallbacks:
        i(eventList,event)
eventList = {}
images = {
    8: ["https://www.colourbox.com/preview/5665824-a-school-building.jpg",
        "http://cache-blog.credit.com/wp-content/uploads/2013/04/student-loans-ts-1360x860.jpg",
        "https://lh3.googleusercontent.com/-wrtKyuFuGH8/VifauF9--7I/AAAAAAAAAF0/0yBwTZCpD60/w1000-h1000/Pepe_rare.png",
        "https://pbs.twimg.com/profile_images/565528824289300480/wIGnl73l.jpeg"]
}