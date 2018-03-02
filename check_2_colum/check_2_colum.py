import os

### INPUT FILES ###
file_one= "in/CHECK.csv"

### OUTPUT FILES ###
file_output = "out/file_output_after_check.csv"

class removeProces:
    '''
    just check the second column of a list , in this case for fix the len by add a 0 if need
    '''
    def __init__(self):
        with open(file_one) as ip:
            self.list_to_check = [row.split(",") for row in ip]

        self.list_output = []
        self.dic_list_to_check = {}

    def process(self):
        for index, line in enumerate(self.list_to_check):
            if len(line[0]) == 6:
                line[0] = "0"+line[0]
            self.dic_list_to_check[line[0]] = index

        for line in self.list_to_check:
            line[2] = str(line[2]).replace("\n","")
            if len(line[2]) == 6:
                line[2] = "0" + line[2]
            print(line[2])
            if line[2] in self.dic_list_to_check.keys():
                self.list_output.append(line)

        # Store output
        with open(file_output,'w') as output:
            for i in self.list_output:
                output.write("|".join(i)+"\n")

if __name__=="__main__":
    removeProces = removeProces()
    removeProces.process()