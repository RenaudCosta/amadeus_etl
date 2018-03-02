#!/usr/bin/env python
# coding: utf-8

import os
import codecs
import math
from tkinter import messagebox

### INPUT FILES ###
file_with_searchable = "in/eva_with_searchable.csv"
file_with_lat_long = "in/bne_with_lat_long.csv"
file_rail_location_provider = "in/rail-location-provider.csv"

### OUTPUT FILES ###
rail_location_provider = "out/rail_location_provider.csv"
different_name = "out/different_name.csv"


class process:
    '''
    this class determinate if a station is sourceable or not and set the correct number for the identification 1 or 2,
    take in input 3 file one with the information regarding the lat and long (if is necessary fix the format of the coordination),
    one with information about searchable and the last the file to fix
    '''

    def __init__(self):
        with open(file_with_searchable) as ip:
            self.list_with_searchable = [row.split(",") for row in ip]
        with open(file_with_lat_long) as ip:
            self.list_with_lat_long = [row.split(",") for row in ip]
        with open(file_rail_location_provider) as ip:
            self.list_rail_location_provider = [row.split("|") for row in ip]

        self.dic_with_lat_long = {} # <UIC, index in list>
        self.dic_with_searchable = {} # <UIC, index in list>

        self.new_list_rail_location_provider = []
        self.different_name = []

    # for convert degree to dms
    def todms(self, longitude, latitude):

        '''
        this method convert the format lat and long to 3.252522 to 45852N for example
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

        degX = str(abs(degrees_x))
        minX = str(minutes_x)
        secX = str(int(seconds_x))
        degY = str(abs(degrees_y))
        minY = str(minutes_y)
        secY = str(int(seconds_y))
        if len(degX) < 2:
            degX = "0" + degX
        if len(minX) < 2:
            minX = "0" + minX
        if len(secX) < 2:
            secX = "0" + secX
        secX += NorS
        if len(degY) < 2:
            degY = "0" + degY
        if len(minY) < 2:
            minY = "0" + minY
        if len(secY) < 2:
            secY = "0" + secY
        secY += EorW

        # abs() remove negative from degrees, was only needed for if-else above
        return degX + minX + secX, degY + minY + secY


    def process(self):
        # Set of UICs for stations in  dic_with_lat_long
        count_bne =0
        for index, line in enumerate(self.list_with_lat_long):
            if len(line) < 7:
                raise IndexError(
                    messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                                      " is insert the wrog one ".format(
                        str(file_with_lat_long))))
                return
            if len(line[6]) > 20:
                count_bne+=1

            #for no count the first 2 number of uic like 118101729, 8101729
            if line[1] == "Generic" or line[1] == "":
                continue
            if len(line[4])>7:
                update = line[4]
                line[4] = update[2:]
            self.dic_with_lat_long[line[4]] = index
            fix_lat = []
            check_cord = False
            uic_desc_line = line
            if line[2].__contains__("."):
                check_cord = True
                new_lat = float(line[2])
                new_long = float(line[3])
                fix_lat = self.todms(new_lat, new_long)
                uic_desc_line[2] = fix_lat[0]
                uic_desc_line[3] = fix_lat[1]
            self.list_with_lat_long[index] = uic_desc_line
        print("name more then 20 BNE : ", count_bne)
        # Set of UICs for stations in  list_rail_location_provider
        for index, line in enumerate(self.list_with_searchable):
            if len(line) < 7:
                raise IndexError(
                    messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                                      " is insert the wrog one ".format(
                        str(file_with_searchable))))
                return
            self.dic_with_searchable[line[3]] = index
        count_find = 0
        count_not_find = 0
        count_find_uic_lat = 0
        count_not_find_uic_lat = 0
        # Iterate through rail location
        for index, line in enumerate(self.list_rail_location_provider):
            if len(line) < 16:
                raise IndexError(
                    messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                                      " is insert the wrog one ".format(
                        str(file_rail_location_provider))))
                return
            new_line = line
            uic = new_line[2]
            #print(self.dic_with_lat_long[uic])
            if uic in self.dic_with_lat_long.keys():
                count_find_uic_lat +=1
                new_lat = self.list_with_lat_long[self.dic_with_lat_long[line[2]]][3]
                new_long = self.list_with_lat_long[self.dic_with_lat_long[line[2]]][2]
                #print(new_lat , " ", new_long )
                new_line[8] = new_lat
                new_line[9] = new_long
            else:
                count_not_find_uic_lat+= 1

            if uic in self.dic_with_searchable.keys():
                count_find +=1
                new_searchable = self.list_with_searchable[self.dic_with_searchable[line[2]]][4]
                if new_searchable == "N":
                    new_line[20] = "2"
                else:
                    if new_searchable == "Y":
                        new_line[20] = "1"
            else:
                count_not_find+=1
            self.new_list_rail_location_provider.append(new_line)

        print("with searchable uic not find : ", count_not_find ,"uic find : " , count_find)
        print("with lat and long uic not find : ", count_not_find_uic_lat, "uic find : ", count_find_uic_lat)

        print("size rail location provider",len(self.new_list_rail_location_provider))

        count_not_equal = 0
        len_more = 0
        # Store output
        with open(rail_location_provider,'w') as output:
            for i in self.new_list_rail_location_provider:
                i[20] = str(i[20]).replace("\n","")
                if i[4] != i[5]:
                    count_not_equal+=1
                    self.different_name.append(i)
                if len(i[5])>20:
                    len_more+=1
                    update = i[5]
                    i[5] = update[:20]
                output.write("|".join(i)+"\n")

        with open(different_name,'w') as output:
            for i in self.different_name:
                output.write("|".join(i)+"\n")

        print("count name different find : ",count_not_equal)
        print("len more then 20 : ", len_more)

if __name__=="__main__":
    process = process()
    process.process()