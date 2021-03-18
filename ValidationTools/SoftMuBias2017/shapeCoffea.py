# Laptop, Python3
from coffea.nanoaod import NanoEvents as Events
import matplotlib.pyplot as plt
import numpy as np
import mplhep as hep, sys, os
import pickle
# import uproot

batch = False

plt.style.use(hep.style.ROOT)

fname = "test.root"
fname = sys.argv[1]
if fname.startswith('/store/'):
    print ("Attempting to read over XRootD...")
    fname = "root://xrootd-cms.infn.it//"+fname

outdir = "pkls"
os.system("mkdir -p "+outdir)

events = Events.from_file(fname)
alljets = events.Jet

def maskDC(jets):
    dflt = (jets.btagDeepB < 0) | (jets.btagDeepC < 0) | (jets.btagDeepB > 1) | (jets.btagDeepC > 1) | (jets.btagDeepB + jets.btagDeepC > 1) | (1-jets.btagDeepB <= 0) | (jets.btagDeepC + jets.btagDeepB <= 0) | (np.isnan(jets.btagDeepB)) | (np.isnan(jets.btagDeepC))
    return dflt

def maskDJ(jets):
    dflt = (jets.btagDeepFlavB < 0) | (jets.btagDeepFlavC < 0) | (jets.btagDeepFlavB >= 1) | (jets.btagDeepFlavC >= 1) | (jets.btagDeepFlavB + jets.btagDeepFlavC > 1) | (1-jets.btagDeepFlavB <= 0) | (jets.btagDeepFlavC + jets.btagDeepFlavB <= 0) | (np.isnan(jets.btagDeepFlavB)) | (np.isnan(jets.btagDeepFlavC))
    return dflt

if "CvsL" not in events.Jet.columns:
    # alljets[(np.isnan(alljets.btagDeepB)) | (np.isnan(alljets.btagDeepC))].btagDeepB = -1
    # alljets[(np.isnan(alljets.btagDeepB)) | (np.isnan(alljets.btagDeepC))].btagDeepC = -1
    # alljetsDCdefaultmask = (alljets.btagDeepB < 0) | (alljets.btagDeepC < 0) | (alljets.btagDeepB + alljets.btagDeepC > 1) | (1-alljets.btagDeepB <= 0) | (alljets.btagDeepC + alljets.btagDeepB <= 0)
    events.Jet["CvsL"] =  events.Jet.btagDeepC/(1-events.Jet.btagDeepB)
    events.Jet["CvsB"] =  events.Jet.btagDeepC/(events.Jet.btagDeepC + events.Jet.btagDeepB)
    # events.Jet[alljetsDCdefaultmask].CvsL = -1
    # events.Jet[alljetsDCdefaultmask].CvsB = -1
    print("Created DeepCSV transformations.")

if "DeepFlavCvsL" not in events.Jet.columns:
    # alljets[(np.isnan(alljets.btagDeepFlavB)) | (np.isnan(alljets.btagDeepFlavC))].btagDeepFlavB = -1
    # alljets[(np.isnan(alljets.btagDeepFlavB)) | (np.isnan(alljets.btagDeepFlavC))].btagDeepFlavC = -1
    # alljetsDJdefaultmask = (alljets.btagDeepFlavB < 0) | (alljets.btagDeepFlavC < 0) | (alljets.btagDeepFlavB + alljets.btagDeepFlavC > 1) | (1-alljets.btagDeepFlavB <= 0) | (alljets.btagDeepFlavC + alljets.btagDeepFlavB <= 0)
    events.Jet["DeepFlavCvsL"] =  events.Jet.btagDeepFlavC/(1-events.Jet.btagDeepFlavB)
    events.Jet["DeepFlavCvsB"] =  events.Jet.btagDeepFlavC/(events.Jet.btagDeepFlavC + events.Jet.btagDeepFlavB)
    # events.Jet[alljetsDJdefaultmask].DeepFlavCvsL = -1
    # events.Jet[alljetsDJdefaultmask].DeepFlavCvsB = -1
    print("Created DeepJet transformations.")



