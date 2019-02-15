import os, sys

if len(sys.argv) < 2:
    inpDir="/pnfs/desy.de/cms/tier2/store/user/lmastrol/VHcc_2016V4bis_Nov18/"
else:
    inpDir = sys.argv[1]

print "Using input directory: "+inpDir

dirlist=sorted([i for i in os.listdir(inpDir) if os.path.isdir(os.path.join(inpDir,i))])
#print dirlist

os.system("mkdir -p filelists")

def getFilenamesRec(dirpath):
    #print dirpath
    subdirlist=sorted([i for i in os.listdir(dirpath) if os.path.isdir(os.path.join(dirpath,i))])
    filelist=sorted([i for i in os.listdir(dirpath) if os.path.isfile(os.path.join(dirpath,i)) and i.endswith(".root")])
    subfilelist = []
    for dir in subdirlist:
        subfilelist+=getFilenamesRec(os.path.join(dirpath,dir))
    for fl in filelist:
        subfilelist.append(os.path.join(dirpath,fl))
    return subfilelist

def manipulatePath(path):
    #print path
    #channel=path.split("VHcc_2016V4bis_Nov18/")[1].split("/")[0]
    #if "_" in channel: channel=channel.split("_")[0]
    #path=path.split('/tier2')[1]
    return path  # + " " + channel
    
for dr in dirlist:
    outlist=open(os.path.join("filelists",dr+".txt"),'w')
    for fl in getFilenamesRec(os.path.join(inpDir,dr)):
     #    print fl
          outlist.write(manipulatePath(fl)+'\n')
    outlist.close()
