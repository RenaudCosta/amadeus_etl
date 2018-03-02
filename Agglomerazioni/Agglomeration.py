#!/usr/bin/env python
# coding: utf-8

import os
import codecs
import math

### INPUT FILES ###
file_with_name = "in/Eva_nomi.txt"
eva_rail_location_provider = "in/rail-location-provider.csv"
other_mapping = "in/locations_with_mapping_other_EVA.csv"

### OUTPUT FILES ###
output_file = "out/output.csv"
output_file_not_in_eva = "out/output_file_not_in_eva.csv"
station_in_other_mapping = "out/station_in_other_mapping.csv"
file_new_station = "out/new_station_for_eva.csv"


class process:

    '''
    class for determinate if a station is an agglomeration or not, and the idea is to check if the name of the station
    is uppercase or not , is yes so should be an agglomeration, and the script set the correct value for that station,
    26 or 29 are the values.
    - list_output , is the result

    Clear the value from character like - and '

    And next two other file in output:
    - station not in example "eva" , which mean the station filtered from the input file eva with the list_output that
    are agglomerations

    - station_in_other_mapping ,  the station except example "eva"
    '''

    def __init__(self):
        with open(file_with_name) as ip:
            self.list_with_name = [row.split(" ") for row in ip]
        with open(eva_rail_location_provider) as ip:
            self.list_eva_rail_location_provider = [row.split(",") for row in ip]
        with open(other_mapping) as ip:
            self.list_other_mapping = [row.split("|") for row in ip]

        self.list_output = []
        self.list_new_station = []
        self.list_output_not_in_eva = []
        self.list_station_in_other_mapping = []

        self.dic_eva_rail_provider = {}
        self.other_mapping = {}
        self.other_mapping_by_name = {}
        self.duplicate = {}
        self.dic_station_in_other_mapping = {}
        self.dic_station_in_other_mapping_name = {}

    def process(self):
        for index, line in enumerate(self.list_eva_rail_location_provider):
            self.dic_eva_rail_provider[line[2]] = index

        for index, line in enumerate(self.list_other_mapping):
                #for remove the " ' and -
            if line[7].__contains__("-"):
                char = line[7].split("-")
                if line[7].__contains__("'"):
                    line[7] = char[0].replace("'", "")
                    print(line[7])
                else: line[7] = char[0]
                self.list_other_mapping[index] = line
            self.other_mapping[line[19]] = line
            self.other_mapping_by_name[line[7]] = line

        for line in self.list_with_name:
            new_line = line
            if line[5].isupper():
                if len(line) > 6:
                    if line[6].isupper():
                        union = ""
                        for index,p in enumerate(line):
                            if index >= 5:
                                union += line[index]+" "
                        new_line[5] = union
                        new_line = line[:6]
                        char = new_line[5].split("-")
                        new_line[5] = char[0].replace("\n","")
                        self.list_output.append(new_line)
                else:
                    char = new_line[5].split("-")
                    new_line[5] = char[0].replace("\n","")
                    #print(new_line)
                    self.list_output.append(new_line)

        for index, line in enumerate(self.list_output):
            if line[0] not in self.dic_eva_rail_provider.keys():
                self.list_output_not_in_eva.append(line)

        for index, line in enumerate(self.list_output_not_in_eva):
            if line[0] in self.other_mapping.keys():
                if self.other_mapping[line[0]][13] == "26" or self.other_mapping[line[0]][13] == "":
                    self.list_station_in_other_mapping.append(self.other_mapping[line[0]])
            if line[5] in self.other_mapping_by_name.keys():
                if self.other_mapping_by_name[line[5]][13] == "26" or self.other_mapping_by_name[line[5]][13] == "":
                    self.list_station_in_other_mapping.append(self.other_mapping_by_name[line[5]])

        #for remove duplicate
        appo = []
        for i in self.list_station_in_other_mapping:
            appo.append(i[7])
        appo = list(set(appo))
        for index, line in enumerate(self.list_station_in_other_mapping):
            self.duplicate[line[7]] = line
        self.list_station_in_other_mapping = []
        for line in appo:
            if line in self.duplicate.keys():
                self.list_station_in_other_mapping.append(self.duplicate[line])

        for n in self.list_station_in_other_mapping:
            self.dic_station_in_other_mapping[n[19]] = line
            self.dic_station_in_other_mapping_name[n[7]] = line

        for line in self.list_output_not_in_eva:
            if line[0] not in self.dic_station_in_other_mapping.keys():
                if line[5] not in self.dic_station_in_other_mapping_name.keys():
                    self.list_new_station.append(line)

        with open(output_file_not_in_eva, 'w') as output:
            for i in self.list_output_not_in_eva:
                output.write("|".join(i) + "\n")
        with open(station_in_other_mapping,'w') as output:
            for i in self.list_station_in_other_mapping:
                output.write("|".join(i))
        with open(file_new_station,'w') as output:
            for i in self.list_new_station:
                output.write("|".join(i)+"\n")
        with open(output_file,'w') as output:
            for i in self.list_output:
                output.write("|".join(i)+"\n")

if __name__== "__main__":
    process = process()
    process.process()