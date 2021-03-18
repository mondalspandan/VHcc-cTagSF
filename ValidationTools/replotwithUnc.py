from ROOT import *
import os, sys
from array import array
gROOT.SetBatch(True)
gStyle.SetOptStat(0)
gStyle.SetLegendBorderSize(0)
isLog=False
from tabulate import tabulate

inDir=sys.argv[1]
subdirs = [i for i in os.listdir(inDir) if "compare" not in i]

def getName(fl):
#    if 'is_E_' in fl and 'nJet_0-4' in fl:
#        return "W+c(e)"
#    elif 'is_M_' in fl and 'nJet_0-4' in fl:
#        return "W+c(mu)"
#    elif 'is_E_' in fl and 'nJet_5-' in fl:
#        return "TT(e)"
#    elif 'is_M_' in fl and 'nJet_5-' in fl:
#        return "TT(mu)"
#    elif 'is_ME_' in fl:
#        return "TT(mue)"
#    elif 'is_MM_' in fl:
#        return "TT(mumu)"
#    elif 'is_EE_' in fl:
#        return "TT(ee)"
#    else:
#        return "DY"
    return ''.join(fl.split('/')[-1].split('_')[:2])

SFNames = {}

for dir in sorted(subdirs):
    noSF=False
    if dir.endswith("central"): noSF=True
    rootList = [i for i in os.listdir(os.path.join(inDir,dir)) if i.endswith(".root") and "Cvs" in i]
    SFNames[dir] = {}
    for rootfile in sorted(rootList):
        rootNom = TFile.Open(os.path.join(inDir,dir,rootfile),"READ")
        if not rootNom: raise ValueError
        MCNom = rootNom.Get("MCSum")
        MCNom.SetTitle("")
        if not noSF:
            rootUp = TFile.Open(os.path.join(inDir+"_Up",dir,rootfile),"READ")
            rootDown = TFile.Open(os.path.join(inDir+"_Down",dir,rootfile),"READ")
            if not rootDown or not rootUp:
                print "*********Skipping "+rootfile+"*********"
                continue
            MCUp = rootUp.Get("MCSum")
            MCDown = rootDown.Get("MCSum")
            MCUp.SetTitle("")
            MCDown.SetTitle("")

        c = TCanvas("main",rootfile,1200,1200)
        c.SetCanvasSize(1200,1200)

        upperCanvas = TPad("up","up",0,0.20,1,1)
        upperCanvas.SetBottomMargin(0.03)
        upperCanvas.SetTopMargin(0.06)
        upperCanvas.SetLogy(isLog)
        upperCanvas.Draw()
        upperCanvas.cd()

        TGaxis.SetMaxDigits(4)


        if not noSF:
            MCUp.SetFillColor(kWhite)
            MCUp.SetLineColor(kGreen)
            MCUp.SetLineWidth(4)
            MCDown.SetFillColor(kWhite)
            MCDown.SetLineColor(kBlue)
            MCDown.SetLineWidth(4)
            MCUp.Draw("hist")
            MCUp.GetYaxis().SetTitle("Events")
            MCDown.Draw("hist same")
            MCNom.SetLineColor(kMagenta)
        else:
            MCNom.SetLineColor(kBlack)
        MCNom.SetFillColor(kWhite)
        MCNom.SetLineWidth(4)
        MCNom.Draw("hist same")

        MCNom.GetYaxis().SetLabelSize(0.03)
        MCNom.GetYaxis().SetTitle("Events")

        legTopMargin = 0.90
        legend = TLegend(0.15, 0.8, 0.89, legTopMargin,"")
        legend.SetFillStyle(0)
        legend.SetTextSize(0.03)
        legend.SetNColumns(2)

        if not noSF:
            legend.AddEntry(MCNom,r"MC with SF_{central}","L")
            legend.AddEntry(MCUp,r"MC with SF_{up}","L")
            legend.AddEntry(MCDown,r"MC with SF_{down}","L")
        else:
            legend.AddEntry(MCNom,r"MC - No SF","L")

        legend.Draw()

        Data=rootNom.Get("Data")
        Data.Draw("same p e")
        legend.AddEntry(Data,"Data","PL")
        if noSF:
            maxY = max(Data.GetMaximum(),MCNom.GetMaximum())
        else:
            maxY = max(Data.GetMaximum(),MCUp.GetMaximum())
        if not isLog:
            MCNom.SetMinimum(1e-3)
            MCNom.SetMaximum(maxY*1.3)
            if not noSF:
                MCUp.SetMinimum(1e-3)
                MCUp.SetMaximum(maxY*1.3)
                MCDown.SetMinimum(1e-3)
                MCDown.SetMaximum(maxY*1.3)
        else:
            MCNom.SetMinimum(11)
            MCNom.SetMaximum(maxY*8)

        c.cd()
        lowerCanvas = TPad("down","down",0,0,1,0.22)
        lowerCanvas.Draw()
        lowerCanvas.cd()
        lowerCanvas.SetTicky(1)
        lowerCanvas.SetLeftMargin(0.1)
        lowerCanvas.SetRightMargin(0.1)
        lowerCanvas.SetTopMargin(0.0)
        lowerCanvas.SetBottomMargin(0.32)
        lowerCanvas.SetFrameFillStyle(0)
        lowerCanvas.SetFrameBorderMode(0)
        lowerCanvas.SetGridy()


        histoRatioNom = Data.Clone()
        histoRatioNom.Divide(MCNom)
        if not noSF:
            histoRatioNom.SetMarkerColor(kMagenta)
            histoRatioNom.SetMarkerSize(1)
            histoRatioUp = Data.Clone()
            histoRatioUp.Divide(MCUp)
            histoRatioUp.SetMarkerColor(kGreen)
            histoRatioUp.SetMarkerSize(1)
            histoRatioDown = Data.Clone()
            histoRatioDown.Divide(MCDown)
            histoRatioDown.SetMarkerColor(kBlue)
            histoRatioDown.SetMarkerSize(1)

        if not noSF:
            histoRatioNom.SetLineColor(kMagenta)
            histoRatioUp.SetLineColor(kGreen)
            histoRatioDown.SetLineColor(kBlue)
        else:
            histoRatioNom.SetLineColor(kBlack)


        histoRatioNom.GetYaxis().SetTitle("Data/MC")
        histoRatioNom.GetYaxis().SetTitleSize(0.11)
        histoRatioNom.GetYaxis().SetTitleOffset(0.4)
        histoRatioNom.GetYaxis().SetTitleFont(42)
        histoRatioNom.GetYaxis().SetLabelSize(0.08)
        histoRatioNom.GetYaxis().CenterTitle()
        histoRatioNom.GetYaxis().SetLabelFont(42)

        if "CvsL" in rootfile:
            xname = "Jet CvsL"
        elif "CvsB" in rootfile:
            xname = "Jet CvsB"
        else:
            xname=""

        histoRatioNom.GetXaxis().SetTitle(xname)
        histoRatioNom.GetXaxis().SetLabelSize(0.1)
        histoRatioNom.GetXaxis().SetTitleSize(0.12)
        histoRatioNom.GetXaxis().SetTitleOffset(1)
        histoRatioNom.GetXaxis().SetTitleFont(42)
        histoRatioNom.GetXaxis().SetTickLength(0.07)
        histoRatioNom.GetXaxis().SetLabelFont(42)
        histoRatioNom.SetTitle("")

        def removeErrors(hist):
            for i in range(1,hist.GetNbinsX()+1):
                hist.SetBinError(i,1e-2)
            return hist

        histoRatioNom=removeErrors(histoRatioNom)
        histoRatioNom.SetLineWidth(2)
        histoRatioNom.Draw("p e L")
        if not noSF:
            histoRatioUp=removeErrors(histoRatioUp)
            histoRatioUp.SetLineWidth(2)
            histoRatioDown=removeErrors(histoRatioDown)
            histoRatioDown.SetLineWidth(2)
            histoRatioUp.Draw("p e same")
            histoRatioDown.Draw("p e same")
        histoRatioNom.SetMaximum(1.49)
        histoRatioNom.SetMinimum(0.51)

        hLine = TLine(-0.2,1,1,1)
        hLine.SetLineColor(kRed)
        hLine.Draw()


        start,end = -0.2,1
        MCNomCount = MCNom.Integral()
        DataCount = Data.Integral()
        MCNormFactor = DataCount/MCNomCount

        hLineNom = TLine(start,MCNormFactor,end,MCNormFactor)
        hLineNom.SetLineStyle(9)
        hLineNom.SetLineWidth(2)

        texRatioNom = TText(1.01,MCNormFactor-0.03,"%.2f"%MCNormFactor)
        texRatioNom.SetTextSize(0.08)

        if noSF:
            hLineNom.SetLineColor(kBlack)
            hLineNom.Draw()

            texRatioNom.SetTextColor(kBlack)
            texRatioNom.Draw("same")
        else:
            hLineNom.SetLineColor(kMagenta)
            hLineNom.Draw()

            texRatioNom.SetTextColor(kMagenta)
            texRatioNom.Draw("same")

            MCUpCount = MCUp.Integral()
            MCNormFactorUp = DataCount/MCUpCount
            hLineUp = TLine(start,MCNormFactorUp,end,MCNormFactorUp)
            hLineUp.SetLineStyle(9)
            hLineUp.SetLineWidth(2)
            hLineUp.SetLineColor(kGreen)
            hLineUp.Draw("same")

            texRatioUp = TText(1.01,MCNormFactorUp-0.03,"%.2f"%MCNormFactorUp)
            texRatioUp.SetTextSize(0.08)
            texRatioUp.SetTextColor(kGreen)
            texRatioUp.Draw("same")

            MCDownCount = MCDown.Integral()
            MCNormFactorDown = DataCount/MCDownCount
            hLineDown = TLine(start,MCNormFactorDown,end,MCNormFactorDown)
            hLineDown.SetLineStyle(9)
            hLineDown.SetLineWidth(2)
            hLineDown.SetLineColor(kBlue)
            hLineDown.Draw("same")

            texRatioDown = TText(1.01,MCNormFactorDown-0.03,"%.2f"%MCNormFactorDown)
            texRatioDown.SetTextSize(0.08)
            texRatioDown.SetTextColor(kBlue)
            texRatioDown.Draw("same")

            distname = getName(rootfile)
            SFNames[dir][xname.split()[-1]+"_"+distname]= (MCUpCount-MCDownCount)/MCNomCount


        # ----------------------------------------------------------

        # ======================== LaTeX ==========================
        texTL = TLatex()
        texTL.SetTextSize(0.036)

        texTR = TLatex()
        texTR.SetTextSize(0.032)
        texTR.SetTextAlign(31)

        upperCanvas.cd()
        texTL.DrawLatexNDC(0.13,0.91, "CMS #it{#bf{Preliminary}}")
        texTR.DrawLatexNDC(0.89,0.95, "#bf{"+str(35900/1000.)+" fb^{-1} (13 TeV)}")
        # ----------------------------------------------------------

        outdir=os.path.join(inDir+"_Unc",dir)
        os.system("mkdir -p "+outdir)
        c.SaveAs(outdir+"/"+rootfile.split(".root")[0]+".png")

tab=[]
headall=[]
for dirs,distdict in SFNames.iteritems():
    row=[dirs.split("_")[-1]]
    if row==["central"]: continue
    head=[]
    for distname,key in distdict.iteritems():
        row.append(key)
        head.append(distname)
    if headall==[]:
        headall=head[:]
    else:
        if head!=headall: print "WARNING: MISMATCH in", dirs
    tab.append(row)
print(tabulate(tab,headers=head))
