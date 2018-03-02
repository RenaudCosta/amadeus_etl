#!/usr/bin/env python
# coding: utf-8

import os
from difflib import SequenceMatcher
from tkinter import messagebox

class ProcessMapping:

    def __init__(self):
        # select * from rail_location_prov where DATA_OWNER='EVA' and generic_location_code='0000000'
        input_file = os.path.dirname(os.path.abspath("")) + '/1-process_mappings/in/location_to_map.csv'
        # select * from rail_location_prov where DATA_OWNER='EVA' and generic_location_code<>'0000000'
        mappings_thisprovider_file = os.path.dirname(os.path.abspath("")) + '/1-process_mappings/in/locations_with_mapping.csv'
        # select * from rail_location_prov where DATA_OWNER<>'EVA' and generic_location_code<>'0000000'
        mappings_otherprov_file = os.path.dirname(os.path.abspath("")) + '/1-process_mappings/in/locations_with_mapping_other.csv'

        ### OUTPUT FILES ###

        self.mappings_found_file = os.path.dirname(os.path.abspath("")) + "/2-updatenvsfile/in/mappings_founds.csv"
        self.mappings_found_file_provider_file = os.path.dirname(
            os.path.abspath("")) + "/3-prepare_provider_files/in/mappings_founds.csv"
        self.no_mappings_found_file = os.path.dirname(os.path.abspath("")) + "/2-updatenvsfile/in/no_mappings_founds.csv"
        self.no_mappings_found_file_ama = os.path.dirname(
            os.path.abspath("")) + "/2-prepare_ama_files/in/no_mappings_founds.csv"
        self.mappings_to_remove_file = os.path.dirname(
            os.path.abspath("")) + "/3-prepare_provider_files/in/mappings_to_remove.csv"

        with open(input_file) as ip:
            self.ls = [row.split("|") for row in ip]
        with open(mappings_thisprovider_file) as ip:
            self.mappings_thisprovider = [row.split("\t") for row in ip]
        with open(mappings_otherprov_file) as ip:
            self.mappings_otherprov = [row.split("\t") for row in ip]

    def find_best_mapping(self, code_value, location_type, long_desc, data_owner, existing_mapping):
        '''
        If the input location is not mapped to any GLC (existing_mapping == ""), find the best mapping among all locations from other providers (minimum match index is 0.9)
        If the input is already mapped, get the best match between the input location and the locations from other providers mapped to the same GLC
        :param code_value:
        :param location_type:
        :param long_desc:
        :param data_owner:
        :param existing_mapping:
        :return:
        '''

        best_mapping_found = ""
        # Match quality index (the bigger the better)
        best_match_index = 0
        locations_compared = 0
        for i in self.mappings_otherprov:
            if i[0] == "ADDRESS":
                continue
            if len(i) < 15:
                raise IndexError(
                    messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                                      " is insert the wrog one ".format(
                        str(mappings_otherprov_file))))
                return

            transformed_current_desc = i[7].strip().upper().translate(str.maketrans("","","()-, ?.!/;:")).replace("ü", "UE").replace("ö", "OE").replace("ä", "AE").replace("ß", "SS")
            # Only consider as a map if location type is the same and provider not the same as input location
            # Border points specificities not taken into account for now (only TRE and BNE impacted)
            if i[13] != "29" and i[13] != "26" and i[13] != "33" and i[13] != "17" :
                raise ValueError(messagebox.showwarning("WARNING", "pls check the index of location type in other ,"
                                                      " is insert the wrog one, or is differente from 29 or 26, 17,33 "))
                return
            if len(i[11]) < 6 :
                raise ValueError(messagebox.showwarning("WARNING", "pls check the index of the generic location code ,"
                                                      " becouse the lenght is less the 7 characthers "))
                return
            if i[13] == location_type and i[18] != data_owner:
                # If mapping already exists, only compare to other location mapped to same GLC
                if not existing_mapping or (existing_mapping == i[11]):
                    locations_compared += 1
                    transformed_input_description = long_desc.strip().upper().translate(str.maketrans("","","()-, ?.!/;:")).replace("ü", "UE").replace("ö", "OE").replace("ä", "AE").replace("ß", "SS")
					# Check by UIC code + 70% name similarity
                    if i[19] == code_value:
                        stringmatch_ratio = SequenceMatcher(None, transformed_input_description, transformed_current_desc).ratio()
                        if stringmatch_ratio > 0.7:
                            match_index = 0.2 + stringmatch_ratio
                            if match_index > best_match_index:
                                best_mapping_found = i[11]# generic location code!!!!
                                best_match_index = match_index
                    # Otherwise accept mapping if first 4 characters are the same + similarity is > 90%
                    if transformed_current_desc[:4] == transformed_input_description[:4]:
                        match_index = SequenceMatcher(None, transformed_input_description, transformed_current_desc).ratio()
                        if match_index > 0.9:
                            if match_index > best_match_index:
                                best_mapping_found = i[11]# generic location code!!!!
                                best_match_index = match_index

        return [best_mapping_found, best_match_index, locations_compared]

    def find_mappings(self):
        '''
        The below method iterates every item in input_file and determines if:
        1) No mapping (GLC code) can be found for this location
        2a) A mapping (GLC code) can be found for this location
        2b) A mapping (GLC code) can be found for this location, and the existing mapping
        (another location from same provider, with same GLC as the mapping found), needs to be unmapped (set its GLC to 0000000)
        :return:
        '''

        self.mapping_found = []
        self.no_mapping_found = []
        self.to_be_unmapped = []

        for i in self.ls:
            if len(i) < 15:
                raise IndexError(
                    messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                                      " is insert the wrog one ".format(
                        str(self.mappings_found_file))))
                return

            i[11] = "0000000"
            i[20]=i[20].strip()
            long_desc = i[7]
            if len(long_desc)>15:
                appo = i[7]
                long_desc=appo[0:len(appo)-5]
            code_value = i[19]
            location_type = i[13]
            data_onwer = i[18]

            mappings_results = self.find_best_mapping(code_value, location_type, long_desc, data_onwer, "")
            mapping_found = mappings_results[0]
            match_index = mappings_results[1]
            # If no mappings found, put in not found list
            if not mapping_found:
                self.no_mapping_found.append(i)
                print (code_value+" "+long_desc+" no mapping found")
            else:
                # Substitute 0000000 with GLC found
                # for check if in the collumn is there the generic location code, else error
                if len(str(i[11])) != 7:
                    raise ValueError(messagebox.showwarning("WARNING", "in the 12 colum is not fill the generic location"
                                                                       "code, pls fix it"))
                    return
                i[11] = mapping_found
                # Check if this glc is already mapped to a location for this provider
                conflicting_location = False
                for j in self.mappings_thisprovider:
                    if len(j) < 15:
                        raise IndexError(
                            messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                                              " is insert the wrog one ".format(
                                str(mappings_thisprovider_file))))
                        return
                    if j[11] == mapping_found:
                        conflicting_location = True
                        # Try to see if the existing mapping is stronger (has better match index)
                        conflicting_code_value = j[19]
                        conflicting_long_desc = j[7]
                        conflicting_location_type = j[13]
                        conflicting_data_onwer = j[18]
                        
                        mappings_results_conflicting_location = self.find_best_mapping(conflicting_code_value, conflicting_location_type, conflicting_long_desc, conflicting_data_onwer, mapping_found)
                        conflicting_location_match_index = mappings_results_conflicting_location[1]
                        conflicting_location_number_of_comparisons = mappings_results_conflicting_location[2]
                        # If existing mapping has a better match index keep the current mapping, and put this current location into "no mapping found" list
                        # Same if conflicting location is the only location mapped to its GLC (number of comparisons == 0)
                        if conflicting_location_match_index >= match_index or conflicting_location_number_of_comparisons == 0:
                            self.no_mapping_found.append(i)
                            print (code_value+" "+long_desc+" no mapping found (conflicting location "+conflicting_code_value+" with better match index: " + str(match_index) + " vs " + str(conflicting_location_match_index) + ")")
                        # Otherwise add current location into "mapping found" and add the conflicting location into "mappings to be removed" list
                        else:
                            print (code_value+" "+long_desc+ " mapping found: " + mapping_found + " match index: " + str(match_index) + ", conflicting location "+conflicting_code_value+" (match index " + str(conflicting_location_match_index) +") to be delinked")
                            self.mapping_found.append(i) 
                            self.mappings_thisprovider.append(i)
                            j[20]=j[20].strip()
                            self.to_be_unmapped.append(j) 
                        break
                # If no conflict found...
                if not conflicting_location:
                    print (code_value+" "+long_desc+ " mapping found: " + mapping_found + " match index: " + str(match_index))
                    self.mapping_found.append(i)    
                    self.mappings_thisprovider.append(i)
                    
        my_list = [self.mapping_found, self.no_mapping_found, self.to_be_unmapped]
        return my_list

    def processMapping(self):
        output_lists = self.find_mappings()
        with open(self.mappings_found_file,'w') as output:
            for i in output_lists[0]:
                output.write("|".join(i)+"\n")
        with open(self.mappings_found_file_provider_file,'w') as output:
            for i in output_lists[0]:
                output.write("|".join(i)+"\n")
        with open(self.no_mappings_found_file,'w') as output:
            for i in output_lists[1]:
                output.write("|".join(i)+"\n")
        with open(self.no_mappings_found_file_ama,'w') as output:
            for i in output_lists[1]:
                output.write("|".join(i)+"\n")
        with open(self.mappings_to_remove_file,'w') as output:
            for i in output_lists[2]:
                output.write("|".join(i)+"\n")

if __name__== "__main__":
    provider = ProcessMapping()
    provider.processMapping()