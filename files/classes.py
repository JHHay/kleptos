from pygame import mixer
from time import sleep
from sys import stdout, path
from os import system, name
path.append("../lib/")
path.append("../lib/keywords/")
path.append("../lib/events/")

class Display(object):

    def __init__(self):
        self.clearStatus()
        self.room = ""
        self.visibility = 0
        self.inventory = []
        
        # Graphics:

        # xairete (Goodbye)
        xairete = open("lib/xairete", "r")
        self.xairete = []
        for line in xairete:
            self.xairete.append(line[:-1])

        # The splash (title) screen:
        splash = open("lib/splash", "r")
        self.splash = []
        for line in splash:
            self.splash.append(line[:-1])

        # The skull
        skull =  open("lib/skull", "r")
        self.skull = []
        for line in skull:
            self.skull.append(line[:-1])

        # The ending graphics:
        eurekas = open("lib/eurekas", "r")
        self.eurekas = []
        for line in eurekas:
            self.eurekas.append(line[:-1])

        mixer.init()

    def clearStatus(self):
        self.status = [" ", " ", " ", " ", " "]

    # For playing sounds
    def play(self, wav):                       
        mixer.Sound(wav).play()

    def updateAll(self, title, room, status, visibility, inventory):
        self.title = title
        self.room = room
        self.updateStatus(status)
        self.visibility = visibility
        self.inventory = inventory

    def updateStatus(self, status):
        del self.status[0]
        self.status.append(status)

    def updateVis(self, vis):
        self.visibility = vis

    def updateInv(self, inv):
        self.inventory = inv

    def updateRoom(self, room):
        self.room = room

    def updateTitle(self, title):
        self.title = title

    def __cls(self):
        system(['clear','cls'][name == 'nt'])

    def printStatus(self):
        for i in range(len(self.status)-1):
            print self.status[i]
        self.type(self.status[4])

    def refresh(self):
        self.__cls()
        print "Current Room: " + self.title
        print "-" * 100
        print self.room
        print "-" * 100
        print "Visibility: %d%%     Inventory: " % self.visibility,
        for i in self.inventory:
            print i,
        print
        print "-" * 100
        print "Recent Events:"
        print
        self.printStatus()
        print
        
    def type(self, string):
        for char in string:
            stdout.write(char)
            stdout.flush()
            self.play('pluck.wav')
            if char == "." or char == "," or char == ":":
                sleep(.25)
            else:
                sleep(.04)
            
        print

    def textscreen(self, text):
        self.__cls()
        for line in text:
            print line
        print "\n\n"
        print "Press ENTER to continue..."

    def loseScreen(self):
        self.__cls()
        print "\n"
        for line in self.skull:
            print line
        print "\n\n"
        self.type("You got caught! Sadly, there will be no trial for a foreign vagabond...")
        self.type("Try again? (yes/no)")

    def winScreen(self):
        self.__cls()
        print "\n"
        for line in self.eurekas:
            print line
        print "\n\n"
        self.type("Eurekas! You found it!")
        self.type("Press ENTER to continue...")

    def ending(self, ending):
        self.__cls()
        for line in ending:
            self.type(line)
        print
        self.type("Would you like to play again?")

    def quitScreen(self):
        self.__cls()
        for line in self.xairete:
            print line
        print
        print

    def splashScreen(self):
        self.__cls()
        for line in self.splash:
            print line
        print
        print
        self.type("Press ENTER to begin!")

