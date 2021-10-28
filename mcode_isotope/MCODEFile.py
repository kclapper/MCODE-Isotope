from mcode_isotope.Element import Element
from mcode_isotope.ProgressTracker import ProgressTracker

class MCODEFile:
    """
    Represents an MCODE input file.
    
    Attributes:

    """

    def __init__(self, mcodeInputFile):
        """Parse the input file for elements and save as an attribute."""

        self.elements = []

        with open(mcodeInputFile, "r") as file:
            self._inputFileLines = [MCODEFileLine(line) for line in file.readlines()]
            
        self._parseMCODEInput()

    def _parseMCODEInput(self):
        """Assign class attributes based on lines of an MCODE input file."""

        self._getElementsFromSections()

    def _getElementsFromSections(self):
        """Creates a new element for each element section in the input file."""

        ProgressTracker("Reading elements from MCODE file")
        for linenumber, line in enumerate(self._inputFileLines):
            if line.isStartOfElementSection():
                ProgressTracker.increment()
                self.elements.append(Element(self._inputFileLines[linenumber:])) ## Not sure how many line long an element section
        ProgressTracker.complete()      

    def __getitem__(self, linesFromFile):
        """Get a subset of lines or a single line from the file."""

        return self._inputFileLines[linesFromFile]

class MCODEFileLine:
    """Represents a single line in an MCODE input file."""

    def __init__(self, fileLine):
        """Assign line to attribute and format accordingly."""

        self._fileLine = fileLine
        self._wordsInLine = self._formatAsList(self._fileLine)

    @staticmethod
    def _formatAsList(fileLine):
        """
        Turn a line of text into a list of words.
        
        If the line is empty it returns a list with a single space in it [" "].
        """

        if not fileLine:
            return [" "]
        return [word for word in fileLine.rstrip().split(" ") if word]

    def _hasWord(self, searchWord, atPosition=0):
        """
        Determines if a search word exists at a specified position in the line.
        
        Default line position to find word is 0 (start of the line).
        """

        if atPosition >= len(self._wordsInLine):
            return False
        return self._wordsInLine[atPosition] == searchWord

    def isStartOfElementSection(self):
        """Determines if this line is the start of an Element section in the MCODE file."""
        
        if self._hasWord("name") and not self.isStartOfExperimentSection():
            return True
        return False
    
    def isStartOfExperimentSection(self):
        """Determines if this line starts an experiment section."""

        experimentPositions = ["A3", "A1", "B3"]
        for spaceName in experimentPositions:
            if self._hasWord(spaceName, atPosition=1):
                return True
        return False

    def isStartOfMaterialSection(self):
        """Determines if this line is the description of a material."""

        return self._hasWord("material")
   
    def __getitem__(self, wordNumber):
        """Get a specific word from the list of words in the line."""
        
        return self._wordsInLine[wordNumber]

    def __repr__(self):
        return str(self._wordsInLine)