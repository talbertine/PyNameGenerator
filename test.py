import SyllableParser as SP
import NameChain as NC

assert(SP.stringToGraphemes("") == [])
assert(SP.stringToGraphemes("Dad") == ["d", "a", "d"])
assert(SP.stringToGraphemes("so") == ["s", "o"])
assert(SP.stringToGraphemes("though") == ["th", "ough"])
assert(SP.stringToGraphemes("zurich") == ['z', 'ur', 'ic', 'h'])
assert(SP.stringToGraphemes("Bhagavad-Gita") == ['bh', 'ag', 'a', 'v', 'a', 'd', '-', 'gi', 't', 'a'])

nameChain = NC.NameChain(3, 0)

with open("./Data/nameLists/words.txt", "r") as file:
  for line in file:
    line = line.strip()
    graphemes = SP.stringToGraphemes(line)
    nameChain.addWord(graphemes)

nameChain.Save("./TEST_DATA/chainData.xml")
otherChain = NC.NameChain(3, 0)
otherChain.Load("./TEST_DATA/chainData.xml")

# I don't know why the sets always come out the same, but I'm not questioning it
assert(nameChain.getMostLikelyWord(100) == otherChain.getMostLikelyWord(100))
# Seeds should be the same, so these should produce the same thing
for i in range(10):
    assert(nameChain.getRandomWord(100) == otherChain.getRandomWord(100))