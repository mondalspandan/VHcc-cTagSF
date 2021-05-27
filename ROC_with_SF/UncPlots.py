import matplotlib
matplotlib.use('Agg')
import pickle, os, sys, mplhep as hep, numpy as np, pandas as pd, uproot
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
plt.style.use(hep.cms.style.ROOT)

#print sys.path
# with open('/net/scratch_cms3a/mondal/ROC_with_SF/nanott17_small_withm1.pkl', 'rb') as f:
#     df17 = pickle.load(f) 
df17 = pd.read_pickle('/net/scratch_cms3a/mondal/ROC_with_SF/nanott17_small_interp.pkl')
df17 = df17[ ((df17['Jet_puId'] >= 6) | (df17['Jet_pt'] > 50)  ) & (df17['Jet_pt'] > 20) & (df17['Jet_jetId'] >= 5) & (abs(df17['Jet_eta']) < 2.5)]

if sys.argv[1] == "1":
    log = False
    stat = False
    fine = False
else:
    log = True
    stat = True
    fine = True

asymm = False
verbose = False
secondyaxis = False
binvaltext = True

SFFile = "../ROC_with_SF/DeepCSV_ctagSF_MiniAOD94X_2017_pTincl_v3_2_interp.root"

order = ["SF Stat. Unc.","Lepton eff.","Pileup","JER","JES","Fact. scale","Renorm. scale","Parton Shower","Cross section","b fragment.","V+jet flav. comp.","Interpolation","DY+b XSec","DY+c XSec","W+c XSec"]
order.reverse()
groups = {
        "Lepton eff."   : "IDSF",
        "Renorm. scale" : "LHEScaleWeight_muR",
        "Fact. scale"   : "LHEScaleWeight_muF",
        "Parton Shower" : "PSWeight",
        "Pileup"        : "PUWeight",
        "Cross section" : "XSec",        
        "JER"           : "jer",
        "JES"           : "jes",
        "b fragment."   : "bFrag",
        "Interpolation" : "Interp"
    }

if fine:
    groups["DY+b XSec"] = "XSec_BRUnc_DYJets_b"
    groups["DY+c XSec"] = "XSec_BRUnc_DYJets_c"
    groups["W+c XSec"] = "XSec_BRUnc_WJets_c"
else:
    groups["V+jet flav. comp."] = "XSec_BRUnc"

