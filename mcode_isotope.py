#!/usr/bin/env python3

"""
Created on Tue Aug 17 12:38:32 2021

@author: hauptman
"""
import sys
import csv
import unicodedata as u

####################################
"""
version = 1.1

command line arguments [filename] [nuclide]
    file must be an mcode input deck, ICE cards can be beginning, end, both, or not included.
    NO STRIPING IMPLEMENTED
    Only works with 1/2/5/4/2/1 plate groupings (96 mat cards per element)
        Can be flipped or not

"""
# Set filenames from argument

mcodefile = sys.argv[1]
nuclide = sys.argv[2]
massfile = "mass.csv"
isotope_library = "/home/seh/scripts/isotope_lib.csv"

################## TESTING ################################
# nuclide = "13027"
# mcodefile = "239_export1"
# isotope_library = "isotope_lib.csv"

################## CONSTANTS ################################
axial = 3.55203125 #cm
depth = 0.08798838 #cm
width = 4.57977446 #cm

node_vol = axial*depth*width
# map material group to plates g:[plates], accounts for flipped or not
groups = {False:{1:[1], 2:[2,3], 3:[4,5,6,7,8], 4:[9,10,11,12], 5:[13,14], 6:[15]},
          True:{1:[1], 2:[2,3], 3:[4,5,6,7], 4:[8,9,10,11,12], 5:[13,14], 6:[15]}}

################### CLASS DEFINITIONS ########################

class Element(object):
    """
    Represents an element; initializes mat dictionary
    """
    def __init__(self, position, name):
        self.position = str(position)
        self.name = str(name)
        self.mats = {}
        self.flip = False

    def get_position(self):
        return self.position
    def get_name(self):
        return self.name
    def get_mats(self):
        return self.mats
    def get_mat(self, gn):
        """
        gn: tuple of (group, node)
        """
        if gn in self.mats.keys():
            return self.mats[gn]
        else:
            return None
    def check_flip(self):
        return self.flip
    def set_flip(self):
        self.flip = True

    def add_mat(self, mat):
        """
        add Material object to mats dictionary, using group and node as tuple key
        and Material object as the value
        """
        g = mat.get_group()
        n = mat.get_node()
        self.mats[(g, n)] = mat

class Material(object):
    """
    Represents a material composition
    """
    def __init__(self, group, node, density):
        self.group = int(group)
        self.node = int(node)
        self.density = float(density)
        self.composition = {}

    def get_group(self):
        return self.group
    def get_node(self):
        return self.node
    def get_composition(self):
        return self.composition
    def get_density(self):
        return self.density
    def get_norm(self):
        return self.norm

    def add_nuclide(self, ID, concentration):
        self.composition[ID] = float(concentration)

    def normalize(self):
        self.norm = {}
        tot = 0
        for key in self.composition.keys():
            tot += self.composition[key]
        for key in self.composition.keys():
            self.norm[key] = self.composition[key]/tot
        return

################## HELPER FUNCTIONS #######################
def strip_space(space_list):
    new_list = []
    for entry in space_list:
        if entry != "":
            new_list.append(entry)
    return new_list

def make_list(lines, i):
    """
    convert line i entry into a list with no extra " " spaces
    if file contains blank line, returns a single space " " list
    """
    row = lines[i].rstrip().split(" ")
    line = []
    for elem in row:
        if elem != "":
            line.append(elem)
    if len(line) == 0:
        return [" "]
    else:
        return line

def find_line(lines, flag, j=0):
    """
    takes lines of text file and searches for the lines with flag in given line index j
        default is start of line
    returns all indices of line with given flag or None if flag not found
    """
    indices = []
    for i in range(len(lines)):
        line = make_list(lines, i)
        if len(line) > j:
            if line[j]==str(flag):
                indices.append(i)
    if len(indices) > 0:
        return indices
    else:
        return None

def get_mat_mass(mat, nuclide, vol=node_vol):
    """
    Takes in the specified nuclide as a string of ZZAAA, and searches in the given material
    for that nuclide and the density. Calls the isotope library for atomic mass.
    Default volume is 1/16 of a fuel plate
    Returns the mass of the nuclide in g for the material (node specific)
    """
    mat.normalize()
    rho = mat.get_density()
    frac = mat.get_norm()[nuclide]
    mass = read_lib(nuclide)
    return vol*rho*mass*frac*10/6.022

def read_lib(nuclide, filename=isotope_library):
    """
    Takes in the specified nuclide as a string of ZZAAA, and searches through the given isotope
    CSV library for the atomic mass. Library file must be in same directory as script(?) or input deck(?).
    Returns the atomic mass for the given isotope [float]
    """
    z = nuclide[:2]
    a = int(nuclide[2:])
    with open(filename, "r", newline="", encoding="windows-1254") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0] == z and int(row[1]) == a:
                return float(row[2])
    print("Used Default")
    return a

