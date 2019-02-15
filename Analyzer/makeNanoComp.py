oF = open("Wlvhcc_nano.py","w")
iF = open("Wlvhcc.py","r")

count = 0
for line in iF:
    line=line.rstrip()
    if "entry." in line and not line.strip().startswith("exec"):
        count += line.count("entry.")
        postEntry = line.split("entry.")
        newLine = postEntry[0]
        for i in postEntry[1:]:
            for ij,j in enumerate(i+" "):
                if (not j.isalnum() and not j=="_") or ij == len(i):
                    if j =="[":
                        ins = "\",'list')"
                    else:
                        ins = "\",'fl')"
                    newi = i[:ij]+ins+i[ij:]
                    break
            newLine += "getEntry(\""+newi
        oF.write(newLine+"\n")
    else:
        oF.write(line+'\n')
        # print newLine

print "\nFound %d instances."%count
iF.close()
oF.close()
