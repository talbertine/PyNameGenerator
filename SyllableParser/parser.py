import xml.etree.ElementTree as ET

parsers = {}
def getParser(langPath):
    global parsers
    if langPath not in parsers:
        parsers[langPath] = Parser(langPath)
    return parsers[langPath]

class Parser:
    def __init__(self, langPath):
        #Initialize variables
        self.syllables = set()
        self.memoDict = dict(); #memoization dictionary
    
        #Load syllable list
        tree = ET.parse(langPath)
        cRoot = tree.find(".//Graphemes")
        for child in cRoot:
            self.syllables.add(child.text.lower())
            
    def parseWord(self, word):
        """Parse a word into the longest matching graphemes"""
        # Start by adding the absolute base case that an empty string has no graphemes
        self.memoDict[""] = []
        # Call the helper function
        resultGraphemes = self._parseWord(word.lower())
        #Reset the memoization dictionary so we don't hog all the memory with things we may never see again
        self.memoDict.clear()
        
        return resultGraphemes
        
    def _parseWord(self, word):
        """Recursive helper function to parse a word into the longest matching graphemes"""
        # Base case
        if word in self.memoDict:
            return self.memoDict[word]
        prefix = word
        suffix = ""
        while len(prefix) > 0:
            if prefix in self.syllables: # first part is a valid grapheme
                suffixSyllables = self._parseWord(suffix)
                if suffixSyllables is not None: # second part is made of valid graphemes
                    # add it to the grapheme dictionary so we don't solve it again
                    self.memoDict[word] = [prefix] + suffixSyllables
                    return self.memoDict[word]
            #If the prefix wasn't a grapheme, or the suffix wasn't parseable into graphemes, shift a character from the prefix to the suffix, and try again
            suffix = prefix[-1] + suffix
            prefix = prefix[:-1]
        # We ran out of characters in the prefix trying to find a matching grapheme, so therefore it can't be parsed.
        return None
        