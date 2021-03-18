from ROOT import *
from array import array

def plotSFs(hist,flname,vertical=False,UncUpHist="",UncDownHist="",noUnc=False, palette=104, textCol=kBlack, plotminus1=True, forceSymm=False): #palette 104 for symmetric
    c = TCanvas("c","c",1500,1500)
    c.cd()
    hist.Draw("colz0")
    taken = []
    text = TLatex()
    #gStyle.SetPalette(1)
    gStyle.SetPalette(palette)
    hist.SetContour(1000)

    hist.SetTitle(hist.GetTitle().replace("SF","").replace("l","udsg"))
    
    if UncUpHist=="" or forceSymm: symm = True
    else: symm = False
    
    for ix in range(1,hist.GetNbinsX()+1):
        for iy in range(1,hist.GetNbinsY()+1):
            if (ix,iy) in taken: continue
            thisblock = [(ix,iy)]
            seed = hist.GetBinContent(ix,iy)
            xend = ix
            
            for ix2 in range(ix+1,hist.GetNbinsX()+1):
                if noUnc:
                    errMatch = True
                else:
                    if symm: errMatch = hist.GetBinError(ix2,iy)==hist.GetBinError(ix,iy)
                    else: errMatch = UncUpHist.GetBinContent(ix2,iy)==UncUpHist.GetBinContent(ix,iy) and UncDownHist.GetBinContent(ix2,iy)==UncDownHist.GetBinContent(ix,iy)
                if hist.GetBinContent(ix2,iy) == seed and errMatch and (ix2,iy) not in taken:
                    thisblock.append((ix2,iy))
                    xend = ix2
                else:
                    break
                    
            reachedYEnd = False
            yend = iy
            
            for iy2 in range(iy+1,hist.GetNbinsY()+1):
                for ix3 in range(ix,xend+1):
                    if noUnc:
                        errMatch = True
                    else:
                        if symm: errMatch = hist.GetBinError(ix3,iy2)==hist.GetBinError(ix,iy)
                        else: errMatch = UncUpHist.GetBinContent(ix3,iy2)==UncUpHist.GetBinContent(ix,iy) and UncDownHist.GetBinContent(ix3,iy2)==UncDownHist.GetBinContent(ix,iy)
                    if not (hist.GetBinContent(ix3,iy2) == seed and errMatch and (ix3,iy2) not in taken):
                        reachedYEnd = True
                        break
                if reachedYEnd: break
                for ix3 in range(ix,xend+1): thisblock.append((ix3,iy2))
                yend = iy2
                
            taken.extend(thisblock)            
            xcent = (hist.GetXaxis().GetBinLowEdge(ix)+hist.GetXaxis().GetBinLowEdge(xend+1))/2
            ycent = (hist.GetYaxis().GetBinLowEdge(iy)+hist.GetYaxis().GetBinLowEdge(yend+1))/2
            
            xwidth = hist.GetXaxis().GetBinLowEdge(xend+1) - hist.GetXaxis().GetBinLowEdge(ix)
            ywidth = hist.GetYaxis().GetBinLowEdge(yend+1) - hist.GetYaxis().GetBinLowEdge(iy)
            
            text.SetTextAlign(22)
            if vertical: text.SetTextAngle(90)
            if ywidth >= 0.2: text.SetTextSize(.02)
            else: text.SetTextSize(.016)
            text.SetTextColor(textCol)
            
            #if seed == 1.: print ix, iy, xend, yend
            
            if noUnc:
                text.DrawLatex(xcent,ycent,"%4.3f"%(seed))
            else:
                if xwidth >= 0.03:
                    if symm: text.DrawLatex(xcent,ycent,"%4.3f #scale[.8]{#pm %4.3f}"%(seed,hist.GetBinError(ix,iy)))
                    else: text.DrawLatex(xcent,ycent,"%4.3f^{+%4.3f}_{-%4.3f}"%(seed,UncUpHist.GetBinContent(ix,iy),UncDownHist.GetBinContent(ix,iy)))
                else:
                    text.DrawLatex(xcent,ycent,"%4.3f"%(seed))
    
    if plotminus1:
        m1val = hist.GetBinContent(0,0)
        pal = list(TColor.GetPalette())
        m1col = pal[int(min(1.,max(0.,(m1val-hist.GetMinimum())/(hist.GetMaximum()-hist.GetMinimum())))*len(pal))]
        m1 = TBox(-.12,-.12,-.02,-.02)    
        m1.SetFillColor(m1col)
        m1.Draw("l same")
        
        if noUnc:
            text.DrawLatex(-.07,-.07,"%4.3f"%(m1val))
        else:
            if symm: text.DrawLatex(-.07,-.07,"%4.3f #scale[.8]{#pm %4.3f}"%(m1val,hist.GetBinError(0,0)))
            else: text.DrawLatex(-.07,-.07,"%4.3f^{+%4.3f}_{-%4.3f}"%(m1val,UncUpHist.GetBinContent(0,0),UncDownHist.GetBinContent(0,0)))
        
        
        text2 = TLatex()
        text2.SetTextSize(.03)
        text2.SetTextFont(42)
        text2.SetTextAlign(22)
        text2.DrawLatex(-.07,0,"-1")
        text2.DrawLatex(0,-.07,"-1")
        text2.SetTextColor(textCol)

    texTL = TLatex()
    texTL.SetTextSize(0.04)
    texTL.SetTextAlign(11)

    texTR = TLatex()
    texTR.SetTextSize(0.032)
    texTR.SetTextAlign(31)

    texTL.DrawLatexNDC(0.10,0.91, "CMS") #it{#bf{Simulation}}") # #it{#bf{Preliminary}}")
    #texTR.DrawLatexNDC(0.90,0.91, "#bf{41.54 fb^{-1} (13 TeV)}")
    c.SaveAs(flname) 
    c.SaveAs(flname.replace(".png",".pdf"))
