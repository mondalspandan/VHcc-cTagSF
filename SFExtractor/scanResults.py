import os,sys
indir = sys.argv[1]
central = [i for i in os.listdir(indir) if "central" in i and os.path.isdir(indir+"/"+i)]
reslist = [i for i in os.listdir(indir+"/"+central[0]) if "results" in i and os.path.isdir(indir+"/"+central[0]+"/"+i)]
for res in reslist:
    suff = res.lstrip("results")
    for skip in ["CvsB","CvsL"]:
        cmd = "python GetUncertainties.py -i %s -skip %s -out %s -scansuff %s"%(indir,skip,suff,suff)
        print cmd
        os.system(cmd)
