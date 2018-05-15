from difflib import SequenceMatcher

from ETL.LineFormatter import LineFormatter, GuessSeparator
from ETL.Step1comparing import Step1Comparing
from ETL.Step2Mapping import Step2Mapping
from ETL.Step3AmaFiles import Step3AmaFiles
from ETL.tests import utils
import bonobo


import unittest

file_new = "in/new.csv"
file_old = "in/old.csv"
file_mapping_other = "in/mapping_other.csv"
file_mapping_provider = "in/mapping_provider.csv"
file_ama_locations = "in/ama_locations.csv"
file_rail_loc_prov = "in/rail-location-provider.csv"
file_rail_loc_mapper = "in/rail-location-mapper.csv"

file_out = "out/compared.csv"
out_ama = "out/rail-location-ama.csv"
out_rail_loc_prov = "out/rail-location-provider.csv"
out_rail_loc_mapper = "out/rail-location-mapper.csv"

old_uics = {}
mapping_other = {}
mapping_provider = {}
ama_locations = {}

test4flag = []
test5flag = []
test5bisflag = []
test6flag = []


class StepsTest(unittest.TestCase):

    # STEP 1 : Test reformat
    def init_test1(self):
        utils.reset(file_new)
        utils.reset(file_out)
        utils.write_in(file_new, "85G2327||CET||1||CH||Genestrerio, Croce Grande|Genestrerio, Croce G|||455124N|29|085754E||||OBB|8575607|UIC|85G2327|8575607|||8575607|UIC\n")

    def assert_test1(self):
        result = utils.read(file_out)
        self.assertEqual(result, "8575607|Genestrerio, Croce Grande|29|455124N|085754E|85G2327|Genestrerio, Croce |29||CH|1\n")

    # STEP 1 : Test check if new station
    def init_test2(self):
        utils.reset(file_old)
        utils.reset(file_out)
        utils.write_in(file_old, "85G2327\t\tCET\t\t1\t\tCH\t\tGenestrerio, Croce Grande\tGenestrerio, Croce G\t\t\t455124N\t29\t085754E\t\t\t\tOBB\t8575607\tUIC\t85G2327\t8575607\t\t\t8575607\tUIC\n", )

    def assert_test2(self):
        result = utils.read(file_out)
        self.assertEqual(result, "")

    def assert_test2bis(self):
        result = utils.read(file_out)
        self.assertEqual(result, "8575607|Genestrerio, Croce Grande|29|455124N|085754E|85G2327|Genestrerio, Croce |29||CH|1\n")

    # STEP 1 : Test reformat (crappy file)
    def init_test9(self):
        utils.reset(file_new)
        utils.reset(file_out)
        utils.reset(out_ama)
        utils.write_in(file_new,
                       "1045647|Station name\n")

    def assert_test9(self):
        result = utils.read(out_ama)
        self.assertEqual(result, "1045647|Station name|29|000000N|000000E|0000000|Station name|29||FI|1\n")

    # STEP 2 : Test reformat
    def init_test3(self):
        utils.reset(file_mapping_provider)
        utils.reset(file_out)
        utils.write_in(file_mapping_provider, "|85G0220|CET|1|CH||LUETISBURG|LUETISBURG||||472301N|26|090414E|||||EVA|8506204|RDS\n")

    def assert_test3(self):
        line = "|".join(mapping_provider["85G0220"])
        self.assertEqual(line, "|CET||1||CH||LUETISBURG|LUETISBURG|||85G0220|472301N|26|090414E||||EVA|8506204|UIC\n")

    # STEP 2 : Test Mapping SAME NAME & UIC
    def init_test4(self):
        utils.reset(file_new)
        utils.reset(file_out)
        utils.reset(file_mapping_other)
        utils.write_in(file_new, "0000000||CET||1||FR||Paris TEST|Paris TEST|||455124N|29|085754E||||OBB|4561348|UIC|0000000|4561348|||4561348|UIC\n")
        utils.write_in(file_mapping_other, "|CET||1||FR||Paris TEST|Paris TEST|||11G1111|532309N|29|004606W||||FRR|4561348|UIC\n")

    def assert_test4(self):
        self.assertEqual(test4flag[0], "mapped")

    # STEP 2 : Test Mapping NO MATCH
    def init_test5(self):
        mapping_other.clear()
        utils.reset(file_new)
        utils.reset(file_out)
        utils.reset(file_mapping_other)
        utils.write_in(file_new,
                       "0000000||CET||1||FR||Paris TEST|Paris TEST|||455124N|29|085754E||||OBB|4561348|UIC|0000000|4561348|||4561348|UIC\n")
        utils.write_in(file_mapping_other, "|CET||1||FR||TEST|TEST|||45G7874|532309N|29|004606W||||FRR|1234567|UIC\n")

    def assert_test5(self):
        self.assertEqual(test5flag[0], "nomapping")

    # Step 2 : Test Mapping SAME UIC & DIFFERENT NAME
    def init_test6(self):
        mapping_other.clear()
        mapping_provider.clear()
        utils.reset(file_new)
        utils.reset(file_out)
        utils.reset(file_mapping_provider)
        utils.reset(file_mapping_other)
        utils.write_in(file_new,
                       "0000000||CET||1||FR||Paris TEST|Paris TEST|||455124N|29|085754E||||OBB|4561348|UIC|0000000|4561348|||4561348|UIC\n")
        utils.write_in(file_mapping_provider,
                       "|CET||1||FR||Paris TES|Paris TES|||45G7874|532309N|29|004606W||||FRR|4561348|UIC\n")
        utils.write_in(file_mapping_other, "|CET||1||FR||Paris TEST|Paris TEST|||45G7874|532309N|29|004606W||||FRR|4561348|UIC\n")

    def assert_test6(self):
        self.assertEqual(test6flag[0], "replacing")


    # Step 3 : Test Generating GLC = UIC
    def init_test7(self):
        mapping_other.clear()
        mapping_provider.clear()
        ama_locations.clear()
        utils.reset(file_new)
        utils.reset(file_out)
        utils.reset(file_mapping_provider)
        utils.reset(file_mapping_other)
        utils.reset(file_ama_locations)
        utils.write_in(file_new,
                       "0000000||CET||1||FR||AVIGNON|AVIGNON|||455124N|29|085754E||||OBB|4561348|UIC|0000000|4561348|||4561348|UIC\n")
        utils.write_in(file_mapping_provider,
                       "45G4546||CET||1||FR||TEST|TEST|||455124N|29|085754E||||OBB|1234156|UIC|45G4546|1234156|||1234156|UIC\n")
        utils.write_in(file_mapping_other,
                       "45G4546||CET||1||FR||TEST|TEST|||455124N|29|085754E||||OBB|1234156|UIC|45G4546|1234156|||1234156|UIC\n")
        utils.write_in(file_ama_locations,
                       "45G4546||CET||1||FR||TEST|TEST|||455124N|29|085754E||||OBB|1234156|UIC|45G4546|1234156|||1234156|UIC\n")

    def assert_test7(self):
        result = utils.read(file_out)
        self.assertEqual(result, "4561348|AVIGNON|29|455124N|085754E|4561348|AVIGNON|29||FR|1\n")


    # Step 3 : Test Generating new GLC
    def init_test8(self):
        mapping_other.clear()
        mapping_provider.clear()
        ama_locations.clear()
        utils.reset(file_new)
        utils.reset(file_out)
        utils.reset(file_mapping_provider)
        utils.reset(file_mapping_other)
        utils.reset(file_ama_locations)
        utils.write_in(file_new,
                       "0000000||CET||1||FR||AVIGNON|AVIGNON|||455124N|29|085754E||||OBB|4561348|UIC|0000000|4561348|||4561348|UIC\n")
        utils.write_in(file_mapping_provider,
                       "45G4546||CET||1||FR||TEST|TEST|||455124N|29|085754E||||OBB|1234156|UIC|45G4546|1234156|||1234156|UIC\n")
        utils.write_in(file_mapping_other,
                       "45G4546||CET||1||FR||TEST|TEST|||455124N|29|085754E||||OBB|4561348|UIC|45G4546|4561348|||4561348|UIC\n")
        utils.write_in(file_ama_locations,
                       "4561348||CET||1||FR||TEST|TEST|||455124N|29|085754E||||OBB|4561348|UIC|45G4546|4561348|||4561348|UIC\n")

    def assert_test8(self):
        result = utils.read(file_out)
        self.assertEqual(result, "4561348|AVIGNON|29|455124N|085754E|45G0000|AVIGNON|29||FR|1\n")


