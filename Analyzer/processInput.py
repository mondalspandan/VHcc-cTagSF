import sys,os,json,time
from ROOT import TFile


# ==================== File stuff and condor compatibility =====================
JECNameList = ["nom","jesTotalUp","jesTotalDown","jerUp","jerDown"]
fileName = str(sys.argv[1])
fullName = fileName

if len(sys.argv) > 2: JECidx = int(sys.argv[2])
else: JECidx = 0
JECName = JECNameList[JECidx]

maxEvents=-1

debug = False
isNano = False
pref = ""
parentDir = ""
pnfspref = "/pnfs/desy.de/cms/tier2/"

if os.path.isfile(fullName):
    pref = ""
    print "Input file is local."
    loc = True
elif os.path.isfile(pnfspref+fullName):
    pref = pnfspref    
    print "Input file is local on /pnfs."
    loc = True
elif fullName.startswith("root:"):
    pref = ""
    print "Input file name is in AAA format."
    loc = False
else:
    pref = "root://xrootd-cms.infn.it//"
    print "Forcing AAA."
    if not fullName.startswith("/store/"):
        fileName = "/" + '/'.join(fullName.split('/')[fullName.split('/').index("store"):])
    loc = False

parentDirList = ["VHcc_2017V5_Dec18/","NanoCrabProdXmas/","/2016/","2016_v2/","/2017/","/2017_v2/","/2018/","VHcc_2016V4bis_Nov18/","RunIISummer20UL17NanoAODv9/"]
for iParent in parentDirList:
    if iParent in fullName: parentDir = iParent

if parentDir == "" and len(fullName.split('/')) >=5:
    parentDir = fullName.split('/')[3]+"/"

if parentDir != "":
    sampName=fullName.split(parentDir)[1].split('/')[0]
    sampNo=fullName.split(parentDir)[1].split('/')[1].split('_')[-1]
    dirNo=fullName.split(parentDir)[1].split('/')[3][-1]
    flNo=fullName.split(parentDir)[1].split('/')[-1].rstrip('.root').split('_')[-1]
    outNo= "%s_%s_%s"%(sampNo,dirNo,flNo)
else:
    sampName = "local"
    outNo = "1"

era = 2016
if "UL2017" in fullName or "UL17" in fullName: era = "UL2017"
elif "UL2018" in fullName or "UL18" in fullName: era = "UL2018"
elif "UL2016" in fullName or "UL16" in fullName:
    if "APV" in fullName or "HIPM" in fullName: era = "UL2016Pre"
    else:  era = "UL2016Post"
elif "2017" in fullName: era = 2017
elif "2018" in fullName: era = 2018
elif "2016" in fullName: era = 2016



if 'Single' in fullName or 'Double' in fullName or 'EGamma' in fullName or 'MuonEG' in fullName:
    isMC = False
else:
    isMC = True
print "isMC:", isMC, "; era: %s"%era
print "Using jet pT with JEC correction:", JECName
print "Output file will be numbered", outNo, "by condor."

if not isMC and "jer" in JECName:
    print "Cannot run data with JER systematics!! Exiting."
    sys.exit()

dirName=open("dirName.sh",'w')
sampNamebu = sampName
if isMC and JECName!="nom":
    sampName += "_"+JECName
dirName.write("echo \""+sampName+"\"")
dirName.close()

flName=open("flName.sh",'w')
flName.write("echo \"%s\""%outNo)
flName.close()

def fileExists(rootfile,checkSkim=False):
    if os.path.isfile(rootfile):
         testfile = TFile.Open(rootfile)
         try:
             treelist = [i.GetName() for i in testfile.GetListOfKeys()]
         except:
             print "File exists but is zombie."
             return False
         skimok = treelist.count("Events") == 1 and treelist.count("Runs") == 1
         if not testfile or testfile.IsZombie() or testfile.TestBit(TFile.kRecovered):
             print "File exists but is zombie."
             return False
         elif checkSkim and not skimok:
             print "File exists but somehow has unexpected trees:",treelist
             return False
         else:             
             return True
    else:
        return False


if "OUTPUTDIR" in os.environ:
    condoroutdir = os.environ["OUTPUTDIR"]
    condoroutfile = "%s/%s/outTree_%s.root"%(condoroutdir,sampName,outNo)
    if fileExists(condoroutfile):
        print "Output file already exists."
        print "Outfile file: %s"%condoroutfile
        sys.exit(99)
    else:
        print "Will continue."
        
