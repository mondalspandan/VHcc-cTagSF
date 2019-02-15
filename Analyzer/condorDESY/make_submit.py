import os,sys

inputdir = "inputs"
runscript = "condor_runscript_Wc.sh"
if len(sys.argv) > 1:
    inputdir = sys.argv[1]
if len(sys.argv) > 2:
    runscript = sys.argv[2]

f1 = open("submit_base.sub","r")
f = open("submit.sub","w")
for line in f1:
    ln = line.replace('condor_runscript.sh', runscript)
    f.write(ln)
f1.close()

if 'NoJEC' not in runscript: f.write("+RequestRuntime = 18000\n\n")

for fl in [i for i in os.listdir(inputdir) if os.path.isfile(os.path.join(inputdir,i))]:
    f.write("\nqueue INFILE from "+inputdir.rstrip('/')+"/"+fl+"\n")
f.close()
f1.close()
