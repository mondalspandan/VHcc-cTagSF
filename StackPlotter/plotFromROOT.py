from ROOT import TFile,kBlue,kRed,kGreen,kGray,THStack,TPad,TCanvas,TLine,TLatex,gROOT,TGaxis,TColor,gStyle,TLegend,kBlack
import os,sys,math,argparse,pickle,numpy as np

gROOT.SetBatch(1)
gStyle.SetLegendBorderSize(0)
TGaxis.SetMaxDigits(4)

parser = argparse.ArgumentParser("Combine different channels into one single plot")
parser.add_argument('-i', '--indir',type=str,default="")
parser.add_argument('-o','--outdir',type=str,default="")
parser.add_argument('-y','--year',type=str,default="2017")
parser.add_argument('-p','--propagate',action="store_true",default=False)
parser.add_argument('-nostat','--nostat',action="store_true",default=False)
parser.add_argument('-lim','--prelim',action="store_true",default=False)
parser.add_argument('-unc','--uncdir',type=str,default="../ROC_with_SF/uncplots_v7/")
parser.add_argument('-sf','--sf',type=str,default="../SFExtractor/SFs_new/DeepCSV_ctagSF_MiniAOD94X_2017_pTincl_v3_2.root")
#parser.add_argument('-scan','--scanResults',action="store_true",default=False)
args = parser.parse_args()

if '2018' in args.year: lumi = 59900
elif '2016' in args.year: lumi = 35900
else: lumi = 41500

def drawHisto(histlist,histoD,xTitle,yTitle,outName,uncHists=""):    
    legend = TLegend(0.35, 0.72, 0.85, 0.92,"") #,"brNDC"
    legend.SetFillStyle(0)

    legend.SetTextSize(0.045)
    legend.SetNColumns(2)

    myStack = THStack("myStack","")
    for hist in histlist:
        myStack.Add(hist,"hist")
    
    histoErr = histlist[0].Clone()
    for iHist in range(1,len(histlist)):
        histoErr.Add(histlist[iHist])
        
    MCCount = myStack.GetStack().Last().Integral()
    DataCount = histoD.Integral()
    MCNormFactor = DataCount/MCCount

#    myStack.Delete()
    myStack = THStack("myStack","")

    for hist in histlist:
        hist.Scale(MCNormFactor)
        myStack.Add(hist,"hist")
        

    histoErr.Scale(MCNormFactor)
    

    if uncHists!="":
        MCMean = myStack.GetStack().Last().Clone()
        MCErr = MCMean.Clone()
        MCErr.Reset()
        for ibin in range(1,MCMean.GetNbinsX()+1):
            thisbinunc = 0
            for ihist in uncHists:
                thisbinunc += ihist.GetBinContent(ibin)**2     #sum assuming correlated
            sfunc = thisbinunc**0.5*MCNormFactor
            if args.nostat:
                MCMean.SetBinError(ibin, sfunc)
                MCErr.SetBinContent(ibin, sfunc)
            else:
                MCMean.SetBinError(ibin, math.sqrt(sfunc**2 + histoErr.GetBinError(ibin)**2))
                MCErr.SetBinContent(ibin, math.sqrt(sfunc**2 + histoErr.GetBinError(ibin)**2))
        
    c = TCanvas("main","main",1200,1200)
    c.SetCanvasSize(1200,1200)
    
    upperCanvas = TPad("up","up",0,0.24,1,1)
    upperCanvas.SetBottomMargin(0.03)
    upperCanvas.SetLeftMargin(0.12)
    upperCanvas.SetTopMargin(0.06)