def jetmask(jets,flav=None):
    cond = (jets.pt > 20) & (np.abs(jets.eta) < 2.5) & (jets.jetId > 5) & (jets.puId > 6)
    if flav!=None: cond = (cond) & (jets.hadronFlavour == flav)
    return cond

def softmumask(muons):
    return (muons.pt < 25) & (np.abs(muons.eta) < 2.4) & (muons.tightId) & (muons.pfRelIso04_all > 0.2)

cjets = events.Jet[jetmask(events.Jet,4)]
cjetswithsoftmu = cjets[softmumask(cjets.matched_muons).any()]
cjetsnomu = cjets[~(cjets.matched_muons.pt>0).any()]

bjets = events.Jet[jetmask(events.Jet,5)]
bjetswithsoftmu = bjets[softmumask(bjets.matched_muons).any()]
bjetsnomu = bjets[~(bjets.matched_muons.pt>0).any()]


goodcjetevs = events[cjetswithsoftmu.counts==1]
goodcjets = cjetswithsoftmu[cjetswithsoftmu.counts==1]
def getDdecay(pdgid):
    Dpm = goodcjetevs.GenPart[abs(goodcjetevs.GenPart.pdgId)==pdgid]
    return goodcjets[(goodcjets[:,0].delta_r(Dpm)<0.4).any()]
    
DpmJets = getDdecay(411)
D0Jets = getDdecay(421)
DsJets = getDdecay(431)


print ("b")
btot = len(bjets.flatten())
print ("\tTotal:",btot)
bgood = len(bjetswithsoftmu.flatten())
print ("\tWith good Soft Mu:",bgood,bgood/btot*100,"%")
bno = len(bjetsnomu.flatten())
print ("\tWithout Mu:",bno,bno/btot*100,"%")
# print ("\tWith Mu:",len(bjets.flatten())-len(bjetsnomu.flatten()))
print
print ("c")
ctot = len(cjets.flatten())
print ("\tTotal:",ctot)
cgood = len(cjetswithsoftmu.flatten())
print ("\tWith good Soft Mu:",cgood,cgood/ctot*100,"%")
cno = len(cjetsnomu.flatten())
print ("\tWithout Mu:",cno,cno/ctot*100,"%")

def make1Dplot(vars,labels,xlabel,outname="",title=None,masks=[]):
    fig, ax = plt.subplots()
    for ivar,var in enumerate(vars):
        var = var.flatten()        
        if masks!=[]:
            # print (var[masks[ivar].flatten()])
            var[masks[ivar].flatten()] = -1
            # print (var[masks[ivar].flatten()])            
        hist,bins = np.histogram(var,range=(0,1),bins=50)
        hist = hist/var.size
        hep.histplot(hist,bins,label=labels[ivar])
    ax.set_xlabel(xlabel,ha="right", x=1)
    ax.set_xlim(0,1)
    ax.set_ylabel("Fraction of jets", ha="right", y=1)
    hep.cms.label(ax=ax)
    # hep.r_align()
    ax.legend(title=title)
    if outname=="": outname=xlabel
    plt.savefig(outname+".png")

def make2Dplot(numx,numy,denx,deny,tagger="",outname="",masks=[]):
    numx = numx.flatten()
    numy = numy.flatten()
    denx = denx.flatten()
    deny = deny.flatten()

    if masks!= []:
        numx[masks[0].flatten()] = -1
        numy[masks[0].flatten()] = -1
        denx[masks[1].flatten()] = -1
        deny[masks[1].flatten()] = -1

    histnum,binx,biny = np.histogram2d(numx, numy, range=[(0, 1),(0,1)], bins=(50,10))
    histden,binx,biny = np.histogram2d(denx, deny, range=[(0, 1),(0,1)], bins=(50,10))
    numm1 = numx[numx < 0].size
    denm1 = denx[denx < 0].size

    if batch:
        pickle.dump([histnum,numx.size,histden,denx.size,numm1,denm1],open("%s/%s_%s.pkl"%(outdir,outname,fname.split('/')[-1].rstrip(".root")),"wb"))
        binfl = "%s/bin.pkl"%outdir
        if not os.path.isfile(binfl): pickle.dump([binx,biny],open(binfl,"wb"))
    else:
        fig, ax = plt.subplots()
        histnum = histnum / numx.size
        histden = histden / denx.size

        ratio = np.where(histden > 0,histnum/histden,1.)
        hep.hist2dplot(ratio, binx, biny, vmin=0.5, vmax=1.5)


        ax.set_ylabel("%s CvsB"%tagger)
        ax.set_xlabel("%s CvsL"%tagger)
        hep.cms.label(ax=ax)
        # hep.r_align()
        plt.savefig(outname+".png")