# ==============================================================================

if False:
    print "Will open file %s."%(pref+fileName)
    toopen = pref+fileName
else:
    skimdir = "/nfs/dust/cms/user/spmondal/ctag_skim/%s_2207"%era
    skimname = "%s/%s/skimmed_%s.root"%(skimdir,sampNamebu,outNo)
    if fileExists(skimname,True):
        print "Skimmed file already exists."        
        toopen = skimname
    elif fileExists("skimmed.root"):
        print "Skimmed file already exists locally. Will not re-skim." 
        toopen = "skimmed.root"
    else:        
        print "Will skim %s."%(pref+fileName)
        from SkimNano import *
        start_skim = time.time()
        doSkim(pref+fileName,outname="skimmed.root")
        print "Done skimming."
        skim_time = time.time() - start_skim
        if skim_time > 3600:
            os.system("mkdir -p %s/%s"%(skimdir,sampNamebu))
            os.system("scp skimmed.root "+skimname)
            toopen = "skimmed.root"
            print "Caching skimmed file on /nfs for future use."
        else:
            toopen = "skimmed.root"

    print  "Running analyzer on %s."%toopen

iFile = TFile.Open(toopen)

inputTree = iFile.Get("Events")
inputTree.SetBranchStatus("*",1)


# =============================== SF files =====================================
# PU
# PU2016File = TFile('scalefactors/pileUPinfo2016.root')
# pileup2016histo = PU2016File.Get('hpileUPhist')

# EGamma
if era == 2016: EIDFile = TFile('scalefactors/egammaSF_mva80.root')
elif era == 2017: EIDFile = TFile('scalefactors2017/ElectronIDSF_94X_MVA80WP.root')
elif era == 2018: EIDFile = TFile('scalefactors2018/ElectronIDSF_2018_MVA80WP.root')
elif era == "UL2017": EIDFile = TFile('scalefactorsUL2017/egammaEffi.txt_EGM2D_MVA80iso_UL17.root')
elif era == "UL2018": EIDFile = TFile('scalefactorsUL2018/egammaEffi.txt_Ele_wp80iso_EGM2D.root')
elif era == "UL2016Pre": EIDFile = TFile('scalefactorsUL2016/egammaEffi.txt_Ele_wp80iso_preVFP_EGM2D.root')
elif era == "UL2016Post": EIDFile = TFile('scalefactorsUL2016/egammaEffi.txt_Ele_wp80iso_postVFP_EGM2D.root')
EGammaHisto2d = EIDFile.Get('EGamma_SF2D')

if era == 2017: ERecoFile = TFile('scalefactors2017/ElectronRecoSF_94X.root')
elif era == 2018: ERecoFile = TFile('scalefactors2018/ElectronRecoSF_2018.root') 
elif era == "UL2017": ERecoFile = TFile('scalefactorsUL2017/egammaEffi_ptAbove20.txt_EGM2D_UL2017.root')   
elif era == "UL2018": ERecoFile = TFile('scalefactorsUL2018/egammaEffi_ptAbove20.txt_EGM2D_UL2018.root')   
elif era == "UL2016Pre": ERecoFile = TFile('scalefactorsUL2016/egammaEffi_ptAbove20.txt_EGM2D_UL2016preVFP.root')
elif era == "UL2016Post": ERecoFile = TFile('scalefactorsUL2016/egammaEffi_ptAbove20.txt_EGM2D_UL2016postVFP.root')

if era == 2017 or era == 2018 or "UL" in era:
    ERecoHisto2d = ERecoFile.Get('EGamma_SF2D')
    
    etrigf = open("scalefactors2017/VHbb1ElectronTrigger2017.json",'r')
    etrigjson = json.load(etrigf)["singleEleTrigger"]["eta_pt_ratio"]
    etrigf.close()

# Muon
if era == 2016:
    MuID2016BFFile = TFile('scalefactors/RunBCDEF_SF_ID.root')
    MuID2016BFhisto2d = MuID2016BFFile.Get('NUM_TightID_DEN_genTracks_eta_pt')
    MuID2016GHFile = TFile('scalefactors/RunGH_SF_ID.root')
    MuID2016GHhisto2d = MuID2016GHFile.Get('NUM_TightID_DEN_genTracks_eta_pt')

