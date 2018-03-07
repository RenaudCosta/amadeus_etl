import os
from tkinter import messagebox

### INPUT FILES ###
file_with_fix_eva = "in/to-fix-searchable-eva.csv"
file_rail_locatio_eva = "in/rail-location-provider-eva.csv"
file_rail_locatio_bne = "in/rail-location-provider-bne.csv"
file_rail_locatio_nvs = "in/rail-location-provider-nvs.csv"
file_fix_searchable_bne = "in/with-fix-searchable-bne.csv"
file_fix_searchable_nvs = "in/with-fix-searchable-nvs.csv"

### OUTPUT FILES ###
output_file_eva_match = "out/rail-location-provider-eva_match.csv"
output_file_nvs_match = "out/rail-location-provider-nvs_match.csv"
output_file_eva_missing = "out/rail-location-provider-eva_missing.csv"
output_file_bne_match = "out/rail-location-provider-bne_match.csv"
output_file_bne_missing = "out/rail-location-provider-bne_missing.csv"
output_file_nvs_missing = "out/rail-location-provider-nvs_missing.csv"
output_file_bne_merge = "out/rail-location-provider_bne_merge.csv"
output_file_eva_merge = "out/rail-location-provider_eva_merge.csv"

class proces:

    '''
    Class for take 2 file that contains the fix searchable code and two file that need to be fixed,
    so we do the compare, by finding the uic code for Eva , and the name list that we take in output from eva ,
    we will use it for match with the bne fix searchable.

    output is the fix file with the correct code, and the list with the name that not match, plus the merge of this
    two file
    '''

    def __init__(self):
        #if the list is empty, pls check the tab format
        with open(file_rail_locatio_bne) as ip:
            self.list_rail_locatio_bne = [row.split("|") for row in ip]
        with open(file_rail_locatio_eva) as ip:
            self.list_rail_locatio_eva = [row.split("|") for row in ip]
        with open(file_rail_locatio_nvs) as ip:
            self.list_rail_locatio_nvs = [row.split("|") for row in ip]
        with open(file_with_fix_eva) as ip:
            self.list_with_fix_eva = [row.split(",") for row in ip]
        with open(file_fix_searchable_bne) as ip:
            self.list_with_fix_bne = [row.split(",") for row in ip]
        with open(file_fix_searchable_nvs) as ip:
            self.list_with_fix_nvs = [row.split("|") for row in ip]

        self.dic_eva_with_fix = {}
        self.dic_eva_all_with_fix = {}
        self.dic_bne_with_fix = {}
        self.dic_nvs_provider = {}
        self.dic_nvs_provider_by_name = {}

        self.new_eva_list_match = []
        self.bne_list_match_to_eva_output = []
        self.new_bne_list_match = []
        self.new_eva_list_match_missing = []
        self.new_bne_list_match_missing = []
        self.new_nvs_list_match_missing = []
        self.output_merged_bne = []
        self.output_merged_eva = []
        self.new_nvs_list_match = []

    def process(self):
        for line in self.list_with_fix_eva:
            try:
                self.dic_eva_with_fix[line[3]] = line[4]
            except IndexError:
                messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                              " is insert the wrog one ".format(str(file_with_fix_eva)))
                return
        for line in self.list_rail_locatio_nvs:
            try:
                self.dic_nvs_provider[line[2]] = line[20].strip()   #key UIC , status code
                self.dic_nvs_provider_by_name [line[4].upper()] = line[5].upper() # key long name , value short name
            except IndexError:
                messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                              " is insert the wrog one ".format(str(file_rail_locatio_nvs)))
                return

        for index, line in enumerate(self.list_rail_locatio_eva):
            try:
                if len(line) < 20:  # suppose line is at least 14 lenght
                    line[14] = str(line[14]).strip()
                    line = line + ["", "", "", "", "", ""]
                if line[2] in self.dic_eva_with_fix.keys():
                    if self.dic_eva_with_fix[line[2]] == "S":
                        line[20] = "1\n"
                    else:
                        line[20] = "2\n"
                else:
                    line[20] = line[20]+"1\n"
                    self.new_eva_list_match_missing.append(line)
                    #self.new_eva_list_match_missing.append(line[2]+"\n")#add only the UIC
                self.new_eva_list_match.append(line)
            except IndexError:
                messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                              " is insert the wrog one ".format(str(file_rail_locatio_eva)))
                return

        '''
        this for need to check and produce in output a file with the not match uic in the nvs provider , vs the uic in
        the nvs_with_fix serchable, and  
        '''
        for index, line in enumerate(self.list_with_fix_nvs):
            try:
                if line[2] not in self.dic_nvs_provider.keys():
                    self.new_nvs_list_match_missing.append(line)
                else  :
                    code = line[3]
                    if code == "J":
                        codeNumber = "1"
                    elif code == "N":
                        codeNumber = "2"
                    if codeNumber != self.dic_nvs_provider[line[2]]:
                        self.new_nvs_list_match.append(line)
            except IndexError:
                messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                              " is insert the wrog one ".format(str(file_fix_searchable_nvs)))
                return

        '''
        this step remove from the missing file so different uic , the station with different name too
        '''
        for index ,line in enumerate(self.new_nvs_list_match_missing):
            if line[1] not in self.dic_nvs_provider_by_name.keys():
                self.new_nvs_list_match_missing.remove(line)

        #inizialize the second dic with the key = name, valure = code value
        for index, line in enumerate(self.new_eva_list_match):
            if len(line)>=20:
                self.dic_eva_all_with_fix[line[4]] = line[20]
            else:
                self.dic_eva_all_with_fix[line[4]] = "1\n" #default 1

        for line in self.list_with_fix_bne:
            try:
                if line[5] in self.dic_eva_all_with_fix.keys():
                    self.dic_bne_with_fix[line[5]] = self.dic_eva_all_with_fix[line[5]]
            except IndexError:
                messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                              " is insert the wrog one ".format(str(file_fix_searchable_bne)))
                return
        '''
        the bne file is update by find the same name into the output file of eva, so if the name is the same 
        the searchable value will be update in the bne output
        '''
        for line in self.list_rail_locatio_bne:
            try:
                upperLine = line[4].upper()
                if upperLine in self.dic_bne_with_fix.keys():
                    line[20] = self.dic_bne_with_fix[upperLine]
                else:
                    self.new_bne_list_match_missing.append(line)
            except IndexError:
                messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                                  " is insert the wrog one ".format(str(file_rail_locatio_bne)))
                return

        # Store output
        with open(output_file_eva_match,'w') as output:
            for i in self.new_eva_list_match:
                self.output_merged_eva.append(i)
                output.write("|".join(i))
        with open(output_file_nvs_match,'w') as output:
            for i in self.new_nvs_list_match:
                output.write("|".join(i))
        with open(output_file_eva_missing,'w') as output:
            for i in self.new_eva_list_match_missing:
                #self.output_merged_eva.append(i)
                output.write("|".join(i))
        with open(output_file_nvs_missing,'w') as output:
            for i in self.new_nvs_list_match_missing:
                output.write("|".join(i))
        with open(output_file_bne_match,'w') as output:
            for i in self.list_rail_locatio_bne:
                self.output_merged_bne.append(i)
                output.write("|".join(i))
        with open(output_file_bne_missing,'w') as output:
            for i in self.new_bne_list_match_missing:
                #self.output_merged_bne.append(i)
                output.write("|".join(i))
        with open(output_file_bne_merge,'w') as output:
            for i in self.output_merged_bne:
                output.write("|".join(i))
        with open(output_file_eva_merge,'w') as output:
            for i in self.output_merged_eva:
                output.write("|".join(i))

if __name__=="__main__":
    removeProces = proces()
    removeProces.process()