#!/usr/bin/env python
# coding: utf-8

import os
import codecs
import math

### INPUT FILES ###
file_with_name = "in/duplicate.csv"

### OUTPUT FILES ###
output_file = "out/output.csv"


class process:
    '''
    this class just remove, if they are present, the duplicate line by line
    example : line 1   5525225
              line 2   5525225     so remove
    '''
    def __init__(self):
        with open(file_with_name) as ip:
            self.list_with_name = [row.split(",") for row in ip]
        self.list_no_dupli = []
        self.list_output = []
        self.list_name = []
        self.dic_duplicate = {}
        for line in self.list_with_name:
            self.list_name.append(line[0])

    def process(self):
        for index, line in enumerate(self.list_with_name):
            self.dic_duplicate[line[0]] = line

        final_list = []
        for line in self.list_name:
            if line not in final_list:
                final_list.append(line)

        for line in final_list:
            if line in self.dic_duplicate.keys():
                self.list_output.append(self.dic_duplicate[line])

        with open(output_file,'w') as output:
            for index , i in enumerate(self.list_output):
                #for remure the duplicate code immeditly after the current line
                if len(self.list_output) != index+1:
                    line = self.list_output[index+1]
                    code = line[1]
                    if code != i[1]:
                        output.write("|".join(i))

if __name__=="__main__":
    process = process()
    process.process()