def map_group(plate, flip):
    """
    Returns material group for given plate number using mapped dictionary in constants def
    flip flag pulled from element object to determine which plate map to use
    """
    for key in groups[flip].keys():
        for p in groups[flip][key]:
            if plate == p:
                return key


def get_plate_mass(nuclide, plate, element):
    """
    For the given element, nuclide, and plate, combines the nuclide mass in all the axial
    nodes.
    Returns the total nuclide mass of the plate as a float
    """
    tot = 0
    g = map_group(plate, element.check_flip())
    for n in range(1, 17):
        mat = element.get_mat((g, n))
        node_mass = get_mat_mass(mat, nuclide)
        tot += node_mass

    return tot

def get_axial_mass(nuclide, node, element):
    """
    For the given element, nuclide, and node, combines the nuclide mass in all the plates.
    Returns the total nuclide mass of the axial height as a float
    """
    tot = 0
    for i in range(1, 16):
        g = map_group(i, element.check_flip())
        mat = element.get_mat((g, node))
        node_mass = get_mat_mass(mat, nuclide)
        tot += node_mass

    return tot

def card_search(lines, start="material", stop="material", alt_stop="name", i=0):
    """
    Takes in entire set of lines, returns only the first chunk between the given
    start and stop values.
    Default is to start at beginning of line file, change i to start later
    Assumes start/stop flags are first entry in line.
    Includes start flag line in chunk, but not end flag line.
    Default alternate stop is next name line of successive card but will also stop at EOF
    Chunk is formatted as list of lines as lists stripped of spaces
    """
    chunk = []
    flag = False
    for line in lines[i::]:
        line_list = line.rstrip().split(" ")
        if len(line_list) == 0:
            check = "\n"

        else:
            check = line_list[0]

        if check == start:
            flag = True
            start = None # Effectively ignore start flag after finding it

        elif check == stop:
            flag = False
            break # only take a single chunk between the two flags

        elif check == alt_stop:
            flag = False
            break

        while flag == True:
            chunk.append(strip_space(line_list))
            break

    return chunk

def parse_mat_chunk(chunk):
    """
    Takes in list chunk with material card
    Creates and returns Material object with mapped composition
    """
    g = chunk[0][1]
    n = chunk[0][3]
    density = chunk[0][4]
    mat = Material(g, n, density)
    for i in range(1, len(chunk)):
        iso = chunk[i][::2]
        conc = chunk[i][1::2]

        for j in range(len(iso)):
            mat.add_nuclide(iso[j][:5], conc[j])

    return mat

def get_element_mats(indices, element):
    """
    Takes in an Element object and the material flag indices
    Parses material cards, creates Material objects for each, maps the nuclide
    compositions, and compiles in Element object material dictionary
    Returns nothing
    """
    for j in indices:
        chunk = card_search(lines, i=j)
        mat = parse_mat_chunk(chunk)
        element.add_mat(mat)

    return

def parse_file(lines):
    """
    Reads entire input deck file, creates Element objects, processes materials
    Returns list of all Element objects
    """
    elements = []
    positions = find_line(lines, "name")
    mat_index = find_line(lines, "material")
    for i in positions:
        exp = False
        pos = make_list(lines, i)[1]
        name = make_list(lines, i+8)[-1]
        rad = make_list(lines, i+13)
        if pos == "A1" or pos == "A3" or pos == "B3":
            exp = True
        else:
            elem = Element(pos, name)
        try:
            if rad[3] == "7":
               elem.set_flip()
        except IndexError:
            pass

        if exp == False:
            indices = []
            for j in mat_index:
                if j > i:
                    indices.append(j)

            get_element_mats(indices[:96], elem)

            elements.append(elem)

    return elements


#################### IMPLEMENTATION ##############################

file = open(mcodefile, "r")
lines = file.readlines()

elements = parse_file(lines)

file.close()

#################### CSV WRITE ##############################

with open(massfile, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    heading = ["mass (g)"]
    for e in elements:
        heading.append(e.get_position())
    writer.writerow(heading)
    for i in range(1, 17):
        row = ["Axial "+str(i)]
        for e in elements:
            row.append(get_axial_mass(nuclide, i, e))
        writer.writerow(row)
    writer.writerow([])
    heading = ["mass (g)"]
    for p in range(1, 16):
        heading.append("Plate "+str(p))
    heading.append("Sum")
    writer.writerow(heading)
    core = 0
    for e in elements:
        row = [e.get_position()]
        tot = 0
        for p in range(1, 16):
            row.append(get_plate_mass(nuclide, p, e))
            tot += get_plate_mass(nuclide, p, e)
        core += tot
        row.append(tot)
        writer.writerow(row)
    writer.writerow(["Core Total:", core])







