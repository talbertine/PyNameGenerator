# PyNameGenerator
A small python project that reads a list of words, breaks them up into syllables, and randomly combines them weighted by how often they come in sequence in the source

There's an old programming joke that one of the hardest problems in programming is naming things, so we're solving that one.

It works by breaking down words into graphemes and building a graph representing the sequences of these Graphemes. Each node is the sequence of some number of graphemes that occurred previously in the word and each edge is a possible next node, identified by all but the oldest of the preceding graphemes, and one new grapheme.

# Usage
Run main.py to start. You should get a command prompt.

? or help \[command\]: Gets a short description of what the command does, or if no command is provided, lists the available commands

add <word>: Breaks the word up into graphemes and adds it to the tree
  
addlist <listPath>: Adds many words at a time. One per line, please.
  
clear: Remove all words from the tree and start over
  
get <type> \[length\]: Generate a word from the model. Valid "types" are likely, which always picks the grapheme that comes after the preceding sequence most often, and random, which chooses one randomly but weighted in accordance with how often that grapheme follows the preceding sequence
  
gethist: Gets the number of preceding graphemes to consider when adding to the tree. If you use a history of 2 for example, the g in dog and the g in hog will be separate nodes. A history of 1 will only consider the o and not the d or h, so they will both link to the same g node. Long histories will match the source better, but because each sequence is a string of that many graphemes, they tend to result in larger model sizes. Besides, short histories are more creative, and can be more fun.
  
getlang: Returns the path to the active language file. I only speak english, so there's just the one right now, which is the default.
  
load <path>: Load a model you have already saved. I don't recommend trying to load a model associated with a different language, but at this time, it's not going to stop you.
  
quit: Closes the program. No surprises there.
  
save <path>: Saves a model to an XML file. This file contains a list of words entered into the graph, as well as the tree structure (by which I mean, a list of grapheme sequence nodes, and their associated following nodes.
  
sethist <length>: Sets the history length. Note that changing this will clear the model, because the number of entries in each node depends on the history. Loading a model will overwrite this too.
  
setlang <langPath>: Sets the language file. These are XML files that list the valid graphemes for a language. If you try to parse a word containing graphemes that aren't in this list, you'll get an error.
  
wordlist: Prints a list of the words in the model

# Example Word Lists
I've included in the repo a few sample word lists in the Data/nameLists folder. There should be a list of the most common female baby names of the '10s, the linux spell check dictionary, and a file I used to debug my english grapheme list so that it would support the words list.

# Tests
If you want to run my tests, run test.py instead. It's not especially interesting though.