import os
from tkinter import messagebox




class CheckOuputProvider:

    def __init__(self):
        ### INPUT FILES ###
        file_one = os.path.dirname(os.path.abspath("")) + "/script_check_output/in/rail-location-mapper.csv"
        file_two = os.path.dirname(os.path.abspath("")) + "/script_check_output/in/rail-location-provider.csv"
        file_3 = os.path.dirname(os.path.abspath("")) + "/script_check_output/in/missing.txt"

        ### OUTPUT FILES ###
        self.file_with_zero = os.path.dirname(os.path.abspath("")) + "/script_check_output/out/rail-location-mapper.csv"
        self.file_with_zero_prov = os.path.dirname(os.path.abspath("")) + "/script_check_output/out/rail-location-provider.csv"
        self.file_missing = os.path.dirname(os.path.abspath("")) + "/script_check_output/out/missing.csv"

        with open(file_one) as ip:
            self.list_one = [row.split("|") for row in ip]
        with open(file_two) as ip:
            self.list_two = [row.split("|") for row in ip]
        with open(file_3) as ip:
            self.file_3_list = [row.split("'") for row in ip]

        self.list_with_zero = []
        self.list_with_zero_prov = []
        self.list_3_out = []

    def processCheckOutput(self):
        '''

        :parameter location-provider -- to take in input in the path in/

        location-mapper -- to take in input in the path in/:

        this method add some 0 when the UIC code len is not 7 and check the short name len
        for cat if is necessary <20, and handle the case with the special character like "ö", "ß", "ü"

        '''
        for line in self.file_3_list:
            if len(line[1]) == 6:
                line[1] = "0"+line[1]
            self.list_3_out.append(line)

        for index, line in enumerate(self.list_one):
            if len(line) < 6:
                raise IndexError(
                    messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                                      " is insert the wrog one ".format(
                        str(file_one))))
                return
            if len(line[1]) == 6:
                line[1] = "0"+line[1]
            if len(line[3]) == 6:
                line[3] = "0"+line[3]
            if len(line[2]) == 5:
                line[2] = "00"+line[2]
            if len(line[2]) == 6:
                line[2] = "0"+line[2]
            if len(line[2]) == 1:
                line[2] = "000000"+line[2]
            self.list_with_zero.append(line)
        special = ["ö", "ß", "ü", "ä"]
        for line in self.list_two:
            if len(line) < 15:
                raise IndexError(
                    messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                                      " is insert the wrog one ".format(
                        str(file_two))))
                return
            if len(line[2]) == 6:
                line[2] = "0"+line[2]
            if len(line[3]) == 6:
                line[3] = "0"+line[3]
            if len(line[3]) == 1:
                line[3] = "000000"+line[3]
            if len(line[2]) == 1:
                line[2] = "000000"+line[2]
            if len(line[5].encode('utf-8')) > 19:#for count the special caracter one bit insted of 2
                # bool = [i[2] for n in special if n in i[2]]
                c = 0
                count = [c + 1 for n in special if n in line[5]]
                if len(count) != 0:
                    appo = line[5]
                    line[5] = appo[:len(line[5]) - len(count) * 2]
                else:
                    appo = line[5]
                    line[5] = appo[:19]
            self.list_with_zero_prov.append(line)

        # Store output
        with open(self.file_with_zero,'w') as output:
            for i in self.list_with_zero:
                output.write("|".join(i))
        # Store output
        with open(self.file_with_zero_prov,'w') as output:
            for i in self.list_with_zero_prov:
                output.write("|".join(i))

        with open(self.file_missing,'w') as output:
            for i in self.list_3_out:
                output.write("'".join(i))

if __name__=="__main__":
    procesCheckOutput = CheckOuputProvider()
    procesCheckOutput.processCheckOutput()