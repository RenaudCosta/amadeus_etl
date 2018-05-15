import os

### INPUT FILES ###
from itertools import count

input_file_whit_loctype = 'in/new_OBB_with_loctype_filtered.csv'
input_file_to_no_loctype = 'in/location_to_map_obb_V2.csv'

### OUTPUT FILES ###
output_list = "out/station_whit_city.csv"
output_filtered = "out/file_filtered.csv"

class sostitute:
    '''
    use it for insert the loctype , from a file that have this information
    '''

    def __init__(self):
        with open(input_file_whit_loctype) as ip:
            self.input_file_with_city = [row.split("|") for row in ip]

        with open(input_file_to_no_loctype) as ip:
            self.input_file_no_city = [row.split("|") for row in ip]

        self.output_list = []
        self.output_filtered = []
        self.list_output_with_loctype_fit = []

    def removeAp(self):
        for i in self.input_file_with_city:
            stringaFiltered = ""
            for n in i:
                n = n.replace("\"", "")
                stringaFiltered = stringaFiltered + "|" + n
            stringaFiltered = stringaFiltered.replace("|", "", 1)
            self.output_filtered.append(stringaFiltered)

    #for fit the loctype
    def process(self):
        count = 1
        for index, i in enumerate(self.input_file_with_city):
            i[1] = i[1].replace("ü", "UE").replace("ö", "OE").replace("ä", "AE").replace("ß", "SS")
            # for fix the ","  problem
            if not i[2].replace("\n", "").isdecimal():
                i[1] = i[1] + ", " + i[2]
                i[2] = i[3]
                i[3] = ""
                self.input_file_with_city[index] = i[:2]

        for index, line in enumerate(self.input_file_no_city):
            # print("entro "+str(line))
            line[7] = line[7].replace("ü", "UE").replace("ö", "OE").replace("ä", "AE").replace("ß", "SS")
            for i in self.input_file_with_city:
                if line[19] == i[0] and line[7] == i[1]:
                    count = count + 1
                    line[13] = i[2].replace("\n","")
                self.input_file_no_city[index] = line
            print(self.input_file_no_city[index])
        print("total equal find  = " + str(count))

        # Store output
        with open(output_list, 'w') as output:
            for i in self.input_file_no_city:
                output.write("|".join(i))

        with open(output_filtered, 'w') as output:
            for i in self.output_filtered:
                output.write(i)

if __name__ == "__main__":
    sostitute = sostitute()
    sostitute.removeAp()
    sostitute.process()