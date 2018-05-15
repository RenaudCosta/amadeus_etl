import re
from GeoCode.rail_country_codes import RailCountryCodes
import json

class ColFinder:
    def __init__(self, lines, separator):
        self.separator = separator
        self.lines = lines
        self.uicID = -1
        self.glcID = -1
        self.longDescID = -1
        self.stationTypeID = -1
        self.NCoordID = -1
        self.ECoordID = -1
        self.ownerID = -1
        self.countryID = -1
        self.displayID = -1
        self.findGlcUic()
        mid = lines[len(lines) // 2]
        self.define_column_ids(mid.split(separator))

    def getIndices(self):
        return {"uic": self.uicID,
                "glc": self.glcID,
                "longdesc" : self.longDescID,
                "owner" : self.ownerID,
                "type": self.stationTypeID,
                "ncoord": self.NCoordID,
                "ecoord": self.ECoordID,
                "country": self.countryID,
                "display": self.displayID,
                }


    """
        We iterate over all the lines to see if we can find something that we are sure is a 1A code (GLC):
        like 01G0001
    """
    def findGlc(self):
        glcPattern = re.compile("^[0-9]{2}G[0-9]{4}$")
        for line in self.lines:
            for id, col in enumerate(line.split(self.separator)):
                if glcPattern.match(col) or col == "0000000":
                    return id
        return -1

    """
        We try to find a line where the 1A code is under the form : 01G0001, so we use another column that has a
        7 digit number (or 010A012) as UIC
    """
    def findUic(self):
        uicPattern = re.compile("^[0-9]{3}A?[0-9]{3,5}$")
        glcPattern = re.compile("^[0-9]{2}G[0-9]{4}$")
        for line in self.lines:
            line = line.split(self.separator)
            if glcPattern.match(line[self.glcID]) or line[self.glcID] == "0000000":
                for id, col in enumerate(line):
                    if id != self.glcID and uicPattern.match(col) and col != "0000000":
                        return id
        return -1


    '''
        For some entry lines, it's not so simple to see whether a code is a GLC or a UIC code.
        Thus we look for a line in which both codes differ from each other and we set the columns id
        for all the other lines like this.
    '''
    # IDEA : Make such a function for all the fields so we can have better results for the columns ids
    # (So if the middle line currently setting the standard for all the lines is poorly filled, we can still have
    # good results because we would base our result on a different line)
    def findGlcUic(self):

        """
            We try to find the GLC and UIC with a simple search
        """
        self.glcID = self.findGlc()
        if self.glcID != -1:
            self.uicID = self.findUic()
            return

        """
            If we couldn't find a GLC, if there's only 1 column that can be either UIC or 1A, we assume it's UIC,
            and 1A is not present
        """
        glcPattern = re.compile("^[0-9]{2}G[0-9]{4}$")
        uicPattern = re.compile("^[0-9]{3}A?[0-9]{3,5}$")
        cols = self.glc_or_uic_cols()
        if len(cols) == 1:
            self.uicID = cols[0]
            self.glcID = -1
            return

        """
            If we have several columns that are ambiguous, we ask the user for the UIC id
        """

        showLine = self.lines[min(1, len(self.lines)-1)]
        print(showLine, end="")
        for id, col in enumerate(showLine.split(self.separator)):
            if len(str(id)) <= len(col):
                print(id, end="")
                for i in range(len(col)-len(str(id))):
                    print(" ", end="")
            print(" ", end="")
        print()
        self.uicID = int(input("uic ID: "))
        self.glcID = -1



    def glc_or_uic_cols(self):
        glcPattern = re.compile("^[0-9]{2}G[0-9]{4}$")
        uicPattern = re.compile("^[0-9]{3}A?[0-9]{3,5}$")
        line = self.lines[min(1,len(self.lines)-1)]
        out = []
        for id, col in enumerate(line.split(self.separator)):
            if glcPattern.match(col) or uicPattern.match(col):
                out.append(id)
        return out



    def define_column_ids(self, line):
        '''
        The task of this function is to guess the input file format from one line taken from the middle of it.
        We assume that in the input file, all the lines are put in the same order, so once we know where to find
        which information, we can then reformat it to change the order to the one we want to use.
        '''
        for id, col in enumerate(line):
            col = col.strip()
            col = col.replace("\n","")
            if col == "":
                continue
            if id == self.glcID: # this ID is already assigned to GLC
                continue
            pattern = re.compile("([a-zA-Z. |(\)-]){4,}") # If we can find 3 letters or special chars in a row
            if (self.stationTypeID == -1 and len(col) == 2 and col.isdigit()):
                self.stationTypeID = id
                continue
            pattern = re.compile("([a-zA-Z. |(\)-]){4,}")  # If we can find 3 letters or special chars in a row
            if (self.longDescID == -1 and pattern.match(col)):
                self.longDescID = id
                continue
            pattern = re.compile("^[A-Z]{2}$")
            if self.countryID == -1 and pattern.match(col):
                self.countryID = id
                continue
            if self.displayID == -1 and (col == "1" or col == "2"):
                self.displayID = id
                continue
            pattern = re.compile("^[0-9]{6}N$")
            pattern2 = re.compile("^[0-9]+,[0-9]+$")
            if self.NCoordID == -1 and (pattern.match(col) or pattern2.match(col)):
                self.NCoordID = id
                continue
            pattern = re.compile("^[0-9]{6}[EW]$")
            if self.ECoordID == -1 and (pattern.match(col) or pattern2.match(col)):
                self.ECoordID = id
                continue
            pattern = re.compile("^[A-Z]{3}$")
            if self.ownerID == -1 and pattern.match(col) and col != "CET" and col != "RDS" and col != "UIC":
                self.ownerID = id
                continue


class LineFormatter:
    def __init__(self, path=""):
        data = json.load(open('iso3166-1.json'))
        data = data['3166-1']
        self.iso_codes = {}

        self.lines = []

        for d in data:
            self.iso_codes[d['name']] = d
        self.countryCode = RailCountryCodes().country_names
        guess_separator = GuessSeparator(path)
        self.separator = guess_separator.separator()
        try:
            with open(path, "r", encoding="utf-8") as input:
                for row in input:
                    self.lines.append(row)
        except UnicodeDecodeError:
            with open(path, "r") as input:
                for row in input:
                    self.lines.append(row)
        colFinder = ColFinder(self.lines, self.separator)
        self.ids = colFinder.getIndices()

    def get_separator(self):
        return self.separator


    def reformat(self, *args):
        lineSplit = args[-1].split(self.separator)
        newLineSplit = [""]*11
        newLineSplit[0] = lineSplit[self.ids["uic"]] if self.ids["uic"] > -1 else ""
        if len(newLineSplit[0]) == 6:
            newLineSplit[0] = "0" + newLineSplit[0]
        if newLineSplit[0][0:2] in self.countryCode and self.countryCode[newLineSplit[0][0:2]] in self.iso_codes:
            countryCode = self.iso_codes[self.countryCode[newLineSplit[0][0:2]]]['alpha_2']
        else:
            countryCode = "N/A"
        newLineSplit[1] = lineSplit[self.ids["longdesc"]].replace("\n", "") if self.ids["longdesc"] > -1 else ""
        newLineSplit[2] = lineSplit[self.ids["type"]].replace("\n", "") if self.ids["type"] > -1 else "29"
        newLineSplit[3] = lineSplit[self.ids["ncoord"]].replace("\n", "") if self.ids["ncoord"] > -1 else "000000N"
        newLineSplit[4] = lineSplit[self.ids["ecoord"]].replace("\n", "") if self.ids["ecoord"] > -1 else "000000E"
        newLineSplit[5] = lineSplit[self.ids["glc"]].replace("\n", "") if self.ids["glc"] > -1 else "0000000"
        newLineSplit[6] = lineSplit[self.ids["longdesc"]][:19].replace("\n", "") if self.ids["longdesc"] > -1 else ""
        newLineSplit[7] = lineSplit[self.ids["type"]].replace("\n", "") if self.ids["type"] > -1 else "29"
        newLineSplit[8] = ""
        newLineSplit[9] = lineSplit[self.ids["country"]].replace("\n", "") if self.ids["country"] > -1 else countryCode
        newLineSplit[10] = lineSplit[self.ids["display"]].replace("\n", "") if self.ids["display"] > -1 else "1\n"
        if newLineSplit[10][-1] != '\n':
            newLineSplit[10] += '\n'
        yield newLineSplit


    def reformatMapping(self, *args):
        lineSplit = args[-1].split(self.separator)
        newLineSplit = [""]*21

        if newLineSplit[0][0:2] in self.countryCode and self.countryCode[newLineSplit[0][0:2]] in self.iso_codes:
            countryCode = self.iso_codes[self.countryCode[newLineSplit[0][0:2]]]['alpha_2']
        else:
            countryCode = "N/A"

        newLineSplit[1] = "CET"
        newLineSplit[3] = lineSplit[self.ids["display"]] if self.ids["display"] > -1 else "\n"
        newLineSplit[5] = lineSplit[self.ids["country"]].replace("\n", "") if self.ids["country"] > -1 else countryCode
        newLineSplit[7] = lineSplit[self.ids["longdesc"]] if self.ids["longdesc"] > -1 else ""
        newLineSplit[8] = lineSplit[self.ids["longdesc"]][:19] if self.ids["longdesc"] > -1 else ""
        newLineSplit[11] = lineSplit[self.ids["glc"]] if self.ids["glc"] > -1 else ""
        newLineSplit[12] = lineSplit[self.ids["ncoord"]] if self.ids["ncoord"] > -1 else "000000N"
        newLineSplit[13] = lineSplit[self.ids["type"]] if self.ids["type"] > -1 else "29"
        newLineSplit[14] = lineSplit[self.ids["ecoord"]] if self.ids["ecoord"] > -1 else "000000E"
        newLineSplit[18] = lineSplit[self.ids["owner"]] if self.ids["owner"] > -1 else "000000E"
        newLineSplit[19] = lineSplit[self.ids["uic"]] if self.ids["uic"] > -1 else ""
        newLineSplit[20] = "UIC\n"

        yield newLineSplit


class GuessSeparator:
    def __init__(self, path=""):
        self.path = path

    def separator(self, line=""):
        if line == "":
            try:
                with open(self.path, "r", encoding="utf-8") as input:
                    for row in input:
                        split_tab = row.split("\t")
                        split_pipe = row.split("|")
                        if len(split_tab) > len(split_pipe):
                            return "\t"
                        else:
                            return "|"
            except UnicodeDecodeError:
                with open(self.path, "r") as input:
                    for row in input:
                        split_tab = row.split("\t")
                        split_pipe = row.split("|")
                        if len(split_tab) > len(split_pipe):
                            return "\t"
                        else:
                            return "|"
        else:
            split_tab = line.split("\t")
            split_pipe = line.split("|")
            if len(split_tab) > len(split_pipe):
                return "\t"
            else:
                return "|"

