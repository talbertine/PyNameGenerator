import SyllableParser.parser as parser

class UnrecognizedSyllable(Exception):
    def __init__(self, text):
        self.message = "Unrecognized syllable: " + text

def stringToGraphemes(source, lang="./Data/orthography/English.xml"):
    myParser = parser.getParser(lang)
    source = source.strip()
    result = myParser.parseWord(source)
    if result is None:
        raise UnrecognizedSyllable(source)
    return result