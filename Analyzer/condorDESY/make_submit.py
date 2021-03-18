import os,sys
from random import random

inputdir = "inputs"
sel = "Wc"
#runscript = "condor_runscript_Wc.sh"
if len(sys.argv) > 1:
    inputdir = sys.argv[1]
if len(sys.argv) > 2:
    sel = sys.argv[2]
#    runscript = sys.argv[2]

#f1 = open("submit_base.sub","r")
#f = open("submit.sub","w")
#for line in f1:
#    ln = line.replace('condor_runscript.sh', runscript)
#    f.write(line)
#f1.close()

#if 'DY' in runscript and 'NoJEC' not in runscript: f.write("+RequestRuntime = 18000\n\n")
#f.write("\nqueue SEL,INFILE from cmdList.txt\n")
#f.close()

f2 = open("cmdList.txt",'w')
for fl in [i for i in os.listdir(inputdir) if os.path.isfile(os.path.join(inputdir,i))]:
#  if "Single" in fl or "Double" in fl or "EGamma" in fl or "MuonEG" in fl:
    f3 = open(inputdir.rstrip('/')+"/"+fl,'r')
    for line in f3:
	if 'Wc' in sel and ('DY' in fl or 'TT' in fl or 'ST' in fl) and '2018' in inputdir:
            if random() > 1: continue
        f2.write(sel+" "+line)
    f3.close()
    #f2.write('\n')
f2.close()
