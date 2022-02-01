#!/usr/bin/env python3

"""
Summary:

    mcode_isotope is a CLI for retrieving nuclide mass data from an MCODE input deck and saving it
    to a CSV file. It may also be used as a python module and provides relevant classes.

CLI Installation:

    From the root directory of this project (MCODE_Isotope) run `pip install .`

CLI Usage:

    The cli can be used as `mcode_isotope <MCODE File> <Nuclide> [Output File] [Flags]`
    See runCLI below.

Notes:

    ICE cards can be beginning, end, both, or not included. NO STRIPING IMPLEMENTED. Only works with
    1/2/5/4/2/1 plate groupings (96 mat cards per element). Elements can be flipped or not.

Modules:

    __init__.py         Contains functions to implement CLI.

    Element.py          Contains classes to represent a fuel element, material within the element, and the
                        NIST isotope library.

    MCODEFile.py        Contains classes to represent an MCODEFile.

    OutputFile.py       Contains a class which represents the output file to write.

    ProgressTracker.py  Contains a class to provide progress bars in stdout.

Created on Tue Aug 17 12:38:32 2021

@author: hauptman

"""
import sys
from pathlib import Path

from mcode_isotope.MCODEFile import MCODEFile
from mcode_isotope.OutputFile import OutputFile
from mcode_isotope.ProgressTracker import ProgressTracker

def runCLI():
    """
    Create's a CSV file describing the mass of a specific nuclide from an MCODE
    input file.

    Usage: mcode_isotope <MCODE File> <Nuclide> [Output File] [Flags]

    <MCODE File>:   Should be path to a valid MCODE input deck.
    
    <Nuclide>:      The nuclide for which masses will be found. Should be in the 
                    format ZZAAA where ZZ is a zero padded atomic number and AAA
                    is a zero padded mass number.

    [Output File]:  Optionally specify the output file to write. Defaults to "mass.csv"
    
    Flags/Options:
        -h --help   Displays this help message

    Example: mcode_isotope EOC_Cycle237_Final.txt 92235 U235Mass.csv
    """

    args = sys.argv[1:]

    if needsHelp(args):
        print(runCLI.__doc__)
        return 

    if hasValidInput(args):
        createFile(*args)
    else:
        print(runCLI.__doc__)
        return

def needsHelp(args):
    """See if the input arguments specified needing help."""

    if "-h" in args or "--help" in args:
        return True

def hasValidInput(args):
    """See if the input is valid."""

    if len(args) > 3:
        print("Too many arguments given.")
        return False

    try:
        Path(args[0]).is_file()
    except:
        print("Invalid MCODE input file specified.")
        return False

    if len(args) == 3:
        try:
            Path(args[2])
        except:
            print("Invalid output file specified")
            return False

    try:
        int(args[1])
        isValid = len(args[1]) == 5
    except:
        print("Invalid nuclide specified.")
        return False

    return isValid

def createFile(mcodefile, nuclide, outputFile="mass.csv"):
    """Creates mass.csv with nuclide masses from mcodefile."""

    mcodefile = MCODEFile(mcodefile)
    massfile = Path(outputFile)

    ProgressTracker("Calculating masses and preparing mass file")
    outputFile = OutputFile(massfile, nuclide)
    for element in mcodefile.elements:
        outputFile.addOutputFromElement(element)
        ProgressTracker.increment()
    outputFile.addCoreTotalMass()
    ProgressTracker.complete()

    outputFile.writeFile()