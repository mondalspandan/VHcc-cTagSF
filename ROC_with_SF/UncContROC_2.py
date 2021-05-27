import matplotlib
import pickle, os, sys, mplhep as hep, numpy as np, pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
plt.style.use(hep.cms.style.ROOT)

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

mod = False


# ax={}
# fig, ((ax[1], ax[2]), (ax[3], ax[4])) = plt.subplots(2,2)
# axind = 1
titles = ["DeepCSV CvsB","DeepCSV CvsL","DeepJet CvsB","DeepJet CvsL"]
valmatrix = []

fig,ax = plt.subplots()
for tagger in ['dCvB','dCvL','dfCvB','dfCvL']:
    with open('rocs/unccont_%s.pkl'%tagger, 'rb') as f:
        dct = pickle.load(f)
    contdct = {}
    for group in groups:
        cont = 0.
        for syst in dct:
            if groups[group] in syst:
                if mod:  cont += abs(dct[syst])
                else: cont += dct[syst]**2
        contdct[group] = cont
    
    labels = []
    vals = []
    for group in order:
        if group not in contdct: continue
        vals.append(contdct[group])
        labels.append(group)
    vals = np.array(vals)
    # vals = vals/np.sum(vals)*100
    print labels, vals
    valmatrix.append(vals)

valmatrix = np.array(valmatrix)
prev = np.zeros(len(valmatrix.T[0]))
col = sns.color_palette("Paired", 11)
col.reverse()
for ival,val in enumerate(valmatrix.T):
    ax.bar(titles,val,width=0.7,label = labels[ival], bottom=prev, color = col[ival])
    if prev.all() == 0: prev = val[:]
    else: prev += val

handles, labels = ax.get_legend_handles_labels()
ax.legend(handles[::-1], labels[::-1], loc="upper center",ncol=3,fontsize=17)
ax.ticklabel_format(style="sci",axis="y",scilimits=(0,0), useMathText=True)
if mod: ax.set_ylabel(r"$|\Delta\ AUC|$")
else: ax.set_ylabel(r"${(\Delta\ AUC)}^2$")
if mod: ax.set_ylim(0,6e-2)
else: ax.set_ylim(0,2.2e-4)
# hep.yscale_legend()

# ax.set_xticks(rotation=45)
ax.tick_params(axis='x', rotation=-20)
hep.cms.label(ax=ax,paper=True,data=True, rlabel="41.5 fb$^{-1}$ (13 TeV)")
hep.r_align()

fig.savefig("rocs/unc%s.png"%("_abs" if mod else ""))
fig.savefig("rocs/unc%s.pdf"%("_abs" if mod else ""))