class Library(object):

    def __init__(self):

        # Reads all files, plus integer determining read request (see __read)
        # and stores them in a master dictionary
        self.master = {}
        self.master["intro"] = self.__read("lib/intro", 1)
        self.master["backstory"] = self.__read("lib/backstory", 1)
        self.master["gamehelp"] = self.__read("lib/gamehelp", 1)
        self.master["glossary"] = self.__read("lib/glossary", 1)
        self.master["rooms"] = self.__read("lib/rooms", 2)
        self.master["general_verbs"] = self.__read("lib/keywords/general_verbs", 1)
        self.master["item_verbs"] = self.__read("lib/keywords/item_verbs", 3)
        self.master["room_objects"] = self.__read("lib/keywords/room_objects", 3)
        self.master["items"] = self.__read("lib/keywords/items", 2)
        self.master["switchObjects"] = self.__read("lib/keywords/switchObjects", 2)
        self.master["roomMap"] = self.__read("lib/roomMap", 2)
        self.master["ending"] = self.__read("lib/ending", 1)

        # Makes the eventBook, the library of all possible commands and outcomes
        # for each room in the house
        self.master["eventBook"] = {}
        for room in self.master["rooms"].iterkeys():
            self.master["eventBook"][room] = self.make_eventMap(room)

    def access(self, key):
        return self.master[key]

    def make_eventMap(self, filename):
        # Finds a file in the event folder (all are named after Rooms)
        #     Map is dict with keys as strings containing possible commands,
        #     items as lists with el. 0 being an output string and el. 1 being possible results,
        #     which might need to be split
        eventMap = self.__read("lib/events/"+filename, 4)
        for k in eventMap.iterkeys():
            if " " in eventMap[k][1]:
                eventMap[k][1] = eventMap[k][1].split(" ")
        return eventMap

    def __read(self, filename, package):
        # Returns the contents of a file, packaged based on parameter(integer):
        # 0 returns a raw file object
        # 1 returns a list
        # 2 returns a dictionary with every other line being a key to the next line
        # 3 same as 2, but item is a list created with .split(' ')
        # 4 reads file in groups of four lines, with the following results:
        #                   Line 1 = key
        #                   Line 2 = element 0 of item, which is a list
        #                   Line 3 = element 1 of item, which is a list
        #                   Line 4 = ignored
        
        readfile = open(filename, "r")

        lines = []
        for line in readfile.readlines():
            if line[-1] == "\n":
                lines.append(line[:-1])
            else:
                lines.append(line)
        if package == 1:
            return lines
        elif package == 2 or package == 3:
            myMap = {}
            keys = []
            items = []
            for i in range(len(lines)):

                if i%2==0:
                    keys.append(lines[i])
                else:
                        
                    if package == 3:
                        subitems = []
                        for j in lines[i].split(" "):
                           subitems.append(j)
                        items.append(subitems)
                    else:
                        items.append(lines[i])
                
            for k in range(len(keys)):
                myMap[keys[k]] = items[k]
            return myMap
        elif package == 4:
            myMap = {}
            keys = []
            strings = []
            actions = []
            for l in range(len(lines)):
                if l%4==0:
                    keys.append(lines[l])    # putting command phrases into keys[]
                elif l%4==1:
                    strings.append(lines[l])   # putting the result string into strings[]
                elif l%4==2:
                    actions.append(lines[l]) # putting the action(s) into actions[]
                else:
                    continue                 # ignoring the blank lines
            for j in range(len(keys)):
                myMap[keys[j]] = [strings[j], actions[j]]
            return myMap
                    
        else:
            print "Improper package for __read"

class Parser(object):

    def __init__(self, gameOptions, verblist):
        self.gameOptions = gameOptions
        self.verbs = verblist

    # Takes input gathered by Runner(),
    # along with a relevant eventMap,
    # determines if it is a valid command and returns an action
    def parse(self, cmd, eventMap, newVerblist, newObjectlist):
        objectlist = newObjectlist
        # Update verb list
        self.verbs = newVerblist
        if cmd == "wait":
            return "actions", "wait"
        elif cmd in self.gameOptions:
            return "gameOptions", cmd
        elif " " in cmd:
            # If command is not wait, chop up the command into separate words
            words = cmd.split(" ")
            # The first word is the verb
            verb = words[0]
            obj = words[1]
            if cmd in eventMap and verb in self.verbs and obj in objectlist:
                return "actions", "action"
            elif not verb in self.verbs:
                return "actions", "badVerb"
            else:
                return "actions", "badInput"     # Doesn't understand user
        else:
            return "actions", "badInput"

class House(object):

    def __init__(self, roomBook, roomMap, eventBook, objectBook):
        self.roomBook = roomBook
        self.rooms = {}
        for page in self.roomBook.iterkeys():
            self.rooms[page] = Room(page, self.roomBook[page], eventBook[page], objectBook[page])

        # A list of rooms with their access codes
        self.roomMap = roomMap

        # A list of the default "openness" of all the rooms. True = open, false = closed ('locked')
        self.roomLocks =  {"00":True,
                           "01":False,
                           "02":False,
                           "03":True,
                           "04":False,
                           "05":True,
                           "06":True,
                           "07":True,
                           "08":False,
                           "09":False}

    def describe(self, key):
        return self.rooms[key].describe()

    def getEvents(self, key):
        return self.rooms[key].shareEvents()

    def getRoom(self, key):
        return self.roomMap[key]

    def getLock(self, key):
        return self.roomLocks[key]

    def unlock(self, key):
        self.roomLocks[key] = 1

    def getObjects(self, key):
        return self.rooms[key].shareObjects()

class Room(object):

    def __init__(self, name, description, eventMap, objectDict):
        self.name = name
        self.description = description
        self.eventMap = eventMap
        self.objects = objectDict
        
    def describe(self):
        return self.description

    def shareEvents(self):
        return self.eventMap

    def shareObjects(self):
        return self.objects     
