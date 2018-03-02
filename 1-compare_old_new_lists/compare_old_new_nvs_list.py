#!/usr/bin/env python
# coding: utf-8

import os
import codecs
import math
import re

'''
for import the others class in each step in the process for generate the 1a
'''

import sys
sys.path.insert(0,os.path.dirname(os.path.abspath(""))+"/1-process_mappings/")
sys.path.insert(0,os.path.dirname(os.path.abspath(""))+"/2-prepare_ama_files/")
sys.path.insert(0,os.path.dirname(os.path.abspath(""))+"/2-updatenvsfile/")
sys.path.insert(0,os.path.dirname(os.path.abspath(""))+"/3-prepare_provider_files/")
sys.path.insert(0,os.path.dirname(os.path.abspath(""))+"/script_check_output/")

#TODO finire di inserire gli altri step
import process_mappings as step2mapping
import prepare_ama_input_csv as step3prepare_ama
import update_nvs_input_csvs as step4update_input_csvs
import prepare_provider_input_csvs as step5prepare_provider_input
import check_provider_output as step6check_provider_output
from tkinter import messagebox

### INPUT FILES ###
old_file_list_file = "in/old_file_list.csv"  # select * from rail_location_prov lp join rail_location_mapper mp on lp.DATA_OWNER=mp.DATA_OWNER and lp.code_value = mp.code_value where lp.DATA_OWNER = 'NVS'
new_file_list_file = "in/new_file_list.csv"

### OUTPUT FILES ###
stations_existing_unchanged_file = os.path.dirname(os.path.abspath(""))+"/2-updatenvsfile/in/stations_existing_unchanged.csv"
stations_existing_with_changes_file = os.path.dirname(os.path.abspath(""))+"/2-updatenvsfile/in/stations_existing_with_changes.csv"
stations_to_add_file = os.path.dirname(os.path.abspath(""))+"/1-process_mappings/in/location_to_map.csv"
stations_to_remove_file = os.path.dirname(os.path.abspath(""))+"/2-updatenvsfile/in/stations_to_remove.csv"

