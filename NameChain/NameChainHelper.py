import xml.etree.ElementTree as ET
import random
import math

class BadFormat(Exception):
    def __init__(self, text):
        self.message = "Bad Format: " + text

class NameChainHelper:
    def __init__(self, history):
        self._history = history
        self._root = NameChainNode(self)
        self._patternDict = {self._root.getPattern(): self._root}
        self._seenWords = set()
        self.addWord([])
        
    def addWord(self, graphemes):
        word = "".join(graphemes)
        if word in self._seenWords:
            # don't double count words
            return
        self._seenWords.add(word)
        self._root.insert(self, graphemes)
        
    def getMostLikelyWord(self, lengthLimit=None):
        result = ""
        currentNode = self._root
        # While a length limit has not been reached
        while (lengthLimit is None or lengthLimit > 0):
            # Get the next node
            currentNode = self._getNodeByPattern(currentNode.getMostLikelySequel())
            if currentNode.isTerminator():
                return result
            else:
                result += currentNode.getPattern()[-1]
            if lengthLimit is not None:
                lengthLimit -= 1
        return result
        
        
    def getRandomWord(self, lengthLimit=None):
        result = ""
        currentNode = self._root
        # While a length limit has not been reached
        while (lengthLimit is None or lengthLimit > 0):
            # Get the next node
            currentNode = self._getNodeByPattern(currentNode.getRandomWeightedSequel())
            if currentNode.isTerminator():
                return result
            else:
                result += currentNode.getPattern()[-1]
            if lengthLimit is not None:
                lengthLimit -= 1
        return result
        
    def Save(self, path):
        #Root node
        root = ET.Element("NameGraph", {"history" : str(self._history)})
        #Seen Words
        seenList = list(self._seenWords)
        seenList.sort()
        for word in seenList:
            ET.SubElement(root, "SeenWord", {"word" : word})
        #Graph Nodes
        for _, node in self._patternDict.items():
            node.save(root)
        tree = ET.ElementTree(root)
        ET.indent(tree)
        tree.write(path)
        
    def Load(self, path):
        self.Clear()
        tree = ET.parse(path)
        #Root
        root = tree.getroot()
        self._history = int(root.attrib["history"])
        
        #Seen Words
        wordTags = root.findall("SeenWord")
        for wordTag in wordTags:
            self._seenWords.add(wordTag.attrib["word"])
            
        #Graph Nodes
        nodeTags = root.findall("GraphNode")
        for nodeTag in nodeTags:
            node = NameChainNode(self)  #Create a node
            node.load(nodeTag)          # load the data
            self._patternDict[node.getPattern()] = node #associate the node with it's pattern
        # update the root node
        self._root = self._patternDict[tuple("" for _ in range(self._history))]
    
    def getSeenWords(self):
        words = list(self._seenWords)
        words.sort()
        return words
        
    def Clear(self):
        self.__init__(self._history)
        
    def _getNodeByPattern(self, pattern):
        """
        _getNodeByPattern
        pattern: The text pattern indicated by the node, in terms of a sequence of graphemes
        """
        return self._patternDict[pattern]
    
    def _setNodeByPattern(self, pattern, node):
        if self._hasNodeWithPattern(pattern):
            raise "Trying to overwrite pattern"
        self._patternDict[pattern] = node
        
    def _hasNodeWithPattern(self, pattern):
        """
        _hasNodeWithPattern
        pattern: The text pattern indicated by the node, in terms of a sequence of graphemes
        """
        return pattern in self._patternDict
        
def patternToAttrDict(pattern):
    attributes = dict()
    for index, val in enumerate(pattern):
        string = val
        if string is None:
            string = "None"
        attributes["pattern" + str(index)] = string
    return attributes
    
def elementToPattern(element, history):
    result = [None for _ in range(history)]
    for key, value in element.attrib.items():
        if "pattern" in key:
            index = int(key[len("pattern"):])
            result[index] = value
            if value == "None":
                result[index] = None
    return tuple(result)
        
class NameChainNode:
    def __init__(self, nch, pattern = None):
        if pattern is None:
            pattern = tuple("" for _ in range(nch._history))
        self._pattern = pattern
        self._nextPatternCounts = dict()
    
    def getPattern(self):
        return self._pattern
        
    def isTerminator(self):
        return None in self._pattern
        
    def insert(self, nch, word):
        nextGrapheme = None #base case, if this is in a node's pattern, it must be a terminator
        if word != []:
            # add the next syllable on to the end of the pattern
            nextGrapheme = word[0]
        nextPattern = tuple(list(self._pattern[1:]) + [nextGrapheme])
        
        #If the node doesn't exist, create it
        if not nch._hasNodeWithPattern(nextPattern):
            nch._setNodeByPattern(nextPattern, NameChainNode(nch, nextPattern))
        
        #If this node doesn't know about the node, add that to our dictionary
        if nextPattern not in self._nextPatternCounts:
            self._nextPatternCounts[nextPattern] = 0
        
        #Now that we're sure it exists, increment it
        self._nextPatternCounts[nextPattern] += 1
        
        #If there's more string to process, feed it to the next Node
        if word != []:
            nch._getNodeByPattern(nextPattern).insert(nch, word[1:])
            
    def save(self, parentXml):
        attributes = patternToAttrDict(self._pattern)
        node = ET.SubElement(parentXml, "GraphNode", attributes)
        for pattern, count in self._nextPatternCounts.items():
            attributes = patternToAttrDict(pattern)
            attributes["count"] = str(count)
            ET.SubElement(node, "NextNode", attributes)
            
    def load(self, nodeXml):
        history = len(self._pattern)
        self._pattern = elementToPattern(nodeXml, history)
        leads = nodeXml.findall("NextNode")
        for lead in leads:
            pattern = elementToPattern(lead, history)
            self._nextPatternCounts[pattern] = int(lead.attrib["count"])
            
    def getMostLikelySequel(self):
        maxPattern = None
        maxVal = 0
        for pattern, count in self._nextPatternCounts.items():
            if count > maxVal:
                maxPattern = pattern
                maxVal = count
        return maxPattern
        
    def getRandomWeightedSequel(self):
        patterns = []
        weights = []
        for pattern, count in self._nextPatternCounts.items():
            patterns.append(pattern) 
            weights.append(count)
        return random.choices(patterns, weights)[0]
            