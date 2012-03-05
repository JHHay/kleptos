from classes import *
from time import sleep

STARTING_VISIBILITY = 0
STARTING_INVENTORY = ["dagger", "coins"]
STARTING_ROOM = "Alley"

class Runner(object):

    def __init__(self):

        self.gameOptions = {"help":self.__help, 
                            "quit":self.__quit, 
                            "backstory":self.__backstory,
                            "intro":self.__intro, 
                            "glossary":self.__glossary, 
                            "commands":self.__commands, 
                            "objects":self.__objects,
                            "bellerophon":self.__win} # a cheat code - instant win!

        self.actions = {"newRoom":self.__newRoom, 
                        "changeVis":self.__changeVis, 
                        "getItem":self.__getItem,
                        "win":self.__win,
                        "lose":self.__lose, 
                        "noAction":self.__noAction, 
                        "badInput":self.__badInput, 
                        "badVerb":self.__badVerb, 
                        "unlockRoom":self.__unlockRoom, 
                        "activateObject":self.__activateObject, 
                        "loseItem":self.__loseItem,
                        "deactivateObject":self.__deactivateObject, 
                        "killObject":self.__killObject,
                        "wait":self.__wait}

        self.choiceGroups = {"gameOptions": self.gameOptions, "actions": self.actions}

        self.Library = Library()
        self.roomBook = self.Library.access("rooms")
        self.eventBook = self.Library.access("eventBook")
        self.objectBook = self.Library.access("room_objects")
        self.verblist = self.Library.access("general_verbs")
        self.item_verbs = self.Library.access("item_verbs")
        self.roomMap = self.Library.access("roomMap")
        self.items = self.Library.access("items")
        self.switchObjects = self.Library.access("switchObjects")

        self.Parser = Parser(self.gameOptions.keys(), self.verblist)
        self.House = House(self.roomBook, self.roomMap, self.eventBook, self.objectBook)
        
        self.visibility = STARTING_VISIBILITY
        self.inventory = []
        for item in STARTING_INVENTORY:
            self.inventory.append(item)
        self.activeRoom = STARTING_ROOM

        self.objectlist = self.House.getObjects(self.activeRoom) + self.inventory

        self.Screen = Display()

        self.Screen.splashScreen()
        raw_input()

        self.Screen.updateAll(self.activeRoom, self.House.describe(self.activeRoom), "", self.visibility, self.inventory)

        # Main game loop
        playOn = True
        while playOn:
            self.Screen.refresh()
            playOn = self.__getCommand()
            if self.visibility >= 100:       # Did we make too many mistakes?
                self.__lose()
            else:
                continue
        self.Screen.quitScreen()

    # Interface / Story options:

    def __prompt(self):
        cmd = raw_input("> ")
        return cmd

    def __quit(self):
        return False

    def __getCommand(self):
        eventMap = self.Library.make_eventMap(self.activeRoom)
        
        #update verblist - adds commands for items in inv, cleans up commands from lost items

        for key in self.item_verbs.iterkeys():
            if key in self.inventory:
                for verb in self.item_verbs[key]:
                    if not verb in self.verblist:
                        self.verblist.append(verb)
                    else:
                        continue
            else:
                for verb in self.item_verbs[key]:
                    if verb in self.verblist:
                        self.verblist.remove(verb)
                    else:
                        continue

        userText = self.__prompt()
        choiceGroup, cmd = self.Parser.parse(userText, eventMap, self.verblist, self.objectlist)

        #If parser says that this is a game action by returning "action,"
        #Runner then uses the eventMap to get further instructions
        if cmd == "action":
            actionBundle = eventMap[userText]
            if isinstance(actionBundle[1], list):
                actionPair = [actionBundle[0], actionBundle[1][0]]
                extraActions = actionBundle[1][1:]
                for action in extraActions:
                    print action
                    value = action[-3:-1]
                    action = action[:-3]
                    self.choiceGroups[choiceGroup][action](value)
            else:
                actionPair = actionBundle
            print actionPair
            if actionPair[1][-1] == "#":      # if command is "changeVis", "newRoom", "unlockRoom" or "getItem"
                shavedKey = actionPair[1][:-3]
                value = actionPair[1][-3:-1]
                actionPair[1] = shavedKey
                
                #Filters for items already picked up (if) locked doors (elif)
                if actionPair[1][0] == "g" and self.__haveItem(value):
                    self.Screen.updateStatus("You already have that item.")
                    return self.__noAction()
                elif actionPair[1][0] == "n" and not self.__doorUnlocked(value):
                    self.Screen.updateStatus("You can't go there yet.")
                    return self.__noAction()
                elif actionPair[1][0] == "u" and self.__doorUnlocked(value):
                    self.Screen.updateStatus("The way is already open.")
                    return self.__noAction()
                else:
                    self.Screen.updateStatus(actionPair[0])
                    return self.choiceGroups[choiceGroup][actionPair[1]](value)
            else:
                self.Screen.updateStatus(actionPair[0])
                return self.choiceGroups[choiceGroup][actionPair[1]]()
                              
        else:
            return self.choiceGroups[choiceGroup][cmd]()
        
    def __help(self):
        self.Screen.textscreen(self.Library.master["gamehelp"])
        raw_input()
        return True

    def __backstory(self):
        self.Screen.textscreen(self.Library.master["backstory"])
        raw_input()
        return True

    def __intro(self):
        self.Screen.textscreen(self.Library.master["intro"])
        raw_input()
        return True

    def __glossary(self):
        self.Screen.textscreen(self.Library.master["glossary"])
        raw_input()
        return True

    # In-game actions

    def __newRoom(self, value):
        if not self.House.getLock(value):
            return True
        else:
            self.Screen.refresh()                # To display the status update
            self.activeRoom = self.House.getRoom(value)
            self.objectlist = self.House.getObjects(self.activeRoom)
            for item in self.inventory:
                if item not in self.objectlist:
                    self.objectlist.append(item)
                else:
                    continue
            self.Screen.updateTitle(self.activeRoom)
            self.Screen.updateRoom(self.House.describe(self.activeRoom))
            self.Screen.clearStatus()
            sleep(.75)
            return True
    
    def __changeVis(self, value):
        self.visibility += int(value)
        self.Screen.updateVis(self.visibility)
        return True
     
    def __getItem(self, value):
        self.inventory.append(self.items[value])
        self.Screen.updateInv(self.inventory)
        return True

    def __loseItem(self, value):
        self.inventory.remove(self.items[value])
        if self.items[value] in self.objectlist:
            self.objectlist.remove(self.items[value])
        self.Screen.updateInv(self.inventory)
        return True

    def __lose(self):
        self.Screen.refresh()
        sleep(2)
        self.Screen.loseScreen()
        return self.__playAgain()

    def __playAgain(self):
        cmd = 0
        while True:
            cmd = self.__prompt()
            if cmd == "yes" or cmd == "y": 
                self.__reset()
                return True
            elif cmd == "no" or cmd == "n":
                return False

    def __reset(self):
        self.visibility = STARTING_VISIBILITY
        self.activeRoom = STARTING_ROOM
        self.inventory = []
        for item in STARTING_INVENTORY:
            self.inventory.append(item)
        self.objectlist = self.House.getObjects(self.activeRoom) + self.inventory
        self.Screen.clearStatus()
        self.Screen.updateAll(self.activeRoom, self.House.describe(self.activeRoom), "", self.visibility, self.inventory)

    def __noAction(self):
        return True

    def __badInput(self):
        self.Screen.updateStatus("That is not a valid command.")
        return True

    def __unlockRoom(self, value):
        self.House.unlock(value)
        return True

    def __haveItem(self, value):
        if self.items[value] in self.inventory:
            return True
        else:
            return False

    def __doorUnlocked(self, value):
       return self.House.getLock(value)

    def __badVerb(self):
        self.Screen.updateStatus("You can't do that.")
        return True

    def __commands(self):
        verbstring = ""
        for item in self.verblist:
            verbstring += " " + item
        self.Screen.updateStatus("Possible commands:" + verbstring)
        return True

    def __objects(self):
        objectstring = ""
        for item in self.objectlist:
            if item not in self.inventory:
                objectstring += " " + item
            else:
                continue
        self.Screen.updateStatus("Relevant objects:" + objectstring)
        return True

    def __activateObject(self, value):
        self.objectlist.append(self.switchObjects[value])
        return True

    def __deactivateObject(self, value):
        self.objectlist.remove(self.switchObjects[value])
        return True

    def __killObject(self, value):
        del self.switchObjects[value]
        return True

    def __wait(self):
        self.Screen.updateStatus("You do nothing. Time is running out!")
        return True

    def __win(self):
        self.Screen.refresh()
        sleep(2)
        self.Screen.winScreen()
        raw_input()
        self.Screen.ending(self.Library.master["ending"])
        return self.__playAgain()
