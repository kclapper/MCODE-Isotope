from setuptools import setup

def readfile(filename):
    with open(filename, 'r+', encoding="utf-8") as f:
        return f.read()

setup(
    name="MCODE Isotope",
    version="1.2.1",
    description="A CLI for getting isotope masses from MCODE input files.",
    long_description=readfile('README.md'),
    author="S. Hauptman",
    packages=[
        'mcode_isotope',
    ],
    license=readfile('LICENSE'),
    entry_points={
        'console_scripts': [
            'mcode_isotope = mcode_isotope:runCLI'
        ]
    },
    package_data={
        "mcode_isotope": ["isotope_lib.csv"],
    },
)