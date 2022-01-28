import SyllableParser as SP
import NameChain as NC
import constants
import sys
import os

shouldQuit = False
commandList = []
commandDict = dict()
currentLang = constants.DEFAULT_LANG_PATH
history = constants.DEFAULT_HISTORY_LENGTH
nameChain = NC.NameChain(history)


def main():
    global shouldQuit
    global commandList
    global commandDict
    commandList.append(Command("quit", 
        [], 
        [], 
        "Exits the program", 
        0, 
        ourQuit))
    commandList.append(Command("help", 
        ["helpTarget"], 
        ["The command to look up"], 
        "Produces documentation for a command", 
        0, 
        ourHelp)) 
    commandList.append(Command("?", 
        ["helpTarget"], 
        ["The command to look up"], 
        "Produces documentation for a command", 
        0, 
        ourHelp))
    commandList.append(Command("setlang", 
        ["langPath"],
        ["The path to the language orthography xml"],
        "Sets the current language for parsing into graphemes. Will clear the source contents in anticipation of reparsing",
        1,
        setLang))
    commandList.append(Command("getlang", 
        [],
        [],
        "Gets the path to the current language for parsing into graphemes.",
        0,
        getLang))
    commandList.append(Command("gethist",
        [],
        [],
        "Gets the length of the history to consider when distinguishing chains of graphemes",
        0,
        getHistory))
    commandList.append(Command("sethist",
        ["length"],
        ["number of graphemes to use when distinguishing sequences"],
        "Sets the length of the history to consider when distinguishing chains of graphemes. This will clear source contents, since the history effects the structure of the model",
        1,
        setHistory))
    commandList.append(Command("wordlist", 
        [],
        [],
        "Displays the words that are currently in the model",
        0,
        getSeenWords))
    commandList.append(Command("add", 
        ["word"],
        ["The word that should be added to the chains"],
        "Insert a word into the namechain model",
        1,
        addWord))
    commandList.append(Command("clear",
        [],
        [],
        "Remove all words from the model",
        0,
        clearWords))
    commandList.append(Command("addlist",
        ["listPath"],
        ["A path to the list of words to add to the model"],
        "Add a file of words to the list",
        1, 
        addWordList))
    commandList.append(Command("save",
        ["path"],
        ["The location where the model xml will be saved"],
        "Store the model so that you can recall it later without having to recreate it",
        1,
        save))
    commandList.append(Command("load", 
        ["path"],
        ["The location from which to load the model"],
        "Load a model you have saved",
        1,
        load))
    commandList.append(Command("get",
        ["type", "length"],
        ["one of \"likely\" or \"random\"", "the maximum number of graphemes in a generated word, or None if there should be no limit"],
        "Generate a word using the model",
        1,
        get))
    
    commandList.sort(key=lambda com:com.getName())
    for command in commandList:
        commandDict[command.getName()] = command

    print("NameGenerator version " + str(constants.VERSION))
    while not shouldQuit:
        command = input(">>> ").lower().split()
        if command == []:
            continue
        consoleInterpret(command[0], command[1:])

def consoleInterpret(command, args):
    if command not in commandDict:
        print("Command not found: " + command)
        return
    command = commandDict[command]
    numArgs = len(args)
    minArgs = command.getMinNumArgs()
    maxArgs = command.getMaxNumArgs()
    if numArgs < minArgs or numArgs > maxArgs:
        print("Invalid number of arguments. Expected " + str(minArgs) + "-" + str(maxArgs) + ". Got " + str(numArgs) + ".")
        return
    command.execute(args)
    
class Command:
    def __init__(self, name, args, argDoc, summary, mandatoryCount, function):
        self._name = name
        self._argList = [(args[i], argDoc[i], True if i < mandatoryCount else False) for i in range(len(args))]
        self._summary = summary
        self._function = function
        
    def getName(self):
        return self._name

    def execute(self, arguments):
        self._function(arguments)
    
    def getMaxNumArgs(self):
        return len(self._argList)
        
    def getMinNumArgs(self):
        count = 0
        for arg in self._argList:
            if arg[2]:
                count += 1
        return count
        
    def getSyntax(self):
        syntaxString = self._name
        for name, _, mandatory in self._argList:
            addString = name
            if not mandatory:
                addString = "<" + addString + ">"
            syntaxString += " " + addString
        return syntaxString
        
    def getHelp(self):
        helpString = self.getSyntax()
        helpString += "\n\n" + self._summary
        for name, desc, mandatory in self._argList:
            helpString += "\n\t" + name + ": " + desc
        return helpString
        
#### Commands ####
        
def ourQuit(args):
    global shouldQuit
    shouldQuit = True
    
def ourHelp(args):
    if len(args) == 0:
        # Get the command list
        for command in commandList:
            print(command.getSyntax())
    else:
        # Specific command
        print(commandDict[args[0]].getHelp())
        
def setLang(args):
    global currentLang
    global nameChain
    if not os.path.isfile(args[0]):
        print("No file found at " + args[0])
        return
    currentLang = args[0]
    # The graphemes are different, so for consistency, reset the name chains
    nameChain.Clear()
    
def getLang(args):
    print(currentLang)

def getHistory(args):
    print(str(history))
    
def setHistory(args):
    global history
    global nameChain
    num = int(args[0])
    if num < 1:
        print("History must be 1 or greater")
        return
    history = int(args[0])
    # 
    nameChain = NC.NameChain(history)
    
def getSeenWords(args):
    words = nameChain.getSeenWords()
    for word in words:
        print(word)
        
def addWord(args):
    graphemes = []
    try:
        graphemes = SP.stringToGraphemes(args[0], currentLang)
    except SP.UnrecognizedSyllable as e:
        print(e.message)
        return
    nameChain.addWord(graphemes)
    
def clearWords(args):
    nameChain.Clear()
    
def addWordList(args):
    try:
        with open(args[0], "r") as file:
            for line in file:
                line = line.split()
                for word in line:
                    graphemes = SP.stringToGraphemes(word)
                    nameChain.addWord(graphemes)
    except FileNotFoundError as e:
        print("No file found at " + args[0])
                
def save(args):
    nameChain.Save(args[0])
    
def load(args):
    if not os.path.isfile(args[0]):
        print("No file found at " + args[0])
        return
    nameChain.Load(args[0])
    
def get(args):
    limit = None
    if len(args) == 2:
        if args[1] == "none":
            limit = None
        else:
            try:
                limit = int(args[1])
            except ValueError as e:
                print(args[1] + " is not an integer")
                return
            if limit < 0:
                print("Limit should be nonnegative")
                return
    if args[0] == "likely":
        print(nameChain.getMostLikelyWord(limit))
    elif args[0] == "random":
        print(nameChain.getRandomWord(limit))
    else:
        print(args[0] + " is not one of \"likely\" or \"random\"")

main() 