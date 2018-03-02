#!/usr/bin/env python
# coding: utf-8
 
import os
from difflib import SequenceMatcher
from tkinter import messagebox


class AmaFileProcessor:

    def __init__(self):
        ### INPUT FILES ###
        no_mappings_found_file = os.path.dirname(os.path.abspath("")) +  "/2-prepare_ama_files/in/no_mappings_founds.csv"  # Locations with no mapping found in step 1-process_mappings
        ama_locations_input_file = os.path.dirname(os.path.abspath("")) +  "/2-prepare_ama_files/in/rail-location-ama.csv"  # Latest AMA CSV file from https://rndwww.nce.amadeus.net/confluence/display/S1CP/Provider+Csv+Files

        ### OUTPUT FILES ###
        self.ama_location_output_file = os.path.dirname(os.path.abspath("")) + "/2-prepare_ama_files/out/rail-location-ama.csv"
        self.mappings_created_file = os.path.dirname(os.path.abspath(
            "")) + "/3-prepare_provider_files/in/mappings_created.csv"  # New mappings created (GLC generated for each new AMA station), to be used in step 3-prepare_provider_files

        with open(ama_locations_input_file) as ip:
            self.ama_locations = [row.split("|") for row in ip]
        with open(no_mappings_found_file) as ip:
            self.no_mappings_found = [row.split("|") for row in ip]
        
        self.glcs_in_use = set()
        self.glc_sequence_number = {}
        self.mappings_created = {}
        
    def generate_glc(self, uic_code):
        # First try to use the uic code itself as GLC..
        if uic_code not in self.glcs_in_use:
            return uic_code
            
        # Otherwise generate new code
        uic_country_code = uic_code[0:2]
        
        # Generated GLC should look like {First 2 chars of UIC code}G{SEQUENCE NUMBER}
        # SEQUENCE NUMBER starts from 0 and we increment until we found the resulting GLC is not yet in use
        generated_glc_code = ""
        if not self.glc_sequence_number.get(uic_country_code):
            self.glc_sequence_number[uic_country_code] = 0
        glc_code_available = False
        while not glc_code_available:
            generated_glc_code = uic_country_code + "G%04d" % self.glc_sequence_number[uic_country_code]
            self.glc_sequence_number[uic_country_code] += 1
            glc_code_available = generated_glc_code not in self.glcs_in_use
            
        self.glcs_in_use.add(generated_glc_code)

        return generated_glc_code
        
    def create_ama_location(self, provider_location, new_glc_code):
        new_ama_location = [None]*19
        new_ama_location[0] = new_glc_code # GLC
        new_ama_location[1] = provider_location[7] #DefaultLongName
        new_ama_location[2] = provider_location[8] #DefaultShortName
        new_ama_location[3] = provider_location[13] #LocationTypeCode
        new_ama_location[4] = provider_location[1] #TimeZone
        new_ama_location[5] = provider_location[12] #Latitude
        new_ama_location[6] = provider_location[14] #Longitude
        new_ama_location[7] = provider_location[0] #Address
        new_ama_location[8] = provider_location[17] #Postal code
        new_ama_location[9] = provider_location[2] #City name
        new_ama_location[10] = provider_location[4] #ProvinceStateCode
        new_ama_location[11] = provider_location[5] #CountryCode
        new_ama_location[12] = provider_location[16] #PhoneNumber
        new_ama_location[13] = provider_location[10] #FaxNumber
        new_ama_location[14] = provider_location[9] #Email
        new_ama_location[15] = provider_location[15] #MinimumConnectionTime
        new_ama_location[16] = provider_location[6] if provider_location[6] else "1234567" #DaysOfWeekOfOperation
        new_ama_location[17] = provider_location[3] #StatusCode
        new_ama_location[18] = "AMA\n" # Data owner
        
        return new_ama_location
        
    def processAma(self):
        # Set of GLCs already in use
        for line in self.ama_locations:
            if len(line) < 15:
                raise IndexError(
                    messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                                      " is insert the wrog one ".format(
                        str(ama_locations_input_file))))
                return
            self.glcs_in_use.add(line[0])
        
        # For each location to add into AMA locations
        for line in self.no_mappings_found:
            if len(line) < 15:
                raise IndexError(
                    messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                                      " is insert the wrog one ".format(
                        str(no_mappings_found_file))))
                return
            uic_code = line[19]
            code_context = line[20].strip()
            #Ignore header line
            if uic_code == "CODE_VALUE":
                continue
            # Generate new GLC for this location
            new_glc_code = self.generate_glc(uic_code)
            # Generate new AMA location item (rearrange field in right order)
            new_ama_location = self.create_ama_location(line, new_glc_code)
            # Add new mapping between location and GLC to output map
            location_key = uic_code+"-"+code_context
            self.mappings_created[location_key] = new_glc_code
            
            # Add to list of output ama locations
            self.ama_locations.append(new_ama_location)
        
        # Store output
        with open(self.ama_location_output_file,'w') as output:
            special = ["ö","ß","ü","ä","/"]
            for i in self.ama_locations:

                if len(i[2].encode('utf-8'))>19:#for count the special caracter one bit insted of 2
                    c=0
                    count = [c + 1 for n in special if n in i[2]]
                    if len(count) != 0:
                        appo = i[2]
                        i[2] = appo[:len(i[2])-len(count)*2]
                    else:
                        appo = i[2]
                        i[2] = appo[:19]
                    print(i)

                if len(i[0]) == 6:
                    appo = "0"+i[0]
                    i[0] = appo
                if len(i[0]) == 5:
                    appo = "00" + i[0]
                    i[0] = appo
                if len(i[0]) == 1:
                    appo = "000000" + i[0]
                    i[0] = appo
                output.write("|".join(i))
        with open(self.mappings_created_file,'w') as output:
            for location_key, glc in self.mappings_created.items():
                output.write(location_key+"|"+glc+"\n")                  
 
if __name__=="__main__":
    ama_processor = AmaFileProcessor()
    ama_processor.processAma()