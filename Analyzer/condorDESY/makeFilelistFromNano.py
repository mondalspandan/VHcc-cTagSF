import os,sys

inp = sys.argv[1]

f = open(inp,'r')
outdir = inp.rstrip('.txt')+"_all"

if os.path.isdir(outdir): 
    print "Cannot run is output directroy %s already exists."%outdir
    sys.exit(1)
os.system("mkdir -p "+ outdir)
for line in f:
    line = line.strip()
    if line == "" or line.startswith('#'): continue
    name = line.split('/')[1]
    os.system('dasgoclient -query="file dataset=%s" >> %s/%s.txt'%(line,outdir,name))
    print "Made %s.txt"%name

f.close()
print "\nDone"

