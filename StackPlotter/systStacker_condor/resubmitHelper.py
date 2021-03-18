import os, subprocess
os.system("grep -Ril condor/*.log -e aborted &> failedlist.txt")
os.system("mkdir -p condor/oldlogs")
failednums = []
with open("failedlist.txt",'r') as lst:
    for line in lst:
        failednums.append(line.split("-")[1].split(".")[1])
failednums.sort()
#failednums += [76]
print failednums
missed = failednums[:]
#concstr = " ".join(failednums)
#print concstr   

with open("toResubmit.txt","w") as fl:
    f=open('cmdList.txt','r')
    ln=f.readlines()
    for failed in failednums:
        fullline = ln[int(failed)].strip()
        for each in fullline.split("NEWLINE"):
            fl.write(each.strip("NEWLINE")+"\n")
        os.system("mv condor/*.%s.log condor/oldlogs"%failed)
