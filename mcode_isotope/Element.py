import csv, os
from importlib.resources import open_text

import mcode_isotope

class Element:
    """Represents a Fuel Element."""

    _maxMaterialDescriptions = 96
    _groups = {False:{1:[1], 2:[2,3], 3:[4,5,6,7,8], 4:[9,10,11,12], 5:[13,14], 6:[15]},
          True:{1:[1], 2:[2,3], 3:[4,5,6,7], 4:[8,9,10,11,12], 5:[13,14], 6:[15]}}

    _axial = 3.55203125 #cm
    _depth = 0.08798838 #cm
    _width = 4.57977446 #cm
    _nodeVolume = _axial * _depth * _width

    def __init__(self, elementSectionLines):
        """Initialize Element attributes from an element section in an MCODE file."""

        self._elementSectionLines = elementSectionLines
        self._removeIrrelevantLines()

        self.gridPosition = elementSectionLines[0][1]
        self.elementName = elementSectionLines[8][-1] 
        self._determineIfFlipped()
        self._getMaterialComposition()

    def _removeIrrelevantLines(self):
        """Removes sections unrelated to this particular element."""

        for lineNumber, line in enumerate(self._elementSectionLines[1:]):
            if line.isStartOfElementSection() or line.isStartOfExperimentSection():
                self._elementSectionLines = self._elementSectionLines[:lineNumber]

    def _determineIfFlipped(self):
        """Determine if the element is flipped."""

        try:
            self.isFlipped = self._elementSectionLines[13][3] == "7"
        except IndexError:
            self.isFlipped = False
    
    def _getMaterialComposition(self):
        """Create a list of material compositions up to the maximum number."""

        self._materials = []
        for lineNumber, line in enumerate(self._elementSectionLines):
            if self._hasMaxMaterialDescriptions():
                break
            elif line.isStartOfMaterialSection():
                self._materials.append(Material(self._elementSectionLines[lineNumber:])) 

    def _hasMaxMaterialDescriptions(self):
        """Determines if the Element already has the maximum number of material descriptions."""

        return len(self._materials) >= self._maxMaterialDescriptions

    def getAxialMass(self, nuclide, node):
        """Returns the total nuclide mass for all fuel plates at an axial height as a float."""

        totalNuclideMass = 0
        for plateNumber in range(1, 16):
            group = self._getGroupFromPlateNumber(plateNumber)
            material = self._getMaterialWithGroupNode(group, node)
            nodeMass = material.getNuclideMassDensity(nuclide) * self._nodeVolume
            totalNuclideMass += nodeMass
        
        return totalNuclideMass

    def _getGroupFromPlateNumber(self, plateNumber):
        """Returns the group number of a given plate."""

        for group, plates in self._groups[self.isFlipped].items():
            if plateNumber in plates:
                return group

    def _getMaterialWithGroupNode(self, group, node):
        """Returns a specific Material correlated with the group and node."""

        for material in self._materials:
            if material.group == group and material.node == node:
                return material
        raise Exception(f"Material not found group: {group}, node: {node}")
    
    def getPlateMass(self, nuclide, plateNumber):
        """Get the mass of a specific nuclide from a specific plate."""

        group = self._getGroupFromPlateNumber(plateNumber)
        
        totalNuclideMass = 0
        for node in range(1, 17):
            material = self._getMaterialWithGroupNode(group, node)
            nodeDensity = material.getNuclideMassDensity(nuclide)
            totalNuclideMass += nodeDensity * self._nodeVolume

        return totalNuclideMass
    
    def __repr__(self):
        """Determine what Element looks like when printed."""

        return self.elementName

class Material:
    """Represents a material composition"""

    def __init__(self, materialSectionLines):
        """Creates a Material from an MCODEFileLine"""

        self._materialSectionLines = materialSectionLines
        self._removeIrrelevantLines()

        self.group = int(self._materialSectionLines[0][1])
        self.node = int(self._materialSectionLines[0][3])
        self._numberDensity = float(self._materialSectionLines[0][4])

        self._getNuclides()
        self._getNormalizedComposition()

    def _removeIrrelevantLines(self):
        """
        Removes the lines that aren't related to the current material section.
        i.e when the next material section starts or an element section starts.
        
        """

        for lineNumber, line in enumerate(self._materialSectionLines[1:], start=1):
            if line.isStartOfMaterialSection() or line.isStartOfElementSection() or line.isStartOfExperimentSection():
                self._materialSectionLines = self._materialSectionLines[:lineNumber]

    def _getNuclides(self):
        """Gets the nuclide data from the relevant material section lines."""

        self.composition = {}
        for line in self._materialSectionLines[1:]:
            self.composition.update({isotope[:5]:float(concentration) for (isotope, concentration) in zip(line[::2], line[1::2])})

    def _getNormalizedComposition(self):
        """Creates attribute holding normalized compositions."""

        self._normalizedComposition = {}
        total = sum(self.composition.values())
        for isotope, composition in self.composition.items():
            self._normalizedComposition.update({isotope: composition/total})

    def getNuclideMassDensity(self, nuclide):
        """Get the mass density of a specific nuclide in the material."""

        atomicMass = NuclideLibrary().nuclideAtomicMass(nuclide)

        return self._numberDensity * self._normalizedComposition[nuclide] * atomicMass * 10 / 6.022

    def __repr__(self):
        """Determines what a Material looks like when printed."""

        return f"Material group: {self.group}, node: {self.node}, number density: {self._numberDensity}"

class NuclideLibrary:
    """Represents the NIST istotope library."""

    def __init__(self, libraryFile="isotope_lib.csv"):
        """Open the library file and read all values."""

        self._libraryFileRows = []

        with open_text(mcode_isotope, libraryFile, encoding='windows-1254', errors='strict') as csvfile:
        # with open(libraryFile, "r", newline="", encoding="windows-1254") as csvfile:
            for row in csv.reader(csvfile):
                self._libraryFileRows.append(row)

    def nuclideAtomicMass(self, nuclide):
        """Returns the atomic mass of a specified nuclide."""

        atomicNumber = nuclide[:2]
        massNumber = int(nuclide[2:])

        for row in self._libraryFileRows:
            if row[0] == atomicNumber and int(row[1]) == massNumber:
                return float(row[2])

        return massNumber ## If atomic mass not available in library