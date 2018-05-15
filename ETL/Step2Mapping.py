from difflib import SequenceMatcher

class Step2Mapping:

    def __init__(self, mapping_provider, mapping_other_by_uic):
        self.mapping_provider = mapping_provider
        self.mapping_other_by_uic = mapping_other_by_uic


    def process_mapping(self, *args):
        # Mapping new stations

        line = args[0]
        code = line[0]
        desc = line[1]
        type = line[2]
        owner = ""
        existing_mapping = ""

        best_mapping_found, match_index = self.find_best_mapping(code, type, desc, owner, existing_mapping)

        flag = ""
        if best_mapping_found == "":
            flag = "nomapping"
        else:
            if best_mapping_found in self.mapping_provider.keys():
                # conflict
                conflicting_line = self.mapping_provider[best_mapping_found]
                conflicting_code_value = conflicting_line[19]
                conflicting_long_desc = conflicting_line[7]
                conflicting_type = conflicting_line[13]
                conflicting_location_type = conflicting_line[13]
                conflicting_data_owner = conflicting_line[18]
                none, conflicting_index = self.find_best_mapping(conflicting_code_value, conflicting_type,
                                                                 conflicting_long_desc,conflicting_data_owner,
                                                                 match_index)

                if conflicting_index >= match_index:
                    flag = "nomapping"
                else:  # The new station is replacing another one
                    line[5] = best_mapping_found  # 1A
                    flag = "replacing"
            else:
                line[5] = best_mapping_found  # 1A
                flag = "mapped"
        yield line, flag

    def find_best_mapping(self, code, type, desc, owner, existing_mapping):

        best_mapping_found = ""
        # Match quality index (the bigger the better)
        best_match_index = 0


        transformed_input_description = desc.strip().upper().translate(
            str.maketrans("", "", "()-, ?.!/;:")).replace(
            "ü", "UE").replace("ö", "OE").replace("ä", "AE").replace("ß", "SS")
        """if code in self.mapping_other_by_uic.keys():
            currentLine = self.mapping_other_by_uic[code]
            transformed_current_desc = currentLine[7].strip().upper().translate(
                str.maketrans("", "", "()-, ?.!/;:")) \
                .replace("ü", "UE").replace("ö", "OE").replace("ä", "AE").replace("ß", "SS")
            stringmatch_ratio = SequenceMatcher(None, transformed_input_description,
                                                transformed_current_desc).ratio()
            if stringmatch_ratio > 0.7:
                match_index = 0.2 + stringmatch_ratio
                if match_index > best_match_index:
                    best_mapping_found = currentLine[11]  # generic location code!!!!
                    best_match_index = match_index
        # Otherwise accept mapping if first 4 characters are the same + similarity is > 90%
        else:"""
        for currentLine in self.mapping_other_by_uic.values():
            transformed_current_desc = currentLine[7].strip().upper().translate(
                str.maketrans("", "", "()-, ?.!/;:")).replace("ü","UE").replace("ö", "OE")\
                .replace("ä", "AE").replace("ß", "SS")
            if transformed_current_desc[:4] == transformed_input_description[:4]:
                match_index = SequenceMatcher(None, transformed_input_description,
                                              transformed_current_desc).ratio()
                if match_index > 0.9:
                    if match_index > best_match_index:
                        best_mapping_found = currentLine[11]  # generic location code!!!!
                        best_match_index = match_index
                        return [best_mapping_found, best_match_index]
        return [best_mapping_found, best_match_index]

    """
        Conditional Node Transformation:
        Checks if the station has been mapped, if so, it yields nothing, otherwise yields the line
    """
    def no_mapping(*args):
        line = args[1]
        flag = args[2]
        if flag == "nomapping":
            yield line

    """
        Conditional Node Transformation:
        Checks if the station has been mapped, if so, it yields the line, otherwise yields nothing
    """

    def mapped(*args):
        #args[0] == Step2 object
        line = args[1]
        flag = args[2]
        if flag == "mapped":
            yield line

    """
        Conditional Node Transformation:
        Checks if the station was mapped over another station, if so, it yields the line, otherwise yields nothing
    """

    def replacing(*args):
        line = args[1]
        flag = args[2]
        if flag == "replacing":
            yield line