elif era == 2017:
    MuID2017BFFile = TFile('scalefactors2017/RunBCDEF_SF_ID.root')
    MuID1718histo2d = MuID2017BFFile.Get('NUM_TightID_DEN_genTracks_pt_abseta')
    MuIso2017BFFile = TFile('scalefactors2017/RunBCDEF_SF_ISO.root')
    MuIso1718histo2d = MuIso2017BFFile.Get('NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta')
    MuTrig2017BFFile = TFile('scalefactors2017/singleMuonTrig.root')
    MuTrig1718histo2d = MuTrig2017BFFile.Get('IsoMu27_PtEtaBins/pt_abseta_ratio')
    MuIDlowpT2017BFFile = TFile('scalefactors2017/RunBCDEF_SF_MuID_lowpT.root')
    MuIDlowpT1718histo2d = MuIDlowpT2017BFFile.Get('NUM_TightID_DEN_genTracks_pt_abseta')

elif era == 2018:
    MuID2018File = TFile('scalefactors2018/RunABCD_SF_ID.root')
    MuID1718histo2d = MuID2018File.Get('NUM_TightID_DEN_TrackerMuons_pt_abseta')
    MuIso2018File = TFile('scalefactors2018/RunABCD_SF_ISO.root')
    MuIso1718histo2d = MuIso2018File.Get('NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta')
    MuTrig2018File = TFile('scalefactors2018/singleMuonTrig.root')
    MuTrig1718histo2d = MuTrig2018File.Get('IsoMu24_PtEtaBins/pt_abseta_ratio')
    MuIDlowpT2018File = TFile('scalefactors2018/RunABCD_SF_MuID_lowpT.root')
    MuIDlowpT1718histo2d = MuIDlowpT2018File.Get('NUM_TightID_DEN_genTracks_pt_abseta')

elif era == "UL2017":
    MuID2017BFFile = TFile('scalefactorsUL2017/Efficiencies_muon_generalTracks_Z_Run2017_UL_ID.root')
    MuID1718histo2d = MuID2017BFFile.Get('NUM_TightID_DEN_TrackerMuons_abseta_pt')
    MuIso2017BFFile = TFile('scalefactorsUL2017/Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root') 
    MuIso1718histo2d = MuIso2017BFFile.Get('NUM_TightRelIso_DEN_TightIDandIPCut_abseta_pt')
    MuTrig2017BFFile = TFile('scalefactors2017/singleMuonTrig.root')                            # Keep EOY 2017
    MuTrig1718histo2d = MuTrig2017BFFile.Get('IsoMu27_PtEtaBins/pt_abseta_ratio')
    MuIDlowpT2017BFFile = TFile('scalefactorsUL2017/Efficiency_muon_generalTracks_Run2017_UL_trackerMuon_Reco.root')  #Actually Reco SFs
    MuIDlowpT1718histo2d = MuIDlowpT2017BFFile.Get('NUM_TrackerMuons_DEN_genTracks')

elif era == "UL2018":
    MuID2017BFFile = TFile('scalefactorsUL2018/Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.root')
    MuID1718histo2d = MuID2017BFFile.Get('NUM_TightID_DEN_TrackerMuons_abseta_pt')
    MuIso2017BFFile = TFile('scalefactorsUL2018/Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root') 
    MuIso1718histo2d = MuIso2017BFFile.Get('NUM_TightRelIso_DEN_TightIDandIPCut_abseta_pt')
    MuTrig2018File = TFile('scalefactors2018/singleMuonTrig.root')
    MuTrig1718histo2d = MuTrig2018File.Get('IsoMu24_PtEtaBins/pt_abseta_ratio')
    MuIDlowpT2017BFFile = TFile('scalefactorsUL2018/Efficiency_muon_generalTracks_Run2018_UL_trackerMuon.root')  #Actually Reco SFs
    MuIDlowpT1718histo2d = MuIDlowpT2017BFFile.Get('NUM_TrackerMuons_DEN_genTracks')

elif era == "UL2016Pre":
    MuID2017BFFile = TFile('scalefactorsUL2016/Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ID.root')
    MuID1718histo2d = MuID2017BFFile.Get('NUM_TightID_DEN_TrackerMuons_abseta_pt')
    MuIso2017BFFile = TFile('scalefactorsUL2016/Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root') 
    MuIso1718histo2d = MuIso2017BFFile.Get('NUM_TightRelIso_DEN_TightIDandIPCut_abseta_pt')
    MuIDlowpT2017BFFile = TFile('scalefactorsUL2016/Efficiency_muon_generalTracks_Run2016preVFP_UL_trackerMuon.root')  #Actually Reco SFs
    MuIDlowpT1718histo2d = MuIDlowpT2017BFFile.Get('NUM_TrackerMuons_DEN_genTracks')