def extract_new():
    with open(file_new, "r", encoding="utf-8") as ip:
        for row in ip:
            yield row


def extract_old():
    with open(file_old, "r", encoding="utf-8") as ip:
        for row in ip:
            yield row


def extract_mapping_other(*args):
    with open(file_mapping_other, "r", encoding="utf-8") as input:
        for row in input:
            lines = row
            yield lines


def extract_mapping_provider(*args):
    with open(file_mapping_provider, "r", encoding="utf-8") as input:
        for row in input:
            lines = row
            yield lines


def extract_ama_locations(*args):
    with open(file_ama_locations, "r", encoding="utf-8") as input:
        for row in input:
            lines = row
            yield lines


def get_graph1():
    formatter = LineFormatter(file_new)
    graph = bonobo.Graph()
    graph.add_chain(extract_new, formatter.reformat, load)
    return graph


def get_graph2():
    formatter = LineFormatter(file_new)
    step1 = Step1Comparing(old_uics)
    graph = bonobo.Graph()
    graph.add_chain(extract_new, formatter.reformat, step1.check_new_stations)

    graph.add_chain(step1.new_station, load, _input=step1.check_new_stations)
    graph.add_chain(step1.old_station_updated, load, _input=step1.check_new_stations)
    return graph


def get_graph2bis():
    formatter = LineFormatter(file_new)
    step1 = Step1Comparing(old_uics)
    graph = bonobo.Graph()

    graph.add_chain(extract_new, formatter.reformat, step1.check_new_stations)

    graph.add_chain(step1.new_station, load, _input=step1.check_new_stations)
    graph.add_chain(step1.old_station_updated, load, _input=step1.check_new_stations)
    graph.add_chain(step1.old_station_unchanged, load, _input=step1.check_new_stations)
    return graph


