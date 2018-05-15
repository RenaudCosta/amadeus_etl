
class Step4ProviderFiles:

    def __init__(self, provider, mapper, owner, prov_sep, mapper_sep):
        self.location_provider = provider
        self.location_mapper = mapper
        self.owner = owner
        self.prov_sep = prov_sep
        self.mapper_sep = mapper_sep


    def reformat_provider(self, *args):
        line = args[0]
        newLine = [""]*21
        newLine[0] = self.owner
        newLine[1] = "UIC"
        newLine[2] = line[0]
        newLine[3] = line[5]
        while len(newLine[3]) < 7:
            newLine[3] = "0"+newLine[3]
        newLine[4] = line[1]
        newLine[5] = line[6]
        newLine[6] = line[2]
        newLine[7] = "CET"
        newLine[8] = line[3]
        newLine[9] = line[4]
        newLine[14] = line[9]
        newLine[20] = line[10]
        yield newLine


    def reformat_mapper(self, *args):
        line = args[0]
        newLine = [""]*7
        newLine[0] = "UIC"
        newLine[1] = line[2]
        newLine[2] = line[3]
        newLine[3] = line[2]
        newLine[6] = self.owner+"\n"
        yield newLine

    def update_provider(self, *args):
        line = args[0]
        try:
            with open(self.location_provider, "a", encoding="utf-8") as output:
                output.write(self.prov_sep.join(line))
        except UnicodeEncodeError:
            with open(self.location_provider, "a") as output:
                output.write(self.prov_sep.join(line))
        yield args

    def update_mapper(self, *args):
        line = args[0]
        try:
            with open(self.location_mapper, "a", encoding="utf-8") as output:
                output.write(self.mapper_sep.join(line))
        except UnicodeEncodeError:
            with open(self.location_mapper, "a") as output:
                output.write(self.mapper_sep.join(line))
        yield args
