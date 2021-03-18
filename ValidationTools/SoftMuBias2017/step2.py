import pickle, sys
from glob import glob
import matplotlib.pyplot as plt
import mplhep as hep, numpy as np
plt.style.use(hep.style.ROOT)
my_cmap = plt.cm.coolwarm
my_cmap.set_under('w',0)

norm = True
if len(sys.argv) > 1: norm = False

unpackbin = pickle.load(open("pkls/bin.pkl",'rb'))
binx = unpackbin[0]
biny = unpackbin[1]

for f in ["2D_DC_b_*","2D_DC_c_*","2D_DJ_b_*","2D_DJ_c_*","2D_DC_b_nomu*","2D_DC_c_nomu*","2D_DJ_b_nomu*","2D_DJ_c_nomu*"]:
    flav = f.split('_')[2]
    if "DC" in f: tagger = "DeepCSV"
    else: tagger = "DeepJet"
    init = True
    numsize = 0
    densize = 0
    numm1 = 0
    denm1 = 0
    if "nomu" in f:  fllist = glob("pkls/"+f)
    else:            fllist = [i for i in glob("pkls/"+f) if "nomu" not in i]
    for fl in fllist:
        unpack = pickle.load(open(fl,'rb'))
        if init:
            histnum = unpack[0]
            histden = unpack[2]
            init = False
        else:
            histnum += unpack[0]
            histden += unpack[2]
        numsize += unpack[1]
        densize += unpack[3]
        numm1 += unpack[4]
        denm1 += unpack[5]

    fig, ax = plt.subplots(figsize=(12,12))
    if norm:
        histnum = histnum / numsize
        histden = histden / densize
        numm1 = numm1 / numsize
        denm1 = denm1 / densize

    # We decided to flip Num and Den, hence things got weird here.
    ratio = histden/histnum
    mn = np.nanmean(ratio)
    print (mn)
    ratio = np.where(histnum > 0,ratio,-10)
    m1ratio = denm1/numm1

    if norm:
        hep.hist2dplot(ratio, binx, biny, vmin=0.5, vmax=1.5, cmap = my_cmap)
    else:
        hep.hist2dplot(ratio, binx, biny, vmin=max(mn/2,2*mn-1), vmax=min(1,mn*3/2), cmap = my_cmap)
    # pickle.dump([ratio,m1ratio],open(f.rstrip('*')+".pkl",'wb'))

    ax.set_ylabel("%s CvsB"%tagger)
    ax.set_xlabel("%s CvsL"%tagger)

    zlabel = r"$\frac{\#\ %s\ jets\ with\ MUSTATUS\ muNORM}{\#\ %s\ jetsNORM}$"%(flav,flav)
    if "nomu" in f:  zlabel = zlabel.replace("MUSTATUS","no")
    else:            zlabel = zlabel.replace("MUSTATUS","soft")
    if norm:         zlabel = zlabel.replace("NORM","\ (normed)")
    else:            zlabel = zlabel.replace("NORM","")
    # zlabel.replace(" ","\ ")

    ax.text(0.5,1.08,zlabel,ha="center",va="center")
    ax.text(-0.1,-0.1,"-1 bin: %.3f"%m1ratio)
    
    hep.cms.label(ax=ax)
    # hep.r_align()
    outname = f.rstrip('*')
    if norm: outname += "normed"
    plt.savefig(outname+".png")
    plt.clf()