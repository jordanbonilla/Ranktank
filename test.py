def readDict(filename):
    with open(filename, "r") as f:
        dict = {}
        content = f.readlines()
        for line in content:
            values = line.split("@")
            dict[values[0]] = values[1].replace("\n", "")
        return(dict)

print readDict("pseudonyms.txt")