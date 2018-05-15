

def reset(file):
    f = open(file, "w+")
    f.close()

def write_in(file, content):
    with open(file, "a", encoding="utf-8") as out:
        for line in content:
            out.write(line)

def read(file):
    txt = ""
    with open(file, "r", encoding="utf-8") as ip:
        for row in ip:
            txt += row
    return txt