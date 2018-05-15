import math


class Step1Comparing:

    def __init__(self, old_uics):
        self.old_uics = old_uics

    def todms(self, longitude, latitude):
        '''
        for convert degree to dms
        :param longitude:
        :param latitude:
        :return:
        '''
        # math.modf() splits whole number and decimal into tuple
        # eg 53.3478 becomes (0.3478, 53)
        split_degx = math.modf(longitude)

        # the whole number [index 1] is the degrees
        degrees_x = int(split_degx[1])
        # multiply the decimal part by 60: 0.3478 * 60 = 20.868
        # split the whole number part of the total as the minutes: 20
        # abs() absoulte value - no negative
        minutes_x = abs(int(math.modf(split_degx[0] * 60)[1]))

        # multiply the decimal part of the split above by 60 to get the seconds
        # 0.868 x 60 = 52.08, round excess decimal places to 2 places
        # abs() absoulte value - no negative
        seconds_x = abs(round(math.modf(split_degx[0] * 60)[0] * 60, 2))

        # repeat for latitude
        split_degy = math.modf(latitude)
        degrees_y = int(split_degy[1])
        minutes_y = abs(int(math.modf(split_degy[0] * 60)[1]))
        seconds_y = abs(round(math.modf(split_degy[0] * 60)[0] * 60, 2))

        # account for E/W & N/S
        if degrees_x < 0:
            EorW = "W"
        else:
            EorW = "E"

        if degrees_y < 0:
            NorS = "S"
        else:
            NorS = "N"

        degX = str(abs(degrees_x ))
        minX = str(minutes_x)
        secX = str(int(seconds_x))
        degY = str(abs(degrees_y))
        minY = str(minutes_y)
        secY = str(int(seconds_y))
        if len(degX) < 2:
            degX = "0"+degX
        if len(minX) < 2:
            minX = "0"+minX
        if len(secX) < 2:
            secX = "0"+secX
        secX+=NorS
        if len(degY) < 2:
            degY = "0"+degY
        if len(minY) < 2:
            minY = "0"+minY
        if len(secY) < 2:
            secY = "0"+secY
        secY+=EorW
        # abs() remove negative from degrees, was only needed for if-else above
        return degX+minX+secX , degY+minY+secY

    def right_format_new(self, line):
        if len(line) < 10:
            return False
        return True

    def check_new_stations(self, *args):

        line = args[0]

        if not self.right_format_new(line):
            print("Skipping: "+"\t".join(line))
        else:
            # STATION TYPE
            if line[2] == "railway" or line[2] == "no":
                line[2] = "29"
                line[7] = ""
            elif line[2] == "city" or line[2] == "yes":
                line[2] = "26"
                line[7] = ""

            # FIX NAME
            line[1] = line[1].replace("|", "")

            # FIX COORDINATES
            if line[3].__contains__(","):
                new_lat = float(line[3].replace(",", "."))
                new_long = float(line[4].replace("\n", "").replace(",", "."))
                fix_lat = self.todms(new_lat, new_long)
                line[3] = fix_lat[0]
                line[4] = fix_lat[1]

            flag = ""
            # CHECK IF NEW LINE
            if line[0] in self.old_uics.keys() and line[2] == self.old_uics[line[0]][7]:
                flag = "exists"
            else:
                flag = "new"
            if not line[0].isdigit():
                print(line[0])
                line = ("",)

            yield line, flag



    """
        Conditional Node Transformation:
        Checks if the station is new, if so, it yields the line, otherwise yields nothing
    """

    def new_station(*args):
        # args[0] is Step1 object
        line = args[1]
        flag = args[2]
        if flag == "new":
            yield line

    """
        Conditional Node Transformation:
        Checks if the station already exists as is, if so, it yields the line, otherwise yields nothing
    """

    def old_station_unchanged(*args):
        # args[0] is Step1 object
        line = args[1]
        flag = args[2]
        if flag == "exists":
            yield line

    """
        Conditional Node Transformation:
        Checks if the station already exists with a different id, it yields the line, otherwise yields nothing
    """

    def old_station_updated(*args):
        # args[0] is Step1 object
        line = args[1]
        flag = args[2]
        if flag == "updated":
            yield line
