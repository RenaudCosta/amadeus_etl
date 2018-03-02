import os

### INPUT FILES ###

file_Errors_NVS = "in/Errors_NVS.txt"
file_rail_location_ama = "in/rail-location-ama.csv"

### OUTPUT FILES ###
output_file = "out/rail-location-ama.csv"

class removeError:

    '''
    read the error log about rail location ama, and fixing the missing line
    next check the len of the UIC if is 7
    '''

    def __init__(self):
        with open(file_Errors_NVS) as ip:
            self.list_Errors_NVS = []
            for row in ip:
                line = row.split(":")
                if(str(line[0]) == "ERROR"):
                    continue
                elif str(line[0] == "ROW"):
                    self.list_Errors_NVS.append(line[1].split("~"))
        with open(file_rail_location_ama) as ip:
            self.list_rail_location_ama = [row.split("\t") for row in ip]

        self.output_list = self.list_rail_location_ama

    def process(self):
        for line in self.list_Errors_NVS:
            appo = [""]*len(self.list_rail_location_ama[0])
            appo[0] = line[2]
            appo[1] = line[4]
            appo[2] = line[5]
            appo[3] = line[6]
            appo[4] = line[7]
            appo[5] = line[8]
            appo[6] = line[9]
            appo[11] = line[14]
            appo[16] = "1234567"
            appo[17] = str(line[20]).replace("\n","")
            appo[18] = "AMA"+"\n"
            self.output_list.append(appo)

        # Store output
        with open(output_file,'w') as output:
            for i in self.output_list:
                if len(i[0]) == 6:
                    i[0] = "0"+str(i[0])
                if len(i[0]) == 1:
                    i[0] = "000000"+str(i[0])
                output.write("|".join(i))

if __name__=="__main__":
    removeError = removeError()
    removeError.process()