import os
import re

### INPUT FILES ###
file_nomi_provider= "in/Nomi_provider.csv"
file_ama= "in/rail-location-ama.csv"

### OUTPUT FILES ###
file_output = "out/rail-location-ama.csv"

class check_len_long_name:
    '''
    this class have the scope to match the short name of two list for replace in the first list the fix len name,
    if that name was cut for some reason.
    and the idea is to find the data using the binary research algorithm.

    In this case the file was Ama.csv
    '''
    def __init__(self):
        with open(file_nomi_provider) as ip:
            self.list_nomi_provider = []
            for row in ip:
                row = row.split("\t")
                row = str(row).replace("\\n","").replace("['","").replace("']","")
                self.list_nomi_provider.append(row)

        with open(file_ama) as ip:
            self.list_ama = [row.split("\t") for row in ip]

        self.list_ama_output = []

        self.dic_nomi_provider = {}

    # binary search for find the substring
    def binSearch(self, lst, target):
        min = 0
        max = len(lst) - 1
        avg = int((min + max) / 2)
        while min < max:
            if target in lst[avg] and len(lst[avg])>=len(target):
                return avg
            elif (lst[avg] < target):
                return avg + 1 + self.binSearch(lst[avg + 1:], target)
            else:
                return self.binSearch(lst[:avg], target)
        return avg

    def process(self):
        self.list_nomi_prov = sorted(self.list_nomi_provider)
        for line in self.list_ama :
            line2 = self.binSearch(self.list_nomi_prov,line[1])
            if line[1] in self.list_nomi_provider[line2] and len(self.list_nomi_provider[line2])>=len(line[1]):
                print(line[1],"                     ", self.list_nomi_provider[line2])
                line[1] = self.list_nomi_provider[line2]
            self.list_ama_output.append(line)

        # Store output
        with open(file_output,'w') as output:
            for i in self.list_ama_output:
                if "pippo" in i:
                    print(i)
                output.write(str(i)+"\n")
        print("provider: ",len(self.list_nomi_provider),"\nama output ",len(self.list_ama_output),"\nama :",len(self.list_ama))

if __name__=="__main__":
    check_len_long_name = check_len_long_name()
    check_len_long_name.process()