elif era == "UL2016Post":
    MuID2017BFFile = TFile('scalefactorsUL2016/Efficiencies_muon_generalTracks_Z_Run2016_UL_ID.root')
    MuID1718histo2d = MuID2017BFFile.Get('NUM_TightID_DEN_TrackerMuons_abseta_pt')
    MuIso2017BFFile = TFile('scalefactorsUL2016/Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root') 
    MuIso1718histo2d = MuIso2017BFFile.Get('NUM_TightRelIso_DEN_TightIDandIPCut_abseta_pt')
    MuIDlowpT2017BFFile = TFile('scalefactorsUL2016/Efficiency_muon_generalTracks_Run2016postVFP_UL_trackerMuon.root')  #Actually Reco SFs
    MuIDlowpT1718histo2d = MuIDlowpT2017BFFile.Get('NUM_TrackerMuons_DEN_genTracks')

def getSF(dict, pT, eta):
    for etas in dict:
        rng = etas.split(':')[1].strip('[').strip(']').split(',')
        if eta >= float(rng[0]) and eta <= float(rng[1]):
            subdict = dict[etas]
            for pTs in subdict:
                rng2 = pTs.split(':')[1].strip('[').strip(']').split(',')
                if pT >= float(rng2[0]) and pT <= float(rng2[1]):
                    tuple = subdict[pTs]
                    return tuple['value'],tuple['error']
            break
    return 1.,0.

#PU
if era == 2018:
    datapufile = 'scalefactors2018/mcPileup2018.root'
    mcpufile = 'scalefactors2018/mcPileup2018.root'
elif era == "UL2017":
    datapufile = 'scalefactorsUL2017/PileupHistogram-UL2017-100bins_withVar.root'
    mcpufile = 'scalefactorsUL2017/mcPileupUL2017.root'
elif era == "UL2018":
    datapufile = 'scalefactorsUL2018/PileupHistogram-UL2018-100bins_withVar.root'
    mcpufile = 'scalefactorsUL2018/mcPileupUL2018.root'
elif "UL2016" in era:
    datapufile = 'scalefactorsUL2016/PileupHistogram-UL2016-100bins_withVar.root'
    mcpufile = 'scalefactorsUL2016/mcPileupUL2016.root'

if era == 2018 or era == "UL2017" or era == "UL2018" or "UL2016" in era:
    PUdatafile = TFile(datapufile)
    PUmcfile = TFile(mcpufile)
    hdataPU = PUdatafile.Get("pileup")
    hdataPU_up = PUdatafile.Get("pileup_plus")
    hdataPU_down = PUdatafile.Get("pileup_minus")
    hmcPU = PUmcfile.Get("pu_mc")
    hdataPU.Scale(1./hdataPU.Integral())
    hdataPU_up.Scale(1./hdataPU_up.Integral())
    hdataPU_down.Scale(1./hdataPU_down.Integral())
    hmcPU.Scale(1./hmcPU.Integral())
    maxpu = max(hdataPU.GetBinLowEdge(hdataPU.GetNbinsX()),hdataPU_up.GetBinLowEdge(hdataPU_up.GetNbinsX()),hdataPU_down.GetBinLowEdge(hdataPU_down.GetNbinsX()),hmcPU.GetBinLowEdge(hmcPU.GetNbinsX()))
    
    hpuweight = hdataPU.Clone()
    hpuweight.Divide(hmcPU)
    hpuweight_up = hdataPU_up.Clone()
    hpuweight_up.Divide(hmcPU)
    hpuweight_down = hdataPU_down.Clone()
    hpuweight_down.Divide(hmcPU)
    
def getPUweight(ntrueint,variation):
    if ntrueint < 0 or ntrueint > maxpu-1: return 0.
    if variation == 0: temppu = hpuweight
    elif variation == 1: temppu = hpuweight_up
    elif variation == -1: temppu = hpuweight_down
    else: raise ValueError
    return temppu.GetBinContent(temppu.GetXaxis().FindBin(ntrueint))

# ==============================================================================