def get_graph4():
    formatter = LineFormatter(file_new)
    step1 = Step1Comparing(old_uics)
    step2 = Step2Mapping(mapping_provider, mapping_other)
    graph = bonobo.Graph()

    graph.add_chain(extract_new, formatter.reformat, step1.check_new_stations, step1.new_station, step2.process_mapping)

    graph.add_chain(step2.mapped, load_test4_flag, _input=step2.process_mapping)

    return graph

# check that "no_mapping" node yields something
def get_graph5():
    formatter = LineFormatter(file_new)
    step1 = Step1Comparing(old_uics)
    step2 = Step2Mapping(mapping_provider, mapping_other)
    graph = bonobo.Graph()

    graph.add_chain(extract_new, formatter.reformat, step1.check_new_stations, step1.new_station, step2.process_mapping)

    graph.add_chain(step2.no_mapping, load_test5_flag, _input=step2.process_mapping)

    return graph

# check that "mapped" node yields nothing
def get_graph5bis():
    formatter = LineFormatter(file_new)
    step1 = Step1Comparing(old_uics)
    step2 = Step2Mapping(mapping_provider, mapping_other)
    graph = bonobo.Graph()

    graph.add_chain(extract_new, formatter.reformat, step1.check_new_stations, step1.new_station, step2.process_mapping)

    graph.add_chain(step2.mapped, load_test5bis_flag, _input=step2.process_mapping)

    return graph


def get_graph6():
    formatter = LineFormatter(file_new)
    step1 = Step1Comparing(old_uics)
    step2 = Step2Mapping(mapping_provider, mapping_other)
    graph = bonobo.Graph()

    graph.add_chain(extract_new, formatter.reformat, step1.check_new_stations, step1.new_station, step2.process_mapping)

    graph.add_chain(step2.replacing, load_test6_flag, _input=step2.process_mapping)

    return graph


def get_graph7():
    formatter = LineFormatter(file_new)
    step1 = Step1Comparing(old_uics)
    step2 = Step2Mapping(mapping_provider, mapping_other)
    step3 = Step3AmaFiles(ama_locations, out_ama)
    graph = bonobo.Graph()

    graph.add_chain(extract_new, formatter.reformat, step1.check_new_stations, step1.new_station, step2.process_mapping)

    graph.add_chain(step2.no_mapping, step3.generate_glc, load, _input=step2.process_mapping)

    return graph


def get_graph9():
    formatter = LineFormatter(file_new)
    graph = bonobo.Graph()
    graph.add_chain(extract_new, formatter.reformat, load_ama)
    return graph


