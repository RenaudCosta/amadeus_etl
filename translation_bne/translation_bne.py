import os
from tkinter import messagebox

class Translation:
    '''
    class for fix ama file with the properly languages

    :parameter rail-location-ama-translation.csv -- to take in input in the file that need be fixed

    file_with_code_translation.csv -- with the language code for do the fix:
    '''

    def __init__(self):
        ### INPUT FILES ###
        file_one = os.path.dirname(os.path.abspath("")) + "/translation_bne/in/rail-location-ama-translation.csv"
        file_two = os.path.dirname(os.path.abspath("")) + "/translation_bne/in/file_with_code_translation.csv"

        ### OUTPUT FILES ###
        self.file_with_fix_translation = os.path.dirname(os.path.abspath("")) + "/translation_bne/out/rail-location-ama-with-fix-translation.csv"
        self.file_not_name_match = os.path.dirname(
            os.path.abspath("")) + "/translation_bne/out/list_not_name_match.csv"

        with open(file_one) as ip:
            self.list_one = [row.split("|") for row in ip]
        with open(file_two) as ip:
            self.list_two = [row.split("|") for row in ip]

        #self.dic_file_with_code_translation = {}
        self.dic_code_langue = {}
        self.list_with_fix_translation = []
        self.list_not_name_match = []

        self.list_3_out = []

    def translationProcess(self):

        '''
        this method add some 0 when the code len is not 7 and check the short name len
        for cat if is necessary <20, and handle the case with the special character like "ö", "ß", "ü"

        and after that look the == name for the 2 input file , and discover which is the right language chose the that
        station.
        generate in output a list with the ama file fixed
        '''

        for index, line in enumerate(self.list_two):
            if len(line) < 4:
                raise IndexError(
                    messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                                      " is insert the wrog one ".format(
                        str(file_two))))
                return
            if index > 4 and index < 13:
                self.dic_code_langue[line[6]] = line[10].strip()  #format ID and ISO language
            if index > 13 :
                break

        #step for replace the iso language in the first column of the second file ##and build the dic
        for line in self.list_two:
            if line[0] in self.dic_code_langue.keys():
                line[0] = self.dic_code_langue[line[0]]
            #self.dic_file_with_code_translation[line[2]] = line[0]  # long name , iso language

        special = ["ö", "ß", "ü", "ä"]
        for index, line in enumerate(self.list_one):
            if len(line) < 5:
                raise IndexError(
                    messagebox.showwarning("WARNING", "pls check the split columns character for the file {0},"
                                                      " is insert the wrong one ".format(
                        str(file_one))))
                return
            if len(line[1]) == 6:
                line[1] = "0"+line[1]
            if len(line[1]) == 5:
                line[1] = "00"+line[2]
            if len(line[1]) == 1:
                line[1] = "000000"+line[1]

            if len(line[4].encode('utf-8')) > 19:#for count the special caracter one bit insted of 2
                # bool = [i[2] for n in special if n in i[2]]
                c = 0
                count = [c + 1 for n in special if n in line[4]]
                if len(count) != 0:
                    appo = line[4]
                    line[4] = appo[:len(line[4]) - len(count) * 2]
                else:
                    appo = line[4]
                    line[4] = appo[:19]
            '''
            end fix the input file format about len of 2 column code and the short name desc that can't be more then 19  
            characters lenght
            '''
            nameList = line[3].upper()
            isNameExist = False
            for index, nameUpper in enumerate(self.list_two):
                if nameUpper[2] == nameList:
                    temp = nameUpper
                    isNameExist = True
                    if temp[0] != line[2]:
                        tp = line[:]
                        tp[2] = temp[0]
                        self.list_with_fix_translation.append(tp)
                        print(tp)
            if not isNameExist:
                self.list_not_name_match.append(line)

            line[4] = line[4].strip() + "\n"
            self.list_with_fix_translation.append(line)

        # Store output
        with open(self.file_with_fix_translation,'w') as output:
            for i in self.list_with_fix_translation:
                output.write("|".join(i))
        with open(self.file_not_name_match,'w') as output:
            for i in self.list_not_name_match:
                output.write("|".join(i))

if __name__=="__main__":
    translation = Translation()
    translation.translationProcess()