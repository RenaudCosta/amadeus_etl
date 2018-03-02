import os

### INPUT FILES ###
file_from_remove = "in/file_with_station_from_remove.csv"
file_whit_station_to_remove = "in/file_with_station_to_remove.csv"   #ask to put uic into colum 20

### OUTPUT FILES ###
output_file = "out/file_without_.csv"

class removeProces:

    '''
    this class take in input 2 file , one with the station from remove and one with the station to remove,
    so the idea is to match the UIC code and remove the station that match with the same UIC
    '''

    def __init__(self):
        with open(file_from_remove) as ip:
            self.from_remove_list = [row.split("|") for row in ip]
        with open(file_whit_station_to_remove) as ip:
            self.from_with_remove_list = [row.split("|") for row in ip]
        self.dic_station_to_remove = {}
        self.output_list = []

    def process(self):
        print("lunghezza list with all: ", len(self.from_remove_list))
        # Set  for stations to remove
        for index, line in enumerate(self.from_with_remove_list):
            #print(line)
            self.dic_station_to_remove[line[2]] = index
        print("lunghezza list to remove: ",len(self.dic_station_to_remove))

        #load the good station
        for index, line in enumerate(self.from_remove_list):
            #print(line)
            # check right uic column
            if line[0] not in self.dic_station_to_remove.keys():
                #print(line)
                self.output_list.append(line)
        print("lunghezza list output: ", len(self.output_list))

        # Store output
        with open(output_file,'w') as output:
            for i in self.output_list:
                output.write("|".join(i))

if __name__== "__main__":
    removeProces = removeProces()
    removeProces.process()