if not batch:
    vars = [DpmJets.DeepFlavCvsL,D0Jets.DeepFlavCvsL,cjetsnomu.DeepFlavCvsL]
    labels = [r"$D^{\pm}$ jets","$D^0$ jets","$D_s$ jets"]
    masks = [maskDJ(DpmJets),maskDJ(D0Jets),maskDJ(cjetsnomu)]
    make1Dplot(vars,labels,"DeepJet CvsL","DJ_Djets_CvsL","DeepJet",masks)
    vars = [DpmJets.DeepFlavCvsB,D0Jets.DeepFlavCvsB,DsJets.DeepFlavCvsB]
    labels = [r"$D^{\pm}$ jets","$D^0$ jets","$D_s$ jets"]
    masks = [maskDJ(DpmJets),maskDJ(D0Jets),maskDJ(DsJets)]
    make1Dplot(vars,labels,"DeepJet CvsB","DJ_Djet_CvsB","DeepJet",masks)



    vars = [cjets.DeepFlavCvsL,cjetswithsoftmu.DeepFlavCvsL,cjetsnomu.DeepFlavCvsL]
    labels = ["All c jets","With soft mu","No soft mu"]
    masks = [maskDJ(cjets),maskDJ(cjetswithsoftmu),maskDJ(cjetsnomu)]
    make1Dplot(vars,labels,"DeepJet CvsL","DJ_c_CvsL","DeepJet",masks)

    vars = [cjets.DeepFlavCvsB,cjetswithsoftmu.DeepFlavCvsB,cjetsnomu.DeepFlavCvsB]
    labels = ["All c jets","With soft mu","No soft mu"]
    masks = [maskDJ(cjets),maskDJ(cjetswithsoftmu),maskDJ(cjetsnomu)]
    make1Dplot(vars,labels,"DeepJet CvsB","DJ_c_CvsB","DeepJet",masks)

    vars = [bjets.DeepFlavCvsL,bjetswithsoftmu.DeepFlavCvsL,bjetsnomu.DeepFlavCvsL]
    labels = ["All b jets","With soft mu","No soft mu"]
    masks = [maskDJ(bjets),maskDJ(bjetswithsoftmu),maskDJ(bjetsnomu)]
    make1Dplot(vars,labels,"DeepJet CvsL","DJ_b_CvsL","DeepJet",masks)

    vars = [bjets.DeepFlavCvsB,bjetswithsoftmu.DeepFlavCvsB,bjetsnomu.DeepFlavCvsB]
    labels = ["All b jets","With soft mu","No soft mu"]
    masks = [maskDJ(bjets),maskDJ(bjetswithsoftmu),maskDJ(bjetsnomu)]
    make1Dplot(vars,labels,"DeepJet CvsB","DJ_b_CvsB","DeepJet",masks)

make2Dplot(cjets.DeepFlavCvsL,cjets.DeepFlavCvsB,cjetswithsoftmu.DeepFlavCvsL,cjetswithsoftmu.DeepFlavCvsB,"DeepJet","2D_DJ_c",[maskDJ(cjets),maskDJ(cjetswithsoftmu)])
make2Dplot(bjets.DeepFlavCvsL,bjets.DeepFlavCvsB,bjetswithsoftmu.DeepFlavCvsL,bjetswithsoftmu.DeepFlavCvsB,"DeepJet","2D_DJ_b",[maskDJ(bjets),maskDJ(bjetswithsoftmu)])
make2Dplot(cjets.DeepFlavCvsL,cjets.DeepFlavCvsB,cjetsnomu.DeepFlavCvsL,cjetsnomu.DeepFlavCvsB,"DeepJet","2D_DJ_c_nomu",[maskDJ(cjets),maskDJ(cjetsnomu)])
make2Dplot(bjets.DeepFlavCvsL,bjets.DeepFlavCvsB,bjetsnomu.DeepFlavCvsL,bjetsnomu.DeepFlavCvsB,"DeepJet","2D_DJ_b_nomu",[maskDJ(bjets),maskDJ(bjetsnomu)])

