import bonobo
from shutil import copyfile
import threading
import re
import sys

sys.path.append("D:/AMADEUS/PythonMapperScripts/ETL")
sys.path.append("D:/AMADEUS/PythonMapperScripts")

from ETL.Step4ProviderFiles import Step4ProviderFiles
from ETL.Step1comparing import Step1Comparing
from ETL.Step2Mapping import Step2Mapping
from ETL.LineFormatter import LineFormatter, GuessSeparator
from ETL.Step3AmaFiles import Step3AmaFiles


### INPUT FILES ###
old_file_list_file = "in/old.csv"  # select * from rail_location_prov lp join rail_location_mapper mp on lp.DATA_OWNER=mp.DATA_OWNER and lp.code_value = mp.code_value where lp.DATA_OWNER = 'NVS'
new_file_list_file = "in/new.csv"
file_locations_with_mapping_other = "in/locations_with_mapping_other.csv"
file_locations_with_mapping = "in/locations_with_mapping.csv"
file_rail_location_provider = "in/rail-location-provider.csv"
file_rail_location_mapper = "in/rail-location-mapper.csv"
file_rail_location_ama = "in/rail-location-ama.csv"


### OUTPUT FILES ###
ama_locations_out = "out2/rail-location-ama.csv"
location_provider_out = "out2/rail-location-provider.csv"
location_mapper_out = "out2/rail-location-mapper.csv"


### OUTPUT SEPARATORS (default values) ###
global location_provider_separator
location_provider_separator = "|"
global location_mapper_separator
location_mapper_separator = "|"


old_uics = {}
mapping_other_by_uic = {}
mapping_provider = {}
ama_locations = {}

lock = threading.Lock()
global counter
counter = 0
stations_to_process = 0
try:
    with open(new_file_list_file) as f:
        for i in f:
            stations_to_process += 1
except UnicodeDecodeError:
    with open(new_file_list_file, "r", encoding="utf-8") as f:
        for i in f:
            stations_to_process += 1



"""
    EXTRACTORS: Take data from the input files
"""
def extract_old_file(*args):
    with open(old_file_list_file, "r", encoding="utf-8") as input:
        for row in input:
            yield row


def extract_new_file(*args):
    with open(new_file_list_file, "r", encoding="utf-8") as input:
        for row in input:
            yield row


def extract_locations_with_mapping(*args):
    with open(file_locations_with_mapping, "r", encoding="utf-8") as input:
        for row in input:
            yield row


def extract_locations_with_mapping_other(*args):
    try:
        with open(file_locations_with_mapping_other, "r", encoding="utf-8") as input:
            for row in input:
                yield row
    except UnicodeDecodeError:
        with open(file_locations_with_mapping_other, "r", encoding="cp1252") as input:
            for row in input:
                yield row


def extract_rail_location_ama(*args):
    try:
        with open(file_rail_location_ama, "r", encoding="utf-8") as input:
            for row in input:
                yield row.split("|")
    except UnicodeDecodeError:
        with open(file_rail_location_ama, "r") as input:
            for row in input:
                yield row.split("|")


def security_check(*args):
    chars = re.compile("[a-zA-Z0-9_/,\.\(\)' «´²&º-]")
    row = args[0]
    if len(row[0]) == 6:  # UIC
        row[0] = "0" + row[0]
    if len(row[5]) == 6:  # 1A
        row[5] = "0" + row[5]
    to_remove = 0
    for c in row[6]:
        if not chars.match(c):
            to_remove += 1
    row[6] = row[6][0:20-to_remove]
    yield row



"""
    Dict loaders: load info from input files to dictionaries
"""
def load_old(*args):
    line = args[0]
    if line[0].isdigit():
        old_uics[line[0]] = line
        yield


def load_mapping_other(*args):
    line = args[0]
    mapping_other_by_uic[line[19]] = line
    yield


def load_mapping_provider(*args):
    line = args[0]
    mapping_provider[line[11]] = line
    yield


def load_ama_locations(*args):
    line = args[0]
    ama_locations[line[0]] = line
    yield


