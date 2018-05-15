#!/usr/bin/env python
# coding: utf-8
 
import os
import codecs
from difflib import SequenceMatcher
from tkinter import messagebox

class NvsFileProcessor:
 
    def __init__(self):
        ### INPUT FILES ###
        stations_to_remove_file = os.path.dirname(os.path.abspath("")) +  "/2-updatenvsfile/in/stations_to_remove.csv"
        description_to_update_file = os.path.dirname(os.path.abspath("")) +  "/2-updatenvsfile/in/stations_existing_with_changes.csv"
        self.nvs_locations_input_file = os.path.dirname(os.path.abspath("")) +  "/2-updatenvsfile/in/rail-location-provider.csv"  # Latest NVS CSV file from https://rndwww.nce.amadeus.net/confluence/display/S1CP/Provider+Csv+Files
        self.nvs_mapper_input_file = os.path.dirname(os.path.abspath("")) +  "/2-updatenvsfile/in/rail-location-mapper.csv"  # Latest NVS CSV file from https://rndwww.nce.amadeus.net/confluence/display/S1CP/Provider+Csv+Files
        location_to_add_mapping_founds = os.path.dirname(os.path.abspath("")) +  "/2-updatenvsfile/in/mappings_founds.csv"
        location_to_add_no_mapping_founds = os.path.dirname(os.path.abspath("")) +  "/2-updatenvsfile/in/no_mappings_founds.csv"  # add to the colum 3 the location code (1 or 2)
        input_file_location_code = os.path.dirname(os.path.abspath("")) + "/2-updatenvsfile/in/stations_existing_unchanged.csv"

        ### OUTPUT FILES ###
        self.nvs_locations_output_file = os.path.dirname(
            os.path.abspath("")) + "/3-prepare_provider_files/in/rail-location-provider.csv"
        self.nvs_mapper_output_file = os.path.dirname(
            os.path.abspath("")) + "/3-prepare_provider_files/in/rail-location-mapper.csv"

        with open(self.nvs_locations_input_file) as ip:
            self.nvs_locations_input = [row.split("|") for row in ip]
        with open(self.nvs_mapper_input_file) as ip:
            self.nvs_mapper_input = [row.split("|") for row in ip]
        with open(stations_to_remove_file) as ip:
            self.stations_to_remove = [row.split("|") for row in ip]
        with open(input_file_location_code) as ip:
            self.input_list_location_code = [row.split("|") for row in ip]
        with open(description_to_update_file) as ip:
            self.description_to_update = [row.split("|") for row in ip]
        with open(location_to_add_mapping_founds) as ip:
            self.location_to_add_mapping_found = [row.split("|") for row in ip]
        with open(location_to_add_no_mapping_founds) as ip:
            self.location_to_add_no_mapping_founds = [row.split("|") for row in ip]

        self.location_to_add = []

        self.uics_new_list = {}
        self.input_list_location_code_dic = {}

        if len(self.location_to_add_mapping_found) == 0 or len(self.location_to_add_mapping_found[0]) >= 18 :
            for line in self.location_to_add_mapping_found:
                self.location_to_add.append(line)
        else:
            raise IndexError(messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                                               " is insert the wrog one ".format(
                str(location_to_add_mapping_founds))))
        if len(self.location_to_add_no_mapping_founds) == 0 or len(self.location_to_add_no_mapping_founds[0]) >= 18:
            for line in self.location_to_add_no_mapping_founds:
                if line[0] == "ADDRESS":
                    continue
                self.location_to_add.append(line)
        else:
            raise IndexError(messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                                               " is insert the wrog one ".format(
                str(location_to_add_no_mapping_founds))))
        #print(len(self.location_to_add)," = len station to add ")

        self.uics_to_remove = set()
        self.desc_to_update = {} # <UIC, New description>
        
        self.nvs_locations_output = []
        self.nvs_mapper_output = []
               
    def processUpdateCsvs(self):
        if len(self.stations_to_remove) != 1:
            # Set of UICs to remove
            for line in self.stations_to_remove:
                # print(line)
                try:
                    self.uics_to_remove.add(line[2])
                except IndexError:
                    messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                                      " is insert the wrog one ".format(str(stations_to_remove_file)))
                    return

        if len(self.description_to_update) >=2 or len(self.description_to_update) == 0 :
            # Map of new descriptions
            for line in self.description_to_update:
                self.desc_to_update[line[0]] = line[1]
        else:
            raise IndexError(messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                                               " is insert the wrog one ".format(
                str(description_to_update_file))))
            return

        for line in self.input_list_location_code:
            try:
                self.input_list_location_code_dic[line[0]] = line[2]
            except IndexError:
                messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                                  " is insert the wrog one ".format(str(input_file_location_code)))
                return

        # iterate through locations file
        for line in self.nvs_locations_input:
            try :
                # Update description if needed
                if line[2] in self.desc_to_update.keys():
                    line[4] = self.desc_to_update[line[2]] # Long desc
                    line[5] = self.desc_to_update[line[2]][:20] # Short desc]
			    # If need to delete...
                if line[2] not in self.uics_to_remove:
                    self.nvs_locations_output.append(line)
            except IndexError:
                messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                              " is insert the wrog one ".format(str(self.nvs_locations_input_file)))
                return

        # if need add....
        provider_line = self.nvs_locations_input[0]
        provider = provider_line[0]
        for line in self.location_to_add:
            appo = [""] * len(line)
            appo.append("\n")
            appo[0] = provider
           # print(line)
            appo[1] = str(line[20]).strip()
            appo[2] = line[19]
            appo[3] = line[11]
            appo[4] = line[7]
            appo[14] = line[5]
            appo[5] = line[8]
            appo[6] = line[13]
            appo[9] = line[14]
            appo[8] = line[12]
            if line[3] == '':
                raise ValueError("the location code field is empty!!")
            appo[20] = line[3]
            line = appo
            self.nvs_locations_output.append(line)
        #update the location code from station existing unchange
        for line in self.nvs_locations_output :
            if line[2] in self.input_list_location_code_dic.keys():
                line[6] = self.input_list_location_code_dic[line[2]]
                #print(line)

        # iterate through mapping file
        for line in self.nvs_mapper_input:
            try:
            # If need to delete...
                if line[1] not in self.uics_to_remove:
                    self.nvs_mapper_output.append(line)
            except IndexError:
                messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                          " is insert the wrog one ".format(str(self.nvs_mapper_input_file)))
                return

    #if need add...
        for line in self.location_to_add:
            appo = [""] * len(line)
            appo.append("\n")
            appo[0] = str(line[20]).replace("\n","")
            appo[1] = line[19]
            appo[2] = line[11]
            if line[18] != "FRR":
                appo[3] = line[19]
            else:
                #when the provider id frr in the mapper we shold have a code with 5 characterin the 4° column
                for code in self.nvs_mapper_input:
                    if code[1] == line[19]:
                        appo[3] = code[3]
                        break
                    else:
                        appo[3] = ""
            appo[6] = line[18]
            line = appo
            self.nvs_mapper_output.append(line)

        # Store output
        with open(self.nvs_locations_output_file,'w') as output:
            for i in self.nvs_locations_output:
                i[7] = "CET"
                output.write("|".join(i))
        with open(self.nvs_mapper_output_file,'w') as output:
            for i in self.nvs_mapper_output:
                if not str(i[6]).__contains__("\n"):
                    i[6]=i[6]+"\n"
                i = i[:7]
                output.write("|".join(i))

if __name__=="__main__":
    nvs_processor = NvsFileProcessor()
    nvs_processor.processUpdateCsvs()