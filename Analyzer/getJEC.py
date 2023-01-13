import numpy as np, sys, math, os 

SFfiles = {
    "UL2017" : ["scalefactorsUL2017/RegroupedV2_Summer19UL17_V5_MC_UncertaintySources_AK4PFchs.txt",
                "scalefactorsUL2017/Summer19UL17_JRV2_MC_SF_AK4PFchs.txt"],
    "UL2018" : ["scalefactorsUL2018/RegroupedV2_Summer19UL18_V5_MC_UncertaintySources_AK4PFchs.txt",
                "scalefactorsUL2018/Summer19UL18_JRV2_MC_SF_AK4PFchs.txt"],
    "UL2016Pre":["scalefactorsUL2016/RegroupedV2_Summer19UL16APV_V7_MC_UncertaintySources_AK4PFchs.txt",
                "scalefactorsUL2016/Summer20UL16APV_JRV3_MC_SF_AK4PFchs.txt"],
    "UL2016Post":["scalefactorsUL2016/RegroupedV2_Summer19UL16_V7_MC_UncertaintySources_AK4PFchs.txt",
                "scalefactorsUL2016/Summer20UL16_JRV3_MC_SF_AK4PFchs.txt"],  
}

JESuncs = {}
JERuncs = {}
JECList = ["nom","jesTotalUp","jesTotalDown","jerUp","jerDown"]

def loadJES(era,syst="Total"):
    global JESuncs
    if era in JESuncs: return

    JESuncs[era] = {}

    fl = SFfiles[era][0]
    if not os.path.isfile(fl): fl = "../Analyzer/"+fl

    with open(fl) as f: lines = f.readlines()
    tot = np.where(np.array(lines)=='[%s]\n'%syst)
    lines = lines[tot[0][0]+2:]

    etabins = []
    ptbins = []
    JESuncs[era]["up"] = []
    JESuncs[era]["down"] = []
    for line in lines:
        line = line.strip()        
        if line == "": continue
        spl = [float(i) for i in line.split()]
        etabins.append(spl[0])

        ptbinsloc = spl[3::3]
        if ptbins == []:
            ptbins = ptbinsloc[:]
        else:
            if ptbinsloc != ptbins:
                print ("Error: Inconsistent pT binning in JES file. Exiting.")
                sys.exit(1)
        
        ups = spl[4::3]
        downs = spl[5::3]
        JESuncs[era]["up"].append(ups[:])
        JESuncs[era]["down"].append(downs[:])
    etabins.append(spl[1])
    ptbins.append(1000000)
    JESuncs[era]["etabins"] = etabins[:]
    JESuncs[era]["ptbins"] = ptbins[:]

def getJES(era,pt,eta,var="up"):
    pt, eta = np.clip(pt,9,10000),np.clip(eta,-5,5)
    loadJES(era)
    etabin = np.digitize(eta,JESuncs[era]["etabins"]) - 1
    ptbin = np.digitize(pt,JESuncs[era]["ptbins"]) - 1   
    if type(etabin) == type(1):
        return np.array(JESuncs[era][var])[etabin][ptbin]
    else:
        return np.array(JESuncs[era][var])[etabin,ptbin]

def loadJER(era):
    global JERuncs
    if era in JERuncs: return

    JERuncs[era] = {}

    fl = SFfiles[era][1]
    if not os.path.isfile(fl): fl = "../Analyzer/"+fl
    with open(fl) as f: lines = f.readlines()[1:]
    
    etabins = []
    JERuncs[era]["nom"] = []
    JERuncs[era]["up"] = []
    JERuncs[era]["down"] = []
    for line in lines:
        line = line.strip()
        if line == "": continue
        spl = [float(i) for i in line.split()]
        etabins.append(spl[0])
        JERuncs[era]["nom"].append(spl[3])
        JERuncs[era]["up"].append(spl[5])
        JERuncs[era]["down"].append(spl[4])
    etabins.append(spl[1])
    JERuncs[era]["etabins"] = etabins[:]

def getJER(era,pt,eta,var="up"):
    pt, eta = np.clip(pt,9,10000),np.clip(eta,-5,5)
    loadJER(era)
    etabin = np.digitize(eta,JERuncs[era]["etabins"]) - 1
    
    return np.array(JERuncs[era][var])[etabin]

def doJECCorr(entry, isMC, era, JECName="nom"):
    if JECName == "jerUp": variation = "up"
    elif JECName == "jerDown": variation = "down"
    else: variation = "nom"

    rawpt = [(1-r)*p for r,p in zip(entry.Jet_rawFactor,entry.Jet_pt)]
    rawmass = [(1-r)*m for r,m in zip(entry.Jet_rawFactor,entry.Jet_mass)]
    if isMC:
        jetPt = [p*getJER(era,i,j,var=variation) for p,i,j in zip(entry.Jet_pt,rawpt,entry.Jet_eta)]
        jetMass = [p*getJER(era,i,j,var=variation) for p,i,j in zip(entry.Jet_mass,rawmass,entry.Jet_eta)]
    else:
        jetPt = entry.Jet_pt
        jetMass = entry.Jet_mass

    if JECName == "jesTotalUp":
        jetPt = [p*(1+getJES(era,i,j,var="up")) for p,i,j in zip(jetPt,rawpt,entry.Jet_eta)]
    elif JECName == "jesTotalDown":
        jetPt = [p*(1-getJES(era,i,j,var="down")) for p,i,j in zip(jetPt,rawpt,entry.Jet_eta)]

    metpt = entry.RawMET_pt
    metphi = entry.RawMET_phi
    metpt_x = metpt*math.cos(metphi)
    metpt_y = metpt*math.sin(metphi)
    for ijet in range(len(jetPt)):
        metpt_x = metpt_x - (jetPt[ijet] - rawpt[ijet])*math.cos(entry.Jet_phi[ijet])
        metpt_y = metpt_y - (jetPt[ijet] - rawpt[ijet])*math.sin(entry.Jet_phi[ijet])

    metPt = math.sqrt(metpt_x**2 + metpt_y**2)
    metPhi = math.atan2(metpt_y, metpt_x) 

    return jetPt, jetMass, metPt, metPhi


def doJECCorrOnDF(df,isMC,era):
    origcols = list(df.columns)
    df["rawpt"] = (1-df["Jet_rawFactor"])*df["Jet_pt"]
    # df["rawmass"] = (1-df["Jet_rawFactor"])*df["Jet_mass"]

    for JECName in JECList:
        if JECName == "jerUp": variation = "up"
        elif JECName == "jerDown": variation = "down"
        else: variation = "nom"

        if isMC:
            df["Jet_pt_"+JECName] = df["Jet_pt"]*getJER(era,df["rawpt"],df["Jet_eta"],var=variation)
            # df["jet_mass_"+JECName] = df["Jet_mass"]*getJER(era,df["rawmass"],df["Jet_eta"],var=variation)
        else:
            df["Jet_pt_"+JECName] = df["Jet_pt"]
            # df["jet_mass_"+JECName] = df["Jet_mass"]

        if JECName == "jesTotalUp":
            df["Jet_pt_"+JECName] = df["Jet_pt_"+JECName]*(1+getJES(era,df["rawpt"],df["Jet_eta"],var="up")) 
        elif JECName == "jesTotalDown":
            df["Jet_pt_"+JECName] = df["Jet_pt_"+JECName]*(1-getJES(era,df["rawpt"],df["Jet_eta"],var="down")) 

    return df[origcols+["Jet_pt_"+i for i in JECList]]

