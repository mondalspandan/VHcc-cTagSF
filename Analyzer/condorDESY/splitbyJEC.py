out=open("cmdList_splitJEC.txt",'w')
inf=open("cmdList.txt",'r')
for line in inf:
    for i in range(5):
        out.write(line.strip()+' %d\n'%i)
        if "Single" in line or "Double" in line or "MuonEG" in line or "EGamma" in line: break
inf.close()
out.close()