#    upperCanvas.SetLogy(isLog)
    upperCanvas.Draw()
    upperCanvas.cd()
    
    myStack.Draw()
    myStack.GetYaxis().SetTitle(yTitle)
    myStack.GetHistogram().GetZaxis().SetTitle()

    myStack.GetYaxis().SetLabelSize(0.048)
    myStack.GetYaxis().SetTitleSize(0.07)
    myStack.GetYaxis().SetTitleOffset(0.78)
    myStack.GetYaxis().SetTitleFont(42)
    legend.Draw("same")

    if uncHists!="":
        MCMean.Draw("e2 same")
        MCMean.SetFillColor(kGreen)
        MCMean.SetLineColor(kGreen)
        MCMean.SetMarkerSize(0)
        MCMean.SetFillStyle(3013)
        
    if not args.nostat:
        histoErr.Draw("e2 same")
        # histoErr.Sumw2()
        histoErr.SetFillColor(kGray+3)
        histoErr.SetLineColor(kGray+3)
        histoErr.SetMarkerSize(0)
        histoErr.SetFillStyle(3013)       

    histoMC = myStack.GetStack().Last()
    histoBkg= myStack.GetStack().Before(histoMC)

    print "Total MC:", histoMC.Integral(), ", Data:",histoD.Integral()


    histoD.Draw("same p e")
    legend.AddEntry(histoD,"Data","PE")
    
    for hist in histlist:
        legend.AddEntry(hist,hist.GetName().replace('uds','udsg').replace('b','bottom').replace('c','charm'),'f')
    legend.AddEntry(histoErr,"MC Stat. Unc.",'f')
    if uncHists!="": legend.AddEntry(MCMean,"SF Unc.",'f')
    maxY = histoD.GetMaximum()
    
    #if myStack.GetMinimum() >= 0:
    myStack.SetMinimum(1e-3)
    myStack.SetMaximum(maxY*1.35)


    c.cd()
    lowerCanvas = TPad("down","down",0,0,1,0.26)
    lowerCanvas.Draw()
    lowerCanvas.cd()
    lowerCanvas.SetTicky(1)
    lowerCanvas.SetLeftMargin(0.1)
    lowerCanvas.SetRightMargin(0.1)
    lowerCanvas.SetTopMargin(0.0)
    lowerCanvas.SetBottomMargin(0.4)
    lowerCanvas.SetLeftMargin(0.12)
    lowerCanvas.SetFrameFillStyle(0)
    lowerCanvas.SetFrameBorderMode(0)
    lowerCanvas.SetGridy()

    histoRatio = histoD.Clone()
    histoRatio.Divide(histoMC)
    for ib in range(1,histoRatio.GetNbinsX()+1):
        if histoD.GetBinContent(ib) != 0:
            histoRatio.SetBinError(ib, histoD.GetBinError(ib)/histoD.GetBinContent(ib)*histoRatio.GetBinContent(ib))
        else:
            histoRatio.SetBinError(ib,0.)

    histoRatio.GetYaxis().SetTitle("Data/MC")
    histoRatio.GetYaxis().SetTitleSize(0.15)
    histoRatio.GetYaxis().SetTitleOffset(0.38)
    histoRatio.GetYaxis().SetTitleFont(42)
    histoRatio.GetYaxis().SetLabelSize(0.14)
    histoRatio.GetYaxis().CenterTitle()
    histoRatio.GetYaxis().SetLabelFont(42)
    histoRatio.GetYaxis().SetNdivisions(5)

    histoRatio.GetXaxis().SetTitle(xTitle)
    histoRatio.GetXaxis().SetLabelSize(0.14)
    histoRatio.GetXaxis().SetTitleSize(0.19)
    histoRatio.GetXaxis().SetTitleOffset(0.88)
    histoRatio.GetXaxis().SetTitleFont(42)
    histoRatio.GetXaxis().SetTickLength(0.07)
    histoRatio.GetXaxis().SetLabelFont(42)
    histoRatio.SetTitle("")

    histoRatio.Draw("P e")
    histoRatio.SetMaximum(1.49)
    histoRatio.SetMinimum(0.51)

    if uncHists!="":
        RatioErr = MCErr.Clone()
        RatioErr.Divide(histoMC)
        RatioErrVals = RatioErr.Clone()
        for ibin in range(1,RatioErr.GetNbinsX()+1):
            RatioErrVals.SetBinContent(ibin,1.)
            RatioErrVals.SetBinError(ibin,RatioErr.GetBinContent(ibin))

        RatioErrVals.Draw("e2 same")
        RatioErrVals.SetFillColor(kGreen)
        RatioErrVals.SetLineColor(kGreen)
        RatioErrVals.SetMarkerSize(0)
        RatioErrVals.SetFillStyle(3013)

    if not args.nostat:
        RatioStatUnc = histoMC.Clone()
        for ibin in range(1,RatioStatUnc.GetNbinsX()+1):
            RatioStatUnc.SetBinContent(ibin,1)
            if histoMC.GetBinContent(ibin) != 0:
                RatioStatUnc.SetBinError(ibin,histoMC.GetBinError(ibin)/histoMC.GetBinContent(ibin))
            else:
                RatioStatUnc.SetBinError(ibin,0)

        RatioStatUnc.Draw("e2 same")
        RatioStatUnc.SetFillColor(kGray+3)
        RatioStatUnc.SetLineColor(kGray+3)
        RatioStatUnc.SetMarkerSize(0)
        RatioStatUnc.SetFillStyle(3013) 
    
    histoRatio.Draw("P e same")  # To bring on top

    hLine = TLine(-0.2,1,1,1)
    hLine.SetLineColor(kRed)
    hLine.Draw()

