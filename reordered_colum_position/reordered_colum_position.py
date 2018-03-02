import os

### INPUT FILES ###
file_one= "in/CHECK.csv"

### OUTPUT FILES ###
file_output = "out/file_output_after_check.csv"

class Reordered:
    '''
    reorder the columns of the input file for be like a rail-location-provider format
    '''

    def __init__(self):
        with open(file_one) as ip:
            self.list_to_check = [row.split("|") for row in ip]

        self.list_output = []


    def processReordered(self):
        for index, line in enumerate(self.list_to_check):
            if line[0] == "CITY_NAME":
                continue
            appo = [""]*21
            appo[0] = line[18]#data owner
            appo[1] = line[20].strip()#code_context
            appo[2] = line[19]#code value
            appo[3] = line[11]#generic location code
            appo[4] = line[7]#long name
            appo[5] = line[8]#short name
            appo[6] = line[13]#location type code
            appo[7] = "CET"
            appo[8] = line[12]#latitude
            appo[9] = line[14]#longitude
            appo[14] = line[5]#contry code
            appo[20] = line[3]+"\n"#status code
            self.list_output.append(appo)

        # Store output
        with open(file_output,'w') as output:
            for i in self.list_output:
                output.write("|".join(i))

if __name__=="__main__":
    removeProces = Reordered()
    removeProces.processReordered()