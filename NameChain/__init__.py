import time
import random
import os
import NameChain.NameChainHelper as NCH

#Basically a wrapper to keep people from accidentally messing with the actual tree
class NameChain:
    def __init__(self, history=2, seed=time.time_ns()):
        """
        NameChain constructor:
        self: the instance
        history: how far back of a history should we consider for a pattern
        seed: The random seed to use to generate random words
        """
        self.nch = NCH.NameChainHelper(history)
        
        # create a random state just for us, but back up the parent's state
        parentRandState = random.getstate()
        random.seed(seed)
        self.randState = random.getstate()
        random.setstate(parentRandState)

    def addWord(self, graphemes):
        """
        Adds the word to the graph
        graphemes: an array of strings containing the word after having been broken down into graphemes
        """
        self.nch.addWord(graphemes)
        
    def getMostLikelyWord(self, lengthLimit=None):
        """
        Chooses the most likely word based on the source words grapheme frequency
        lengthLimit: In case the most common patterns form a cycle, this is the number of graphemes after which we will cut it off. 
        """
        return self.nch.getMostLikelyWord(lengthLimit)
        
    def getRandomWord(self, lengthLimit=None):
        """
        Chooses a random grapheme weighted by the number of times a pattern shows up.
        lengthLimit: If the pattern is going on too long, this is when we cut it off.
        """
        #backup random state
        parentRandState = random.getstate()
        random.setstate(self.randState)
        
        word = self.nch.getRandomWord(lengthLimit)
        
        #restor random state
        self.randState = random.getstate()
        random.setstate(parentRandState)
        
        return word
        
    def Save(self, path):
        """
        Save
        Store the results so we don't have to regenerate the graph from scratch again
        """
        try:
            # Create the directory if it doesn't exist
            directory = os.path.dirname(path)
            os.makedirs(directory)
        except OSError:
            pass # We don't actually care if they're already there
        try:
            # Delete file if it exists
            os.remove(path) 
        except OSError:
            pass # If it's already not there, that's fine too
        self.nch.Save(path)
        
    def Load(self, path):
        """
        Load
        Load a saved graph so we don't have to start from scratch again
        """
        self.nch.Load(path)
        
    def getSeenWords(self):
        return self.nch.getSeenWords()
        
    def Clear(self):
        self.nch.Clear()
        