class NvsListProcessor:

    '''
    compare the old file with a new file for filter the new station, idea is just to check if the uic code is already
    present in the old_list, if no so is a new station. This step is important for reduce the amount of time that the
    mapper step take for run.

    Where is necessary fix the lat and long with the correct value  column 3°lat and 4°long

    And if is necessary update the railway to 29 and city to 26

    +there is a check in the NEW file in input, that not allow the missing value inside the columns
    +send automatically the output file of this script in the in/ file for the next script that need that file in input

    :parameter in the 2° column should be the UIC, for the old file!!!:
    :parameter in the 0° column should be the UIC, for the new file!!!:
    '''

    def __init__(self):
        with open(old_file_list_file) as ip:
            self.old_nvs_list = [row.split("\t") for row in ip]

        with open(new_file_list_file) as ip:
            self.new_nvs_list = [row.split("\t") for row in ip]

        self.uics_old_list = {} # <UIC, index in list>
        self.uics_new_list = {} # <UIC, index in list>
        self.stations_existing_unchanged = []
        self.stations_existing_with_changes = []
        self.stations_to_add = []
        self.stations_to_remove = []

    def todms(self,longitude, latitude):
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


    def process(self):
        # Set of UICs for stations in old list
        for index, line in enumerate(self.old_nvs_list):
            if len(line) < 9:
                raise IndexError(
                    messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                                      " is insert the wrog one ".format(
                        str(old_file_list_file))))
                return
            self.uics_old_list[line[2]] = index

        # Set of UICs for stations in new list
        for index, line in enumerate(self.new_nvs_list):
            if len(line) < 10:
                raise IndexError(
                    messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                                      " is insert the wrog one ".format(
                        str(new_file_list_file))))
                return
            '''   
            this line must be like that example => "8302642	Pozzallo	railway	36,733606	14,84717	8312420
            Pozzallo	railway		IT	1"
            
            '''

            for indexIntern,  i in enumerate(line) :
                if not  i and indexIntern != 8:
                    raise ValueError(messagebox.showwarning("WARNING", "pls check the line {0} can't be empty !!\n\n"
                                                                       "file = {3}\n\n"
                                                                       "line = {1}\n\n"
                                                                       "value missing in column = {2}"
                                                            .format(index+1,line,indexIntern+1,str(new_file_list_file))))
            if line[0].__contains__("TH type"):
                continue
            if line[2] == "railway" or line[2] == "no":
                line[2] = "29"
                line[7] = ""
            elif line[2] == "city" or line[2] == "yes":
                line[2] = "26"
                line[7] = ""
            self.uics_new_list[line[0]] = index

        # Iterate through new locations
        for index, line in enumerate(self.new_nvs_list):
            uic_desc_line = line
            pattern = r"|"
            uic_desc_line[1] = re.sub(pattern,"",uic_desc_line[1])
            line[1] = uic_desc_line[1]
            fix_lat=[]
            check_cord = False
            if line[3].__contains__(","):
                check_cord = True
                new_lat = float(line[3].replace(",","."))
                new_long = float(line[4].replace("\n", "").replace(",","."))
                fix_lat = self.todms(new_lat, new_long)
                uic_desc_line[3] = fix_lat[0]
                uic_desc_line[4] = fix_lat[1]

            # Is stations exists also in old list
            if line[0] in self.uics_old_list.keys():
                # if description and domestic code are the same, put into existing locations with no changes
                new_uic = line[0]
                old_uic = self.old_nvs_list[self.uics_old_list[line[0]]][2]
                old_lat = self.old_nvs_list[self.uics_old_list[line[0]]][12]
                old_long = self.old_nvs_list[self.uics_old_list[line[0]]][14]

                if new_uic == old_uic:
                    self.stations_existing_unchanged.append(line)
                else:
                    # Only take the 2 first field (UIC and description)
                    self.stations_existing_with_changes.append(uic_desc_line)
            # else we it is a new station
            else:
                uic_desc_line = line[:11]
                uic_desc_line[7].replace("\n","")
                self.stations_to_add.append(uic_desc_line)

        # Iterate through old locations
        for index, line in enumerate(self.old_nvs_list):
            self.owner = line[0]
            if line[19] == "CODE_VALUE":
                continue
            # Is stations does not exists in new list, it is a station to be deleted
            if line[2] not in self.uics_new_list.keys():
                self.stations_to_remove.append(line)

        print("station into old: ", str(len(self.old_nvs_list)))
        print("station to remove: ", str(len(self.stations_to_remove)))
        print("station into new: ", str(len(self.new_nvs_list)))
        print("station to add: ", str(len(self.stations_to_add)))

        # Store output
        with open(stations_existing_unchanged_file,'w') as output:
            for i in self.stations_existing_unchanged:
                if str(i).__contains__("|"):
                    appo = str(i[1]).replace("|"," ")
                    i[1] = appo
                output.write("|".join(i))
        with open(stations_existing_with_changes_file,'w') as output:
            for i in self.stations_existing_with_changes:
                output.write("|".join(i)+"\n")
        with open(stations_to_add_file,'w') as output:
            for i in self.stations_to_add:
                if str(i).__contains__("|"):
                    appo = str(i[1]).replace("|"," ")
                    i[1] = appo
                #format the columns in the correct allocations, for to fit in input to the mapper
                newLine = [""]*21
                newLine[1] = "CET"
                newLine[3] = str(i[10]).replace("\n","")
                newLine[5] = i[9]
                newLine[7] = i[1]
                newLine[8] = i[6]
                newLine[11] = "0000000"
                newLine[12] = i[3]
                newLine[13] = i[2]
                newLine[14] = i[4]
                newLine[18] = self.owner
                newLine[19] = i[0]
                newLine[20] = "UIC\n"
                output.write("|".join(newLine))
        try:
            with open(stations_to_remove_file,'w') as output:
                    for i in self.stations_to_remove:
                        output.write("|".join(i))
        except FileNotFoundError:
            messagebox.showerror("ERROR", "pls check the path of stations_to_remove.csv !!")
            return

if __name__== "__main__":
    nvs_list_processor = NvsListProcessor()
    nvs_list_processor.process()

    providerMapping = step2mapping.ProcessMapping()
    providerMapping.processMapping()

    prepareAMA = step3prepare_ama.AmaFileProcessor()
    prepareAMA.processAma()

    nvs_processor = step4update_input_csvs.NvsFileProcessor()
    nvs_processor.processUpdateCsvs()

    prov_processor = step5prepare_provider_input.PrepareCheckOutput()
    prov_processor.processCheckOutput()

    procesCheckOutput = step6check_provider_output.CheckOuputProvider()
    procesCheckOutput.processCheckOutput()