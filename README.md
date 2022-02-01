# MCODE Isotope

`mcode_isotope` is a CLI for retrieving nuclide mass data from an MCODE input deck and saving it
to a CSV file. It may also be used as a python module and provides relevant classes.

## Installation

`mcode_isotope` requires Python 3 and is not backwards compatible with Python 2. It is best installed using `pip`. 
Note that if you have both Python 3 and Python 2 you should replace the following commands with `pip3` instead.
On Windows, these commands must be run as Adminstrator otherwise usage will be slightly [different](#windows-installation).

#### Installing with `pip`

If you have ssh setup with GitHub, the easiest way to install `mcode_isotope` is with the following
command:

    pip install git+https://github.com/kclapper/MCODE-Isotope.git

If you don't have ssh setup, first clone/download the repository. Then from the project root directory run:

    pip install .

If you plan on editing the mcode_isotope source files you should instead install using:

    pip install -e .

## Usage

Once installed, the CLI can be used as follows:

    mcode_isotope <MCODE File> <Nuclide> [Output File] [Flags]

    <MCODE File>:   Should be path to a valid MCODE input deck.
    
    <Nuclide>:      The nuclide for which masses will be found. Should be in the 
                    format ZZAAA where ZZ is a zero padded atomic number and AAA
                    is a zero padded mass number.

    [Output File]:  Optionally specify the output file to write. Defaults to "mass.csv"
    
    Flags/Options:
        -h --help   Displays this help message

### Example:

    mcode_isotope EOC_Cycle237_Final.txt 92235 U235Mass.csv

## Notes

#### MCODE Compatibility

ICE cards can be beginning, end, both, or not included. NO STRIPING IMPLEMENTED. Only works with
1/2/5/4/2/1 plate groupings (96 mat cards per element). Elements can be flipped or not.

#### Using without `pip`

Installing `mcode_isotope` with `pip` is prefered for every day use. However, `mcode_isotope` can alternatively 
be run directly from the module. To run directly from the module, download the source files and from the project root 
directory run:

    python -m mcode_isotope <MCODE File> <Nuclide> [Output File] [Flags]

#### Windows Installation

If `mcode_isotope` is not installed with administrative priviledges, the CLI can still be run from any directory, however you won't be able 
to call the command by `mcode_isotope`. You'll have to call `python -m mcode_isotope` instead.

If you install with adminstrative priviledges as directed in the [installation instructions](#installation), you can call `mcode_isotope` normally
as depicted in the [usage instructions](#usage).

## Uninstall

To uninstall run:

    pip uninstall mcode_isotope
