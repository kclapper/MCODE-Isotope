import csv

from mcode_isotope.ProgressTracker import ProgressTracker

class OutputFile:
    """Represents the output file containing the isotope masses."""

    def __init__(self, outputFile, nuclide):
        """Opens the file to writes out and set attributes."""

        self._outputFile = outputFile
        self._nuclideOfInterest = str(nuclide)
        self._axialHeading = ["mass (g)"]
        self._axialRows = [[f"Axial {nodeNumber}"] for nodeNumber in range(1, 17)]

        self._plateHeading = ["mass (g)"] + [f"Plate {plateNumber}" for plateNumber in range(1, 16)] + ["Sum"]
        self._plateRows = []

    def addOutputFromElement(self, element):
        """From an Element, add necessary information to write to the output file."""

        self._axialHeading += [element.gridPosition]

        self._addElementToAxialRows(element)
        self._addElementToPlateRows(element)

    def _addElementToAxialRows(self, element):
        """Adds the axial mass of an element to the axialRows."""

        for node, row in enumerate(self._axialRows, start=1):
            row.append(element.getAxialMass(self._nuclideOfInterest, node))

    def _addElementToPlateRows(self, element):
        """Adds the plate mass of each element to the plate rows."""

        plateMasses = [element.getPlateMass(self._nuclideOfInterest, plateNumber) for plateNumber in range(1,16)]
        newRow = [element.gridPosition] + plateMasses + [sum(plateMasses)]
        self._plateRows.append(newRow)

    def addCoreTotalMass(self):
        """Gets total core mass from plate masses."""

        coreMass = 0
        for row in self._plateRows:
            coreMass += row[16]

        self._coreMassRow = ["Core Total:", coreMass]

    def writeFile(self):
        """Writes the output file to disk."""

        ProgressTracker("Writing mass file")
        rowsToWrite = [
            self._axialHeading,
            *self._axialRows,
            [],
            self._plateHeading,
            *self._plateRows,
            [],
            self._coreMassRow
        ]
        with open(self._outputFile, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            for row in rowsToWrite:
                writer.writerow(row)
                ProgressTracker.increment()
        ProgressTracker.complete()