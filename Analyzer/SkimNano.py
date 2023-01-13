from ROOT import RDataFrame,RDF,ROOT,std
import os, sys
ROOT.EnableImplicitMT(2)

def doSkim(inpname,outname="skimmed.root"):
    d = RDataFrame('Events', inpname)

    sel = '''(Sum(Electron_pt > 15 && Electron_mvaFall17V2Iso_WP90) >= 2  ||
    Sum(Muon_pt > 12) >= 2 ||
    Sum(Electron_pt > 30 && Electron_mvaFall17V2Iso_WP80) >= 1   ||
    Sum(Muon_pt > 24 && Muon_tightId) >= 1 ||
    (Sum(Muon_pt > 12) >=1 && Sum(Electron_pt > 15 && Electron_mvaFall17V2Iso_WP90) >= 1 ) )
    && (Sum(abs(Jet_eta)<2.5 && Jet_pt > 18 && Jet_jetId) >= 1) 
    '''

    dOut = d.Filter(sel)

    varsToSave = ['event', 'run', 'luminosityBlock','Jet_.*','MET_p.*','MET_s.*','RawMET_.*','Electron_.*','Muon_.*','nGenPart','GenPart_.*','genWeight','pu.*','Pileup_n.*','LHE.*','PS.*','PV.*','nSV','SV.*','nJet','nElectron','nMuon','nLHE.*','nPSWeight',
    'HLT_IsoMu24','HLT_IsoTkMu24','HLT_Ele27_WPTight_Gsf','HLT_Ele32_WPTight_Gsf_L1DoubleEG','HLT_IsoMu27','HLT_Ele32_WPTight_Gsf',
    'HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL','HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ','HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL','HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ','HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8','HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8','HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL','HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ',
    "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL",
    "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
    "HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL",
    "HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
    "HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL",
    "HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
    "HLT_Mu8_TrkIsoVVL_Ele17_CaloIdL_TrackIdL_IsoVL",
    "HLT_Mu17_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL",
    "HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL",
    "HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_DZ",
    "HLT_Mu8_DiEle12_CaloIdL_TrackIdL",
    "HLT_DiMu9_Ele9_CaloIdL_TrackIdL"]

    outVars = "("+"|".join(varsToSave)+")"

    print "Starting skim event loop..."
    dOut.Snapshot("Events", outname, outVars)

    dR = RDataFrame('Runs', inpname)
    opts = RDF.RSnapshotOptions()
    opts.fMode = "UPDATE"
    dR.Snapshot("Runs", outname, '.*', opts)
    #(run|genEventCount|genEventSumw|genEventSumw2|nLHEScaleSumw|LHEScaleSumw|nLHEPdfSumw|LHEPdfSumw)

    print "Produced skimmed file:",outname

if __name__=="__main__":
    doSkim(sys.argv[1])