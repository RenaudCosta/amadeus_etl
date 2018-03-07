#!/usr/bin/env python
# coding: utf-8

import os
import codecs
import math
from difflib import SequenceMatcher

### INPUT FILES ###
file_provider_nvs = "in/rail-location-provider-nvs.csv"
file_provider_bne = "in/rail-location-provider-bne.csv"
file_mapper_bne = "in/rail-location-mapper-bne.csv"

### OUTPUT FILES ###
file_provider_bne_output = "out/rail-location-provider-bne.csv"
file_mapper_bne_output = "out/rail-location-mapper-bne.csv"


class process:
    '''
    input: 2 list one with correct 1a and one to fix it and one file that contains the mapper
    this class do a comparision between the provider nvs and provider bne  (is an example), for find out if there are
    some 1a that not is equal to the same station into the nvs 1a column (that in this case is the correct list)

    the idea is :  there are 3 case that is handle
                    1- same uic and same long name (easy)
                    2- different uic but same name (with binary research)
                    3- different both name and uic (so i have use a name similarity and in particular the name
                    must be similar to the 90% and the first 4 character are the same)
    so in the end you have a output list with a provider format fixed
    and a mapper too
    '''

    def __init__(self):
        with open(file_provider_nvs) as ip:
            self.list_provider_nvs = [row.split("\t") for row in ip]
        with open(file_provider_bne) as ip:
            self.list_provider_bne = [row.split("\t") for row in ip]
        self.bne_original = self.list_provider_bne[:]
        with open(file_mapper_bne) as ip:
            self.list_mapper_bne = [row.split("\t") for row in ip]
        self.list_provider_bne_output = []
        self.list_provider_bne_not_match = []
        self.mapper_bne_output = []
        self.list_provider_bne_output_no_duplicate = []

        self.dic_provider_nvs = {}
        self.dic_provider_nvs_with_name = {}
        self.dic_provider_output = {}

    # binary search by name
    def binSearch(self, lst, target):
        min = 0
        max = len(lst) - 1
        avg = int((min + max) / 2)
        while min < max:
            if target == lst[avg]:
                return avg
            elif (lst[avg] < target):
                return avg + 1 + self.binSearch(lst[avg + 1:], target)
            else:
                return self.binSearch(lst[:avg], target)
        return avg

    def process(self):
        list_provider_nvs_only_long_name = []
        list_provider_bne_only_long_name = []

        for line in self.list_provider_nvs:
            self.dic_provider_nvs[line[2]] = line  # key uic, value the line
            self.dic_provider_nvs_with_name[line[4]] = line #key name , value line
            list_provider_nvs_only_long_name.append(line[4]) #for create a list only with the name
        for line in self.list_provider_bne:
            list_provider_bne_only_long_name.append(line[4])

        list_provider_nvs__name_sorted = sorted(list_provider_nvs_only_long_name)

        list_remove = []
        for line in self.list_provider_bne:
            if line[2] in self.dic_provider_nvs.keys():
                dic_line = self.dic_provider_nvs[line[2]]
                if line[4] == dic_line[4]:
                    line[3] = dic_line[3]  # case where the uic are = and long desc too
                    #print(line)
                    #self.list_provider_bne_output.append(line)
                    list_remove.append(line)
                    self.list_provider_bne.remove(line)
            else:
                # case where the uic are different but exist a name equal into the list
                indexElementFoundid = self.binSearch(list_provider_nvs__name_sorted, line[4])
                name = list_provider_nvs__name_sorted[indexElementFoundid]
                if name == line[4]:
                    #get the name from idex , and find it into the dic with name how key, for replace into the provider bne
                    line[3] = self.dic_provider_nvs_with_name[list_provider_nvs__name_sorted[indexElementFoundid]][3]
                    #print(line)
                    #self.list_provider_bne_output.append(line)
                    list_remove.append(line)
                    self.list_provider_bne.remove(line)

                #case uic different and name is not perfect == , so try to find into the nvs list a station name with
                #70% of similarity
                else:
                    best_match_index = 0
                    best_mapping_found = ""
                    isFound = False
                    for nameLine in self.list_provider_nvs:
                        transformed_name_bne = line[4].strip().upper().translate(
                            str.maketrans("", "", "()-, ?.!/;:")).replace("ü", "UE").replace("ö", "OE").replace("ä",
                                                                                                            "AE").replace(
                            "ß", "SS")
                        transformed_name_nvs = nameLine[4].strip().upper().translate(
                            str.maketrans("", "", "'\()-, ?.!/;:")).replace("ü", "UE").replace("ö", "OE").replace("ä",
                                                                                                            "AE").replace(
                            "ß", "SS")

                        if transformed_name_bne[:4] == transformed_name_nvs[:4]:
                            match_index = SequenceMatcher(None, transformed_name_bne,
                                                          transformed_name_nvs).ratio()
                            if match_index > 0.9:
                                if match_index > best_match_index:
                                    best_mapping_found = nameLine
                                    best_match_index = match_index
                                    #print(nameLine)
                                    isFound = True

                    if isFound:
                        #print(line)
                        line[3] = best_mapping_found[3]
                        #self.list_provider_bne_output.append(line)
                        list_remove.append(line)
                        self.list_provider_bne.remove(line)
                        #print(line,"\n\n")
            self.list_provider_bne_output.append(line)

        for line in list_remove :
            self.list_provider_bne_output.append(line)

        dic_remove = {}
        # for remove the duplicate inside the output list
        for line in self.list_provider_bne_output:
            dic_remove[line[2]] = line
        # create a new list with no duplicate
        for line in dic_remove:
            #print(dic_remove.get(line))
            self.list_provider_bne_output_no_duplicate.append(dic_remove.get(line))

        # prepare the mapper with the fixing
        for line in self.list_provider_bne_output_no_duplicate:
            self.dic_provider_output[line[2]] = line

        for line in self.list_mapper_bne:
            if line[1] in self.dic_provider_output.keys():
                line[2] = self.dic_provider_output[line[1]][3]
        #print(len(list_remove))
        #print(len(self.list_provider_bne_output)," ")
        #print(len(self.list_provider_bne_output_no_duplicate))

        #for add the station that is not change
        for line in self.bne_original:
            if line [2] not in self.dic_provider_output:
                self.list_provider_bne_output_no_duplicate.append(line)

        #print(len(self.list_provider_bne_output_no_duplicate))

        # OUTPUT
        with open(file_provider_bne_output, 'w') as output:
            for index, i in enumerate(self.list_provider_bne_output_no_duplicate):
                output.write("|".join(i))
        with open(file_mapper_bne_output, 'w') as output:
            for index, i in enumerate(self.list_mapper_bne):
                output.write("|".join(i))

if __name__ == "__main__":
    process = process()
    process.process()
