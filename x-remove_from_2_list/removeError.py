import os

### INPUT FILES ###
file_from_remove = "in/rail-location-provider.csv"
file_mapper = "in/rail-location-mapper.csv"
file_whit_station_to_remove = "in/failed_EVA_RDS_Stations.txt"   #ask to put uic into colum 20

### OUTPUT FILES ###
output_file = "out/rail-location-provider.csv"

class removeProces:

    '''
    script for take in input the provider and mapper, and the error log
    read this file with error and fix this problem "duplicate row" in that case
    '''

    def __init__(self):
        with open(file_from_remove) as ip:
            self.from_remove_list = [row.split("|") for row in ip]
        with open(file_whit_station_to_remove) as ip:
            self.from_with_remove_list = [row.split(",") for row in ip]
        with open(file_mapper) as ip:
            self.list_mapper = [row.split("|") for row in ip]
        self.dic_station_to_remove = {}
        self.output_list = []

    def process(self):
        print("lunghezza list with all: ", len(self.from_remove_list))
        # Set  for stations to remove
        for index, line in enumerate(self.from_with_remove_list):
            #print(line)
            if line[0] != "ERROR: Duplicate row":
                continue

            self.dic_station_to_remove[str(line[3]).replace("CODE_VALUE=","")] = index
        print("lunghezza list to remove: ",len(self.dic_station_to_remove))

        #load the good station
        for index, line in enumerate(self.from_remove_list):
            #print(line)
            # check right uic column
            if line[2] in self.dic_station_to_remove.keys() and line[6] == 26:
                print(line)
                line[1] = "RDS"
            self.output_list.append(line)

        print("lunghezza list output: ", len(self.output_list))

        # Store output
        with open(output_file,'w') as output:
            for i in self.output_list:
                output.write("|".join(i))

if __name__== "__main__":
    removeProces = removeProces()
    removeProces.process()