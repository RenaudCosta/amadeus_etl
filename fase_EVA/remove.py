import os

### INPUT FILES ###
eva_station_list_others_file= "in/EVA_STATIONS_LIST_OTHERS.csv"
ama_file= "in/rail-location-ama.csv"
missing_station= "in/missing_eva_station.csv"
eva_nomi = "in/eva_nomi.txt"


### OUTPUT FILES ###
output_file = "out/eva_station_list_others.csv"
output_file_eva = "out/eva_stations_alredy_in_rfd.csv"
output_file_missing_eva_filtered = "out/missing_eva_station_without_list_others.csv"
output_station_to_add = "out/station_to_add.csv"
output_station_to_add_compare_ama = "out/station_to_add_compare_ama.csv"
output_station_to_add_compare_ama_not_match = "out/output_station_to_add_compare_ama_not_match.csv"
eva_vs_others_prov_match_name = "out/eva_vs_others_prov_match_name.csv"
not_eva_vs_others_prov_match_name_file = "out/not_eva_vs_others_prov_match_name_list.csv"

class evaProcess:
    '''
    check from eva nomi the station that missing using the file missing_eva_station

    output file the station to add, split in many file, just read the file out for know what they have inside
    '''
    def __init__(self):
        with open(eva_station_list_others_file) as ip:
            self.eva_station_list_others = [row.split("|") for row in ip]
        with open(ama_file) as ip:
            self.ama_list = [row.split("|") for row in ip]
        with open(missing_station) as ip:
            self.missing_station_list = [row.split("|") for row in ip]
        with open(eva_nomi) as ip:
            self.eva_nomi_list = [row.split("     ") for row in ip]

        self.eva_station_dic_others = {}
        self.output_dic_missing_eva_filtered = {}
        self.eva_nomi_dic_code_value = {}
        self.eva_nomi_dic_name_long = {}
        self.ama_dic = {}

        self.eva_station_list_others_list = []
        self.output_list_eva = []
        self.output_station_to_add = []
        self.eva_vs_others_prov_match_name_list = []
        self.not_eva_vs_others_prov_match_name_list = []
        self.output_station_to_add_compare_ama_not_match = []
        self.output_list_missing_eva_filtered = []
        self.output_station_to_add_compare_ama = []

    def process(self):

        for index, line in enumerate(self.eva_nomi_list):
            self.eva_nomi_dic_code_value[str(line[0]).strip()] = index
            name = str(line[1]).strip().lower()
            if len(name)>15:
                name = name[:16]
            self.eva_nomi_dic_name_long[name] = index

        for index, line in enumerate(self.eva_station_list_others):
            self.eva_station_dic_others[line[19]] = index
        for index, line in enumerate(self.ama_list):
            self.ama_dic[str(line[1]).strip()] = index

        for line in self.eva_station_list_others:
            #remove line with EVA
            if line[18] != "EVA" and line[18] != "DATA_OWNER":
                self.eva_station_list_others_list.append(line)
            else:
                self.output_list_eva.append(line)

        for line in self.missing_station_list:
            linee = str(line).replace("\\n",'')
            linee = linee.replace("[","").replace("]","").replace("\'","")
            if linee not in self.eva_station_dic_others.keys():
                linee = linee.replace("[","").replace("]","").replace("\'","")
                if len(linee) == 6:
                    linee = "0"+linee
                self.output_list_missing_eva_filtered.append(linee)
                self.output_dic_missing_eva_filtered[linee] = 1

        #station to add
        for line in self.eva_nomi_list:
            linee = line
            format = linee[1].replace("\\n']", "")
            linee = linee[0].replace("['","")

            _output = linee, format
            if linee in self.output_dic_missing_eva_filtered.keys():
                _output = _output[0], "|", _output[1]
                _output = str(_output).replace("('", "").replace("',", "").replace("')", "").replace("'", "")
                self.output_station_to_add.append(_output)

        for line in self.output_station_to_add:
            linee = str(line).split("|")
            linee[1] = linee[1].strip()
            if linee[1] in self.ama_dic.keys():
                self.output_station_to_add_compare_ama.append(line)
            else:
                self.output_station_to_add_compare_ama_not_match.append(line)
        print(len(self.output_station_to_add_compare_ama))

        for line in self.eva_station_list_others_list:
            name = line[7]
            if len(name)>15:
                name = name[:16]
            if str(name).lower() in self.eva_nomi_dic_name_long.keys():
                if line[19] in self.eva_nomi_dic_code_value.keys():
                    self.eva_vs_others_prov_match_name_list.append(line)
            else:
                self.not_eva_vs_others_prov_match_name_list.append(line)

        # Store output
        with open(output_file,'w') as output:
            for i in self.eva_station_list_others_list:
                output.write("|".join(i))

        with open(output_file_eva,'w') as output:
            for i in self.output_list_eva:
                output.write("|".join(i))

        with open(output_file_missing_eva_filtered,'w') as output:
            for i in self.output_list_missing_eva_filtered:
                output.write(i+"\n")

        with open(output_station_to_add,'w') as output:
            for i in self.output_station_to_add:
                output.write(i+"\n")

        with open(output_station_to_add_compare_ama,'w') as output:
            for i in self.output_station_to_add_compare_ama:
                output.write(str(i)+"\n")

        with open(output_station_to_add_compare_ama_not_match,'w') as output:
            for i in self.output_station_to_add_compare_ama_not_match:
                output.write(str(i)+"\n")

        with open(eva_vs_others_prov_match_name, 'w') as output:
            for i in self.eva_vs_others_prov_match_name_list:
                output.write("|".join(i))

        with open(not_eva_vs_others_prov_match_name_file, 'w') as output:
            for i in self.not_eva_vs_others_prov_match_name_list:
                output.write("|".join(i))

if __name__=="__main__":
    removeProces = evaProcess()
    removeProces.process()