#    if drawDataMCRatioLine:
#        MCCount = histoMC.Integral()
#        if MCCount > 0.:
#            DataCount = histoD.Integral()
#            MCNormFactor = DataCount/MCCount
#            hLine2 = TLine(start,MCNormFactor,end,MCNormFactor)
#            hLine2.SetLineColor(kBlue)
#            hLine2.Draw()

    # ----------------------------------------------------------

    # ======================== LaTeX ==========================
    texTL = TLatex()
    texTL.SetTextSize(0.07)
    texTL.SetTextAlign(13)

    texTR = TLatex()
    texTR.SetTextSize(0.05)
    texTR.SetTextAlign(31)

#    if dataset=="" or noRatio:
#        texTL.DrawLatexNDC(0.13,0.87, "CMS #it{#bf{Preliminary}}")
#        texTR.DrawLatexNDC(0.89,0.91, "#bf{"+str(lumi/1000.)+" fb^{-1} (13 TeV)}")
#    else:
    upperCanvas.cd()
    
    texTL.DrawLatexNDC(0.16,0.92, "CMS") # #it{#bf{Preliminary}}")
    if args.prelim:
        texTL2 = TLatex()
        texTL2.SetTextSize(0.05)
        texTL2.SetTextAlign(13)
        suff = "#it{#bf{Preliminary}}"
        texTL2.DrawLatexNDC(0.16,0.85, suff)

    texTR.DrawLatexNDC(0.89,0.95, "#bf{"+str(lumi/1000.)+" fb^{-1} (13 TeV)}")
    # ----------------------------------------------------------

    c.SaveAs(outName+".pdf")
    c.SaveAs(outName+".png")
    
    
indir = args.indir
outdir = args.outdir
# if len(sys.argv) > 3 and sys.argv[3]!="":
#     isPostSF = True
    # indirsyst = sys.argv[3]
    # rootlistUp = [i for i in os.listdir(indirsyst) if i.endswith ('.root') and "Up" in i]
    # rootlistDown = [i for i in os.listdir(indirsyst) if i.endswith ('.root') and "Down" in i]
rootlist = [i for i in os.listdir(indir) if "Up" not in i and "Down" not in i and ((i.endswith ('.root') and i.rstrip(".root").endswith('_')) or i.rstrip().endswith('_'))]
print 