for tagger in ['dCvB','dCvL','dfCvB','dfCvL']:
    if verbose: print tagger

    if tagger.startswith('df'):
        pref = "DeepCSVWt_"
        sffl = SFFile.replace("CSV","Jet")        
    else:
        pref = "DeepFlavWt_"
        sffl = SFFile

    SFroot = uproot.open(sffl)

    systs = [i for i in df17.columns if i.startswith(pref) and "central" not in i and "Stat" not in i]

    for truth in ['truthb','truthc','truthudsg']:
        if verbose: print "   ", truth
        thisdf = df17[df17[truth]==1]

        binwidth = 0.04
        if fine: binwidth = 0.02
        uncbins = np.arange(-0.2,1,binwidth)
        uncbinning = [(i,i+binwidth) for i in uncbins]

        binvals = {}
        poisunc = []
        for bins in uncbinning:
            if verbose: print "   "*2, bins
            # if bins[0] <=-0.1 and bins[1] > -0.1: 
            #     thisbin = thisdf[thisdf[tagger] < 0]
            #     print thisbin.head
            # else:
            thisbin = thisdf[(thisdf[tagger] > bins[0]) & (thisdf[tagger] < bins[1])]
            Variances = {}

            #central
            vals = thisbin[pref+"central"]
            uncs = thisbin[pref+"StatUp"]
            df = pd.DataFrame(data={'unc' : uncs, 'val': vals})
            group = df.groupby(['unc','val'])

            vallist = group['val'].sum()
            unclist = group['unc'].sum()            
            stat2 = np.sum(unclist**2)
            central = np.sum(vals)

            # if stat:            
            Variances["SF Stat. Unc."] = stat2
                # Variances["MC Poissonian Unc."] = central
            if central > 0: poisunc.append(1./central)
            else: poisunc.append(0)
            
            for group in groups:
                groupUp2 = 0.
                groupDown2 = 0.
                for syst in systs:
                    if groups[group] in syst:
                        if groups[group] == "XSec" and "XSec_BRUnc" in syst: continue
                        if bins[0] <=-0.1 and bins[1] > -0.1: 
                            fl = truth.replace("udsg","l")[-1]
                            systvar = SFroot["SF%s_hist_%s"%(fl,syst.lstrip(pref))].to_numpy(flow=True)
                            cent = SFroot["SF%s_hist"%(fl)].to_numpy(flow=True)
                            diff = systvar[0][0][0] - cent[0][0][0]
                            central = cent[0][0][0]
                        else:
                            diff = (np.sum(thisbin[syst]) - central)
                        if diff >= 0: groupUp2 += diff**2
                        else: groupDown2 += diff**2

                Variances[group] = max(groupUp2,groupDown2)
                if asymm: Variances[group] = abs(np.sqrt(groupUp2) - np.sqrt(groupDown2))/max(np.sqrt(groupUp2),np.sqrt(groupDown2))
                
            last = ""
            for i in sorted(Variances):
                if i not in binvals: binvals[i] = []
                if bins[0] <=-0.1 and bins[1] > -0.1:
                    binvals[i].append(Variances[i]/central**2)
                else:
                    binvals[i].append(np.where(central==0,0.,Variances[i]/central**2))
                if verbose: print "   "*3, i, np.where(central==0,0.,Variances[i]/central**2)
                last = i
        
        fig, ax = plt.subplots()

        labels = []
        hists = []
        bot = None
        legs = []
        
        for i in order:
            if i not in binvals: continue
            if i == "SF Stat. Unc.":
                if not stat: continue
            hists.append(binvals[i])
            labels.append(i)            
            # legs.append(ax.bar(uncbins+binwidth/2, binvals[i], binwidth, bottom=bot))
            if type(bot) == type(None): bot = np.array(binvals[i])
            else: bot += np.array(binvals[i])
            
        histsum = np.sqrt(np.sum(hists,axis=0))
        histstat = np.sqrt(binvals["SF Stat. Unc."])
        # if len(hists) > 11: col = sns.color_palette("Paired", len(hists))
        # else: col = sns.color_palette("Paired", 11)
        
        if len(hists) > 12: col = sns.color_palette("husl",len(hists)-12)
        else: col = []
        col += sns.color_palette("Paired", min(len(hists),12))        
        col.reverse()
        if not stat: poisunc = None
        hep.histplot(hists,list(uncbins)+[1],stack=True,histtype='fill',label=labels,color=col)

        errx = uncbins+binwidth/2
        erry = bot
        yerr = poisunc
        # ax.errorbar(errx,erry,yerr=yerr,fmt='.')

        if np.sum(bot[int(len(bot)/6):int(len(bot)*7/12)]) < np.sum(bot[int(len(bot)/5):])/2:
            loc = 'upper left'
        else:
            loc = 'upper right'

        ax.set_xlim((-0.2,1))        
        ax.set_xlabel(tagger.replace("df","DeepJet ").replace("d","DeepCSV ").replace("v","vs"))
        ax.set_ylabel(r"Relative variance, $\left( \frac {\sigma_{\mathrm{SF}} } {\mathrm{SF}}\right)^2$")
        if asymm:
            ax.set_ylabel(r"Asymmetry metric, $ \frac{||\sigma_{plus}|-|\sigma_{minus}||}{max(\sigma_{plus},\sigma_{minus})}$")

        flavlabel = truth.replace("truth","")+" jets"

        if loc == 'upper left':
            ax.text(0.96, 0.96, flavlabel, ha='right', va='top', transform=ax.transAxes)
        else:
            ax.text(0.04, 0.96, flavlabel, ha='left', va='top', transform=ax.transAxes)        

        # ax.legend(legs,labels) #,fontsize=15)
        if log:
            ax.set_yscale('log')
            if stat: ax.set_ylim(1e-6,max(bot)*100)        
            else: ax.set_ylim((1e-6,max(bot)*10))
            ax.legend(loc=loc,ncol=2,fontsize=20)
        else:
            ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0), useMathText=True)
            ax.set_ylim((0,max(bot)*1.2))            
            ax.legend(loc=loc)
            hep.yscale_legend()
            ax.set_ylim((0,ax.get_ylim()[1]*1.15))

        hep.r_align()

        rightcol = "grey"

        if secondyaxis:
            ax2 = ax.twinx()        
            ylim = ax.get_ylim()
            ax2.set_ylim(ylim[0], ylim[1])
            unclines = [0.01, 0.015, 0.02, 0.05, 0.1, 0.15, 0.2]
            secondary = [0.04,0.08]
            for i in [1,2]:
                uncsq = np.array(unclines)**2
                rightticks = [uncsq[0]]
                lastunc = rightticks[0]
                for unc2 in uncsq[1:]:
                    dist = (unc2 - lastunc)/(ylim[1]-ylim[0])
                    if unc2 > ylim[1]: break
                    if dist > 0.1:
                        rightticks.append(unc2)
                        lastunc = unc2
                if len(rightticks) > 3: break
                unclines.extend(secondary)
                unclines.sort()
                if ylim[1]>0.08**2: unclines.remove(0.04)

            
            rightticknames = np.sqrt(rightticks)
            ax2.set_yticks(rightticks, minor=False)
            ax2.set_yticks([], minor=True)
            ax2.set_yticklabels(rightticknames, minor=False)
            ax2.set_ylabel(r'Relative uncertainty, $\frac{\sigma_{\mathrm{SF}}}{\mathrm{SF}}$', rotation = 270, labelpad=38, horizontalalignment='left', y=1.0, color=rightcol)
            ax2.spines['right'].set_color(rightcol)
            ax2.tick_params(axis='y', colors=rightcol)
            # ax2.hlines(rightticks, -0.2, 1, color=rightcol, linestyles='dashed')

        if binvaltext:
            uncbinsclosed = list(uncbins)+[1]
            histsum2 = np.sum(hists,axis=0)
            for ibin, binval in enumerate(histsum2):
                if binval <= 0: continue
                binmid = uncbinsclosed[ibin] + (uncbinsclosed[ibin+1] - uncbinsclosed[ibin])*0.6
                ax.text(binmid, binval, ' %.1f%%'%(np.sqrt(binval)*100), ha='center', va='bottom',color=rightcol, fontsize=15, rotation=90)

        # hep.r_align()
        hep.cms.cmslabel(ax=ax,data=True,paper=True,rlabel=r"41.5 fb$^{-1}$ (13 TeV)")
        
        if secondyaxis: plt.subplots_adjust(left=0.13, right=0.85, top=0.9, bottom=0.1)

        

        pre = ""
        if not stat: pre+="nostat_"
        if fine: pre+="fine_"
        if asymm: outdir = "AsymmSystsPlots"
        else: outdir = "uncplots_v12"
        os.system("mkdir -p "+outdir)
        fig.savefig("%s/%s%s_%s.pdf"%(outdir,pre,tagger,truth))
        fig.savefig("%s/%s%s_%s.png"%(outdir,pre,tagger,truth))
        if not stat:
            pickle.dump(histsum,open("%s/%s%s_%s.pkl"%(outdir,pre,tagger,truth),'wb'))
            pickle.dump(histstat,open("%s/statonly_%s_%s.pkl"%(outdir,tagger,truth),'wb'))
        ax.cla()

            
            





