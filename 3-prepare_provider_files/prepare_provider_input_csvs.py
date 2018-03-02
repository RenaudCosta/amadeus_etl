#!/usr/bin/env python
# coding: utf-8
 
import os
from difflib import SequenceMatcher
from tkinter import messagebox

class PrepareCheckOutput:
 
    def __init__(self):
        ### INPUT FILES ###
        mappings_found_file = os.path.dirname(os.path.abspath("")) +  "/3-prepare_provider_files/in/mappings_founds.csv"  # Mapping created in step 1-process_mappings
        mappings_created_file =os.path.dirname(os.path.abspath("")) +  "/3-prepare_provider_files/in/mappings_created.csv"  # Mappings created in step 2-prepare_ama_files
        self.to_be_unmapped_file =os.path.dirname(os.path.abspath("")) +  "/3-prepare_provider_files/in/mappings_to_remove.csv"  # Mapping invalidated in step 1-process_mappings
        provider_location_input_file = os.path.dirname(os.path.abspath("")) + "/3-prepare_provider_files/in/rail-location-provider.csv"  # Latest provider CSV file from https://rndwww.nce.amadeus.net/confluence/display/S1CP/Provider+Csv+Files
        provider_mapper_input_file = os.path.dirname(os.path.abspath("")) + "/3-prepare_provider_files/in/rail-location-mapper.csv"  # Latest provider CSV file from https://rndwww.nce.amadeus.net/confluence/display/S1CP/Provider+Csv+Files

        ### OUTPUT FILES ###
        self.provider_location_output_file = os.path.dirname(
            os.path.abspath("")) + "/script_check_output/in/rail-location-provider.csv"
        self.provider_mapper_output_file = os.path.dirname(
            os.path.abspath("")) + "/script_check_output/in/rail-location-mapper.csv"

        with open(provider_location_input_file) as ip:
            self.provider_locations = [row.split("|") for row in ip]
        with open(provider_mapper_input_file) as ip:
            self.provider_mapper = [row.split("|") for row in ip]
            
        with open(mappings_found_file) as ip:
            self.mappings_found = [row.split("|") for row in ip]
        with open(mappings_created_file) as ip:
            self.mappings_created = [row.split("|") for row in ip]
        with open(self.to_be_unmapped_file) as ip:
            self.to_be_unmapped = [row.split("|") for row in ip]
        
        self.locations_to_be_unmapped = set() # In format {UIC}-{CODECONTEXT}, e.g. "8006900-UIC"
        self.locations_to_be_mapped = {}# In format {UIC-CODECONTEXT}->{GLC}, e.g. "8006900-UIC"->"80G0005"
               
    def processCheckOutput(self):
        # List locations to be mapped
        for line in self.mappings_found:
            if len(line) < 15 :
                raise IndexError(
                    messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                                      " is insert the wrog one ".format(
                        str(mappings_found_file))))
                return
            location_key = line[19]+"-"+line[20].strip()
            location_glc = line[11]
            self.locations_to_be_mapped[location_key] = location_glc
        for line in self.mappings_created:
            if len(line) < 1:
                raise IndexError(
                    messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                                      " is insert the wrog one ".format(
                        str(mappings_created_file))))
                return
            location_key = line[0]
            location_glc = line[1].strip()
            self.locations_to_be_mapped[location_key] = location_glc
            
        # List locations to be unmapped
        for line in self.to_be_unmapped:
            print(line)
            if len(line) == 0 or len(line)<15:
                raise IndexError(
                    messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                                      " is insert the wrog one ".format(
                        str(self.to_be_unmapped_file))))
                return
            location_key = line[19]+"-"+line[20].strip()
            self.locations_to_be_unmapped.add(location_key)
        
        # Process provider location list
        for line in self.provider_locations:
            if len(line) < 15:
                raise IndexError(
                    messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                                      " is insert the wrog one ".format(
                        str(provider_location_input_file))))
                return
            location_key = line[2]+"-"+line[1]
            # If we need to map, set its GLC to the right value
            if location_key in self.locations_to_be_mapped.keys():
                line[3] = self.locations_to_be_mapped[location_key]
                print(line[3])
            # If we need to unmap, set its GLC to '0000000'
            if location_key in self.locations_to_be_unmapped:
                line[3] = '0000000'

        # Process provider mapper list
        for line in self.provider_mapper:
            if len(line) < 6:
                raise IndexError(
                    messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                                      " is insert the wrog one ".format(
                        str(provider_mapper_input_file))))
                return
            location_key = line[1]+"-"+line[0]
            # If we need to map, set its GLC to the right value
            if location_key in self.locations_to_be_mapped.keys():
                line[2] = self.locations_to_be_mapped[location_key]
           # else:
            #    self.provider_mapper.append(location_key)
            # If we need to unmap, set its GLC to '0000000'
            if location_key in self.locations_to_be_unmapped:
                line[2] = '0000000'
        
        # Store output
        with open(self.provider_location_output_file,'w') as output:
            provided = self.provider_locations[1]
            for i in self.provider_locations:
                i[0] = provided[0]
                i[7] = provided[7]
                if len(i[3]) == 6:
                    appo = str(i[3])
                    i[3] = "0" + appo

                if len(i[2]) == 6:
                    appo = str(i[2])
                    i[2] = "0"+appo
                    i[3] = i[2]
                #print(i)
                output.write("|".join(i))

        with open(self.provider_mapper_output_file,'w') as output:
            provider = self.provider_mapper[0]
            for i in self.provider_mapper:
                if len(i[1]) == 6:
                    appo = str(i[1])
                    i[1] = "0"+appo
                if len(i[2]) == 6:
                    appo = str(i[2])
                    i[2] = "0"+appo
                if len(i[3]) == 6:
                    appo = str(i[3])
                    i[3] = "0"+appo
                if i[6] == "":
                    i[6] = provider[6]
                i = i[:7]
                if not i[6].__contains__("\n"):
                    i[6]+="\n"
                output.write("|".join(i[:7]))

if __name__== "__main__":
    prov_checkOutput = PrepareCheckOutput()
    prov_checkOutput.processCheckOutput()