os.system("mkdir -p "+outdir)
for tagger in ["DeepJet","DeepCSV"]:
  for xvar in ["CvsL","CvsB"]:
    for sel in ["Wc","TT","DY"]:
        histdict = {"c":"","b":"","uds":"","data":"","SFUnc":[]}
        UncArg = ""
        count = 0
        for rootfile in rootlist:
            reg = rootfile.split("_")[0]
#            print reg,sel,rootfile
            if reg != sel: continue
            if xvar not in rootfile: continue
            if tagger == "DeepCSV" and "DeepFlav" in rootfile: continue
            if tagger == "DeepJet" and "DeepFlav" not in rootfile: continue
            if sel == "Wc": yTitle = "Jets, OS-SS subtracted"
            else: yTitle = "Jets"
            
            f = TFile.Open(indir+"/"+rootfile)
            c = f.Get("c")
            b = f.Get("b")
            uds = f.Get("uds")
            lep = f.Get("lep")
            MCSum = f.Get("MCSum")
            data = f.Get("Data")
            c.SetDirectory(0)
            b.SetDirectory(0)
            uds.SetDirectory(0)
            lep.SetDirectory(0)
            data.SetDirectory(0)
            
            uds.Add(lep) 
            f.Close()
            
            if histdict["c"] == "":
                histdict["c"] = c
                histdict["b"] = b
                histdict["uds"] = uds
                histdict["data"] = data
                histdict["c"].SetFillColor(TColor.GetColor("#82E3FF"))
                histdict["b"].SetFillColor(TColor.GetColor("#FF548B"))
                histdict["uds"].SetFillColor(TColor.GetColor("#FFF18F"))
            else:
                histdict["c"].Add(c)
                histdict["b"].Add(b)
                histdict["uds"].Add(uds)
                histdict["data"].Add(data)

            f.Close()
            count += 1
        
        def makeUncHist(hist,flav,tagger,xvar):
            varn = xvar.replace('s','')
            tag = 'd' if 'CSV' in tagger else 'df'
            fl = flav.replace('uds','udsg')
            fl2 = flav.replace('uds','l')
            sffile = args.sf if 'CSV' in tagger else args.sf.replace('CSV','Jet')
            sfr = TFile.Open(sffile,'READ')
            sfvals = sfr.Get("SF%s_hist"%fl2)
            sfvalsup = sfr.Get("SF%s_hist_TotalUncUp"%fl2)
            sfvalsdown = sfr.Get("SF%s_hist_TotalUncDown"%fl2)
            upunc = sfvalsup.GetBinContent(0,0)
            downunc = sfvalsdown.GetBinContent(0,0)
            m1unc = max(upunc,downunc)/sfvals.GetBinContent(0,0)
            sfr.Close()

            pklfile = args.uncdir+'/statonly_%s%s_truth%s.pkl'%(tag,varn,fl)
            unchiststatnp = pickle.load(open(pklfile,'rb'))
            pklfile = args.uncdir+'/nostat_%s%s_truth%s.pkl'%(tag,varn,fl)
            unchistsystnp = pickle.load(open(pklfile,'rb'))
            # print unchiststatnp
            unchist = hist.Clone()
            unchist.Reset()
            unchist.SetBinContent(3,m1unc*hist.GetBinContent(3))
            for ib in range(6,unchist.GetNbinsX()+1):
                # print hist.GetBinContent(ib),unchiststatnp[ib-1]
                unchist.SetBinContent(ib,np.sqrt(unchiststatnp[ib-1]**2+unchistsystnp[ib-1]**2)*hist.GetBinContent(ib))
            return unchist

        if count > 0:
            if args.propagate:
                UncArg = []
                for fl in ['c','b','uds']:
                    UncArg.append(makeUncHist(histdict[fl],fl,tagger,xvar))
        
            drawHisto([histdict["uds"],histdict["b"],histdict["c"]],histdict["data"],"%s %s"%(tagger,xvar),yTitle,"%s/%s_%s_%s"%(outdir,sel,tagger,xvar),UncArg)
