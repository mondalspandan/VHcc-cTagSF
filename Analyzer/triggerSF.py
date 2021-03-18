from ROOT import *
gROOT.SetBatch(True)
TH1DModel = ROOT.Experimental.TDF.TH1DModel

# fileglob = "/pnfs/desy.de/cms/tier2/store/user/lmastrol/VHcc_2017V5_Dec18/SingleElectron/Run2017B-31Mar2018-v195/181214_174022/0000/tree_100.root"
fileglob = "/pnfs/desy.de/cms/tier2/store/user/lmastrol/VHcc_2017V5_Dec18/SingleElectron/Run2017B-31Mar2018-v195/181214_174022/0000/*.root"
mainDF = ROOT.Experimental.TDataFrame("Events", fileglob)

trigName = "HLT_Ele32_WPTight_Gsf_L1DoubleEG"
xlow = 25
xhigh = 100
nBins = (xhigh-xlow)*2

filterStr = "nElectron>=1"

filtDF = mainDF.Filter(filterStr).Define("leadElePt","Electron_pt[0]")
notrig = filtDF.Histo1D(   TH1DModel("No_trigger","No Trigger",nBins,xlow,xhigh),
                                             "leadElePt"
                                         )

withtrig = filtDF.Filter("%s == 1"%trigName)           \
                     .Histo1D(   TH1DModel("With_trigger","Trigger %s"%trigName,nBins,xlow,xhigh),
                                          "leadElePt"
                                      )
print "Starting loop"
print "Total:", notrig.Integral()
print "Pass:", withtrig.Integral()
withtrig.Sumw2()
notrig.Sumw2()
trigSF = withtrig.Clone()
trigSF.Divide(notrig.Clone())
trigSF.SetBinContent(nBins+1, trigSF.GetBinContent(nBins))
trigSF.SetName("TrigSF")
trigSF.SetTitle("TrigSF: %s"%trigName)
outroot = TFile("trigSF.root","RECREATE")
outroot.cd()
notrig.Write()
withtrig.Write()
trigSF.Write()
outroot.Close()