def get_graph_mapping_other():
    graph = bonobo.Graph()
    mapping_formatter = LineFormatter(file_mapping_other)
    graph.add_chain(extract_mapping_other, mapping_formatter.reformatMapping, load_mapping_other)
    return graph


def get_graph_mapping_provider():
    graph = bonobo.Graph()
    mapping_formatter = LineFormatter(file_mapping_provider)
    graph.add_chain(extract_mapping_provider, mapping_formatter.reformatMapping, load_mapping_provider)
    return graph


def get_graph_ama_locations():
    graph = bonobo.Graph()
    graph.add_chain(extract_ama_locations, load_ama_locations)
    return graph


def get_graph_old_file():

    graph = bonobo.Graph()
    old_formatter = LineFormatter(file_old)

    graph.add_chain(extract_old, old_formatter.reformat, load_old)

    return graph


def get_services(**options):
    return {}


def load_old(*args):
    line = args[0]
    if line[0].isdigit():
        old_uics[line[0]] = line
        yield


def load_mapping_other(*args):
    line = args[0]
    mapping_other[line[19]] = line
    yield


def load_mapping_provider(*args):
    line = args[0]
    mapping_provider[line[11]] = line
    yield


def load_ama_locations(*args):
    sep = GuessSeparator()
    line = args[0].split(sep.separator(args[0]))
    ama_locations[line[0]] = line
    yield


def neutral_load(*args):
    print(args[0])


def load(*args):
    line = args[0]
    utils.write_in(file_out, "|".join(line))


def load_ama(*args):
    line = args[0]
    utils.write_in(out_ama, "|".join(line))


def load_test4_flag(*args):
    test4flag.append("mapped") if len(args[0]) > 0 else test4flag.append("")
    yield


def load_test5_flag(*args):
    test5flag.append("nomapping") if len(args[0]) > 0 else test5flag.append("")
    yield


def load_test6_flag(*args):
    test6flag.append("replacing") if len(args[0]) > 0 else test6flag.append("")
    yield


def load_test5bis_flag(*args):
    test5bisflag.append("nomapping") if len(args[0]) == 0 else test5flag.append("")
    yield


if __name__ == '__main__':
    test = StepsTest()

    print("Test 1")
    test.init_test1()
    bonobo.run(get_graph1(), services=get_services())
    test.assert_test1()

    print("Test 2")
    test.init_test2()
    bonobo.run(get_graph_old_file(), services=get_services())
    bonobo.run(get_graph2(), services=get_services())
    test.assert_test2()

    print("Test 2 bis")
    test.init_test2()
    bonobo.run(get_graph2bis(), services=get_services())
    test.assert_test2bis()

    print("Test 3")
    test.init_test3()
    bonobo.run(get_graph_mapping_provider(), services=get_services())
    test.assert_test3()

    print("Test 4")
    test.init_test4()
    bonobo.run(get_graph_mapping_other(), services=get_services())
    bonobo.run(get_graph4(), services=get_services())
    test.assert_test4()

    print("Test 5")
    test.init_test5()
    bonobo.run(get_graph_mapping_other(), services=get_services())
    bonobo.run(get_graph5(), services=get_services())
    test.assert_test5()

    # Opposite test (graph5bis)
    print("Test 5 bis")
    test.init_test5()
    bonobo.run(get_graph_mapping_other(), services=get_services())
    bonobo.run(get_graph5bis(), services=get_services())
    test.assert_test5()

    print("Test 6")
    test.init_test6()
    bonobo.run(get_graph_mapping_other(), services=get_services())
    bonobo.run(get_graph_mapping_provider(), services=get_services())
    bonobo.run(get_graph6(), services=get_services())
    test.assert_test6()

    print("Test 7")
    test.init_test7()
    bonobo.run(get_graph_mapping_other(), services=get_services())
    bonobo.run(get_graph_mapping_provider(), services=get_services())
    bonobo.run(get_graph_ama_locations(), services=get_services())
    bonobo.run(get_graph7(), services=get_services())
    test.assert_test7()

    print("Test 8")
    test.init_test8()
    bonobo.run(get_graph_mapping_other(), services=get_services())
    bonobo.run(get_graph_mapping_provider(), services=get_services())
    bonobo.run(get_graph_ama_locations(), services=get_services())
    bonobo.run(get_graph7(), services=get_services())
    test.assert_test8()

    print("Test 9")
    test.init_test9()
    bonobo.run(get_graph9(), services=get_services())
    test.assert_test9()

    unittest.main()