#DeepCSV
if not batch:
    vars = [DpmJets.CvsL,D0Jets.CvsL,cjetsnomu.CvsL]
    labels = [r"$D^{\pm}$ jets","$D^0$ jets","$D_s$ jets"]
    masks = [maskDC(DpmJets),maskDC(D0Jets),maskDC(cjetsnomu)]
    make1Dplot(vars,labels,"DeepCSV CvsL","DC_Djets_CvsL","DeepCSV",masks)
    vars = [DpmJets.CvsB,D0Jets.CvsB,DsJets.CvsB]
    labels = [r"$D^{\pm}$ jets","$D^0$ jets","$D_s$ jets"]
    masks = [maskDC(DpmJets),maskDC(D0Jets),maskDC(DsJets)]
    make1Dplot(vars,labels,"DeepCSV CvsB","DC_Djet_CvsB","DeepCSV",masks)

    vars = [cjets.CvsL,cjetswithsoftmu.CvsL,cjetsnomu.CvsL]
    labels = ["All c jets","With soft mu","No soft mu"]
    masks = [maskDC(cjets),maskDC(cjetswithsoftmu),maskDC(cjetsnomu)]
    make1Dplot(vars,labels,"DeepCSV CvsL","DC_c_CvsL","DeepCSV",masks=masks)

    vars = [cjets.CvsB,cjetswithsoftmu.CvsB,cjetsnomu.CvsB]
    labels = ["All c jets","With soft mu","No soft mu"]
    masks = [maskDC(cjets),maskDC(cjetswithsoftmu),maskDC(cjetsnomu)]
    make1Dplot(vars,labels,"DeepCSV CvsB","DC_c_CvsB","DeepCSV",masks=masks)

    vars = [bjets.CvsL,bjetswithsoftmu.CvsL,bjetsnomu.CvsL]
    labels = ["All b jets","With soft mu","No soft mu"]
    masks = [maskDC(bjets),maskDC(bjetswithsoftmu),maskDC(bjetsnomu)]
    make1Dplot(vars,labels,"DeepCSV CvsL","DC_b_CvsL","DeepCSV",masks=masks)

    vars = [bjets.CvsB,bjetswithsoftmu.CvsB,bjetsnomu.CvsB]
    labels = ["All b jets","With soft mu","No soft mu"]
    masks = [maskDC(bjets),maskDC(bjetswithsoftmu),maskDC(bjetsnomu)]
    make1Dplot(vars,labels,"DeepCSV CvsB","DC_b_CvsB","DeepCSV",masks=masks)

make2Dplot(cjets.CvsL,cjets.CvsB,cjetswithsoftmu.CvsL,cjetswithsoftmu.CvsB,"DeepCSV","2D_DC_c",[maskDC(cjets),maskDC(cjetswithsoftmu)])
make2Dplot(bjets.CvsL,bjets.CvsB,bjetswithsoftmu.CvsL,bjetswithsoftmu.CvsB,"DeepCSV","2D_DC_b",[maskDC(bjets),maskDC(bjetswithsoftmu)])
make2Dplot(cjets.CvsL,cjets.CvsB,cjetsnomu.CvsL,cjetsnomu.CvsB,"DeepCSV","2D_DC_c_nomu",[maskDC(cjets),maskDC(cjetsnomu)])
make2Dplot(bjets.CvsL,bjets.CvsB,bjetsnomu.CvsL,bjetsnomu.CvsB,"DeepCSV","2D_DC_b_nomu",[maskDC(bjets),maskDC(bjetsnomu)])

print("Done with",fname.split('/')[-1])