import os, subprocess
os.system("grep -Ril condor/*.log -e aborted &> failedlist.txt")
os.system("mkdir -p condor/oldlogs")
failednums = []
with open("failedlist.txt",'r') as lst:
    for line in lst:
        failednums.append(line.split("-")[1].rstrip(".log\n"))
failednums.sort()
print failednums
missed = failednums[:]
#concstr = " ".join(failednums)
#print concstr   
proc = subprocess.Popen(['condor_history']+failednums,stdout=subprocess.PIPE)

with open("toResubmit.txt","w") as fl:
    for line in iter(proc.stdout.readline,''):
        if not line.startswith(" "):
            jobid = line.split()[0]
            missed.remove(jobid)
            fl.write(line.strip().split()[-1]+"\n")

with open("resubmit.sub","w") as fl:
    with open("submit.sub","r") as flin:
        for line in flin:
            if not line.startswith("queue"): fl.write(line)
    fl.write("queue INFILE from toResubmit.txt")
print "Created resubmit.sub."
if len(missed) > 0: print "Could not find condor_history for:"
print missed
