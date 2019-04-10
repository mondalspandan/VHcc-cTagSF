from ROOT import *
from PIL import Image
import os, sys
gROOT.SetBatch(1)
gStyle.SetOptStat(0)

indir = sys.argv[1]
outdir = indir+"/BinnedKinematicsOut/"
TGaxis.SetMaxDigits(3)

hor = 801
ver = 377
kins = ["jet_Pt"]

os.system("mkdir -p "+outdir)

rootfls = [i for i in os.listdir(indir) if i.endswith('.root')]

def getcbld(fl,rescaleMC=True):
    inp = TFile.Open(fl,'READ')
    hList = [i.GetName() for i in list(inp.GetListOfKeys())]
    h={}

    for ihist, hName in enumerate(hList):
        h[hName]=inp.Get(hName)

    c = h["Wplusc"].Clone()
    c.Add(h["Wpluscc"])

    b = h["Wplusb"].Clone()
    l = h["Wplusuds"].Clone()
    d = h["Data"].Clone()

    c.SetDirectory(0)
    b.SetDirectory(0)
    l.SetDirectory(0)
    d.SetDirectory(0)

    for ihist, hName in enumerate(hList):
        if hName.startswith("W"): continue
        if hName.endswith("c"):
            c.Add(h[hName])
        elif hName.endswith("b"):
            b.Add(h[hName])
        elif hName.endswith("uds"):
            l.Add(h[hName])
    inp.Close()
    c.SetFillColor(kCyan)
    b.SetFillColor(kMagenta-9)
    l.SetFillColor(kYellow+3)
    if rescaleMC:
        MCTot = c.Integral() + b.Integral() + l.Integral()
        if not MCTot==0:
            DataTot = d.Integral()
            c.Scale(DataTot/MCTot)
            b.Scale(DataTot/MCTot)
            l.Scale(DataTot/MCTot)
    return c,b,l,d

def combineChannels(flE,flM,fl3=[]):
    ce,be,le,de = getcbld(flE)
    cm,bm,lm,dm = getcbld(flM)
    ce.Add(cm)
    be.Add(bm)
    le.Add(lm)
    de.Add(dm)

    for fl in fl3:
        c3,b3,l3,d3 = getcbld(fl)
        ce.Add(c3)
        be.Add(b3)
        le.Add(l3)
        de.Add(d3)
    return ce, be, le, de

varBin1=[-0.2,0.0,0.2,0.4,0.6,0.8,1.0]
varBin2=[-0.2,0.0,0.2,0.4,0.6,0.8,1.0]

for i in range(len(varBin1)-1):
    for j in range(len(varBin2)-1):
        txt = "jet_CvsL_muJet_idx_"+str(varBin1[i])+"-"+str(varBin1[i+1])+"+jet_CvsB_muJet_idx_"+str(varBin2[j])+"-"+str(varBin2[j+1])
        txt2 = "jet_CvsL_0_"+str(varBin1[i])+"-"+str(varBin1[i+1])+"+jet_CvsB_0_"+str(varBin2[j])+"-"+str(varBin2[j+1])
        filesinbin = [k for k in rootfls if txt in k or txt2 in k]
        for kin in kins:
            kinfiles = [k for k in filesinbin if kin in k]
            for k in kinfiles: print k
#            print kinfiles
            for fl in kinfiles:
                fl = os.path.join(indir,fl)
                if 'is_E_' in fl and 'nJet_0-4' in fl:
                    WcEfile = fl
                elif 'is_M_' in fl and 'nJet_0-4' in fl:
                    WcMfile = fl
                elif 'is_E_' in fl and 'nJet_5-' in fl:
                    TTEfile = fl
                elif 'is_M_' in fl and 'nJet_5-' in fl:
                    TTMfile = fl
                elif 'is_ME_' in fl:
                    TTMEfile = fl
                elif 'is_MM_' in fl:
                    TTMMfile = fl
                elif 'is_EE_' in fl:
                    TTEEfile = fl
                else:
                    DYfile = fl

            cW,bW,lW,dW = combineChannels(WcEfile,WcMfile)
            cTT,bTT,lTT,dTT = combineChannels(TTEEfile,TTMMfile,[TTMEfile,TTEfile,TTMfile])
            cDY,bDY,lDY,dDY = getcbld(DYfile)

            c = TCanvas("","",hor,ver)
            c.Divide(3,1,0.001)

            Stacks =[]
            selNames = ["Wc","TTb","DYl"]
            for ic, hlist in enumerate([[cW,bW,lW,dW],[cTT,bTT,lTT,dTT],[cDY,bDY,lDY,dDY]]):
                chist = hlist[0].Clone()
                bhist = hlist[1].Clone()
                lhist = hlist[2].Clone()
                dhist = hlist[3].Clone()


                hStack = THStack("Stack",selNames[ic])
                hStack.Add(lhist.Clone())
                hStack.Add(bhist.Clone())
                hStack.Add(chist.Clone())

                dhist.SetMarkerColor(kBlack)
                dhist.SetMarkerStyle(20)
                dhist.SetMarkerSize(1)
                dhist.SetLineColor(1)

                histoErr=chist.Clone()
                histoErr.Add(bhist)
                histoErr.Add(lhist)
                histoErr.SetFillColor(kGray+3)
                histoErr.SetLineColor(kGray+3)
                histoErr.SetMarkerSize(0)
                histoErr.SetFillStyle(3013)

#                legend = ROOT.TLegend(0.15, 0.75, 0.25, .89,"")
#                legend.SetFillStyle(0)
#                legend.SetTextSize(0.03)

#                legend.AddEntry(chist,"c","f")
#                legend.AddEntry(bhist,"b","f")
#                legend.AddEntry(lhist,"l","f")
#                legend.AddEntry(dhist,"Data","PL")

                dMax = dhist.GetMaximum()
                hStack.SetMaximum(dMax*1.3)


                c.cd(ic+1)
                Stacks.append(hStack.Clone())
                Stacks[ic].Draw("hist")
                dhist.DrawCopy("same p e")
                histoErr.DrawCopy("same e2")
                Stacks[ic].GetXaxis().SetTitle(r"p_{T}^{jet}")
                Stacks[ic].GetXaxis().SetRangeUser(20.,100.)
                Stacks[ic].GetYaxis().SetLabelOffset(0.0001)
#                legend.Draw()
            c.SaveAs(outdir+"/"+kin+"_CvsL_"+str(i+1)+"_CvsB_"+str(j+1)+".png")

for kin in kins:
    imgs = [i for i in os.listdir(outdir) if i.startswith(kin) and i.endswith(".root")]
    result = Image.new("RGB", (hor*(len(varBin1)-2), ver*(len(varBin2)-2)))
    for i in range(1,len(varBin1)-1):
        for j in range(1,len(varBin2)-1):
            img = Image.open(outdir+"/"+kin+"_CvsL_"+str(i+1)+"_CvsB_"+str(j+1)+".png")
#            img.thumbnail((hor, ver), Image.ANTIALIAS)
            x = (i-1)*hor
            y = ((len(varBin2)-1)-j-1)*(ver-22)
            result.paste(img, (x, y))
    result.save(outdir+"/"+kin+"_grid.png")
