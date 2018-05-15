#!/usr/bin/env python
# coding: utf-8

import os
from difflib import SequenceMatcher
from tkinter import messagebox


class Step3AmaFiles:

    def __init__(self, ama_locations, out_path):
        self.ama_locations = ama_locations
        self.glc_sequence_number = {}
        self.out_path = out_path


    def generate_glc(self, *args):
        line = args[0]
        uic_code = line[0]
        # First try to use the uic code itself as GLC..
        if uic_code not in self.ama_locations.keys():
            line[5] = uic_code
            yield line
        else:
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
                glc_code_available = generated_glc_code not in self.ama_locations.keys()

            line[5] = generated_glc_code
            self.ama_locations[line[5]] = line
            yield line

    def create_ama_location(self, *args):
        provider_location = args[0]
        new_ama_location = [""] * 19
        new_ama_location[0] = provider_location[5].replace("\n","")  # GLC
        new_ama_location[1] = provider_location[1].replace("\n","")  # DefaultLongName
        new_ama_location[2] = provider_location[6].replace("\n","")  # DefaultShortName
        new_ama_location[3] = provider_location[2].replace("\n","")  # LocationTypeCode
        new_ama_location[4] = "CET"  # TimeZone
        new_ama_location[5] = provider_location[3].replace("\n","")  # Latitude
        new_ama_location[6] = provider_location[4].replace("\n","")  # Longitude
        new_ama_location[7] = ""  # Address
        new_ama_location[8] = ""  # Postal code
        new_ama_location[9] = ""  # City name
        new_ama_location[10] = ""  # ProvinceStateCode
        new_ama_location[11] = provider_location[9].replace("\n","")  # CountryCode
        new_ama_location[12] = ""  # PhoneNumber
        new_ama_location[13] = ""  # FaxNumber
        new_ama_location[14] = ""  # Email
        new_ama_location[15] = ""  # MinimumConnectionTime
        new_ama_location[16] = "1234567"  # DaysOfWeekOfOperation
        new_ama_location[17] = provider_location[10].replace("\n","")  # StatusCode
        new_ama_location[18] = "AMA\n"  # Data owner

        yield new_ama_location

    def load_ama(self, *args):
        line = args[0]
        try:
            with open(self.out_path, "a", encoding="utf-8") as output:
                output.write("|".join(line))
        except UnicodeEncodeError:
            with open(self.out_path, "a") as output:
                output.write("|".join(line))