def update_counter(*args):
    global counter
    with lock:
        counter += 1
        print("\r"+str(counter/stations_to_process*100)[:4]+"%", end="")


"""
    General graph which runs the entire sequence of transformations
"""
def get_graph(owner):

    global location_mapper_separator, location_provider_separator

    new_formatter = LineFormatter(new_file_list_file)

    step1 = Step1Comparing(old_uics)
    step2 = Step2Mapping(mapping_provider, mapping_other_by_uic)
    step3 = Step3AmaFiles(ama_locations, ama_locations_out)
    step4 = Step4ProviderFiles(location_provider_out, location_mapper_out, owner, location_provider_separator,
                               location_mapper_separator)

    graph = bonobo.Graph()

    graph.add_chain(extract_new_file, new_formatter.reformat, security_check, step1.check_new_stations)

    graph.add_chain(step1.new_station, step2.process_mapping, _input=step1.check_new_stations)
    graph.add_chain(step1.old_station_updated, update_counter, _input=step1.check_new_stations)
    graph.add_chain(step1.old_station_unchanged, update_counter, _input=step1.check_new_stations)

    graph.add_chain(step2.no_mapping, step3.generate_glc, _input=step2.process_mapping)
    graph.add_chain(step2.mapped, step4.reformat_provider, step4.update_provider, step4.reformat_mapper,
                    step4.update_mapper, update_counter, _input=step2.process_mapping)
    graph.add_chain(step2.replacing, update_counter, _input=step2.process_mapping)

    graph.add_chain(step3.create_ama_location, step3.load_ama, update_counter, _input=step3.generate_glc)
    graph.add_chain(step4.reformat_provider, step4.update_provider, step4.reformat_mapper, step4.update_mapper,
                    update_counter, _input=step3.generate_glc)

    return graph


def debug_load_to_be_mapped(*args):
    with open("debug/to_be_mapped.csv", "a+") as output:
        output.write("|".join(args[0]))


def debug_load_no_mapping(*args):
    with open("debug/no_mapping.csv", "a+") as output:
        output.write("|".join(args[0]))


"""
    Graph used to load the input files of station to local variables
"""
def get_graph_old_file():
    graph = bonobo.Graph()
    old_formatter = LineFormatter(old_file_list_file)

    graph.add_chain(extract_old_file, old_formatter.reformat, load_old)

    return graph


def get_graph_locations_with_mapping_other():

    graph = bonobo.Graph()
    mapping_formatter = LineFormatter(file_locations_with_mapping_other)
    graph.add_chain(extract_locations_with_mapping_other, mapping_formatter.reformatMapping, load_mapping_other)
    return graph


def get_graph_locations_with_mapping():

    graph = bonobo.Graph()
    mapping_formatter = LineFormatter(file_locations_with_mapping)
    global location_provider_separator
    location_provider_separator = mapping_formatter.get_separator()
    graph.add_chain(extract_locations_with_mapping, mapping_formatter.reformatMapping, load_mapping_provider)
    return graph


def set_rail_location_mapper_separator():
    global location_mapper_separator
    mapping_formatter = LineFormatter(file_rail_location_mapper)
    location_mapper_separator = mapping_formatter.get_separator()


def get_graph_ama_locations():

    graph = bonobo.Graph()
    graph.add_chain(extract_rail_location_ama, load_ama_locations)
    return graph


def get_services(**options):
    return {}


if __name__ == '__main__':
    parser = bonobo.get_argument_parser()
    copyfile(file_rail_location_ama, ama_locations_out)
    copyfile(file_rail_location_provider, location_provider_out)
    copyfile(file_rail_location_mapper, location_mapper_out)
    set_rail_location_mapper_separator()
    bonobo.run(get_graph_old_file(), services=get_services())
    bonobo.run(get_graph_locations_with_mapping_other(), services=get_services())
    bonobo.run(get_graph_locations_with_mapping(), services=get_services())
    bonobo.run(get_graph_ama_locations(), services=get_services())
    print("Provider: ")
    owner = input("")
    bonobo.run(get_graph(owner), services=get_services())
