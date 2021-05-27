import matplotlib
matplotlib.use('Agg')
import pickle, os, sys, mplhep as hep, numpy as np
from sklearn.metrics import roc_curve, auc
from scipy.interpolate import interp1d
#from cTagSFReader import *
import matplotlib.pyplot as plt
from myROC import roc_curve_with_stats
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from scipy.spatial import ConvexHull

compresspdf = True

#print sys.path
with open('/net/scratch_cms3a/mondal/ROC_with_SF/nanott17_small.pkl', 'rb') as f:
    df17 = pickle.load(f) 
df17 = df17[ ((df17['Jet_puId'] >= 6) | (df17['Jet_pt'] > 50)  ) & (df17['Jet_pt'] > 20) & (df17['Jet_jetId'] >= 5) & (abs(df17['Jet_eta']) < 2.5)]
# df17=df17[:2000000]

#with open('/nfs/dust/cms/user/spmondal/ROC_with_SF_2018/nanott18.pkl', 'rb') as f:
#    df18 = pickle.load(f)

#df18 = df18[(df18['Jet_puId'] > 0) & (df18['Jet_pt'] > 20) & (df18['Jet_jetId'] > 4)]
    
systs = ['EleIDSFDown', 'EleIDSFUp', 'LHEScaleWeight_muFDown', 'LHEScaleWeight_muFUp', 'LHEScaleWeight_muRDown', 'LHEScaleWeight_muRUp', 'MuIDSFDown', 'MuIDSFUp', 'PUWeightDown', 'PUWeightUp', 'XSec_DYJetsDown', 'XSec_DYJetsUp', 'XSec_STDown', 'XSec_STUp', 'XSec_WJetsDown', 'XSec_WJetsUp', 'XSec_ttbarDown', 'XSec_ttbarUp', 'jerDown', 'jerUp', 'jesTotalDown', 'jesTotalUp', 'PSWeightFSRDown', 'PSWeightFSRUp', 'PSWeightISRDown', 'PSWeightISRUp', 'bFragDown', 'bFragUp']

def adjust_lightness(color, amount=0.5):
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], max(0, min(1, amount * c[1])), c[2])

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

def roc_input(frame, signal=["HCC"], include = ["HCC", "Light", "gBB", "gCC", "HBB"], norm=False, tagger='fj_doubleb', applySF=False, doSysts=True):       
    # Bkg def - filter unwanted
    bkg = np.zeros(frame.shape[0])    
    for label in include:
        bkg = np.add(bkg,  frame['truth'+label].values )
    bkg = [bool(x) for x in bkg]
    tdf = frame[bkg] #tdf for temporary df   
    
    # Signal
    truth = np.zeros(tdf.shape[0])
    predict = np.zeros(tdf.shape[0])
    prednorm = np.zeros(tdf.shape[0])
    for label in signal:
        truth   += tdf['truth'+label].values
        predict += tdf['predict'+label].values
    for label in include:
        prednorm += tdf['predict'+label].values
    tag_vals = tdf[tagger].values
    
    weightSysts = []
    systNames = [] # For printing out
    weightStat = []
    if applySF:        
        if tagger in ['dCvB','dCvL']:
            weights = tdf['DeepCSVWt_central'].values
            if doSysts:
                for systSuff in systs:
                    weightSysts.append(tdf['DeepCSVWt_'+systSuff].values)
                    systNames.append(systSuff)
                weightStat = tdf['DeepCSVWt_StatUp'].values
        elif tagger in ['dfCvB','dfCvL']:
            weights = tdf['DeepFlavWt_central'].values
            if doSysts:
                for systSuff in systs:
                    weightSysts.append(tdf['DeepFlavWt_'+systSuff].values)
                    systNames.append(systSuff)
                weightStat = tdf['DeepFlavWt_StatUp'].values
        else:
            weights = np.ones(len(truth))
    else:
            weights = np.ones(len(truth))
        
    if norm == False:
        return truth, predict, tag_vals, weights, weightSysts, weightStat, systNames
    else:
        return truth, np.divide(predict, prednorm), tag_vals, weights
        
#def roc_curve_with_stats(truth, pred, sample_weight=[], weight_errs=[]):
#    if sample_weight == []: sample_weight = np.ones(pred.size)
#    if weight_errs == []: weight_errs = np.zeros(pred.size)
#    
#    trueindices = np.where(truth == 1)[0]
#    falseindices = np.where(truth == 0)[0]
#    
#    sigtotal = np.sum(np.take(sample_weight,trueindices))
#    bkgtotal = np.sum(np.take(sample_weight,falseindices))
#    
#    sigerr = np.sqrt(np.sum(np.take(weight_errs**2,trueindices)))
#    bkgerr = np.sqrt(np.sum(np.take(weight_errs**2,falseindices)))
#    
#    fprs, tprs, fpres, tpres = [], [], [], []
#    
##    looplist = sorted(list(set(pred)))
##    if looplist[0] != 0: looplist = [0.]+looplist
##    if looplist[-1] != 1: looplist.append(1.)
#    
#    for cut in np.arange(0,1,1e-2):
#        passindices = np.where(pred > cut)[0]        
#        
#        trueposind = np.in1d(passindices, trueindices)
#        falseposind = np.in1d(passindices, falseindices)
#        
#        tp = np.sum(np.take(sample_weight,trueposind))
#        fp = np.sum(np.take(sample_weight,falseposind))
#        tpr = tp/sigtotal
#        fpr = fp/bkgtotal
#        
#        tpe = np.sqrt(np.sum(np.take(weight_errs**2,trueposind)))
#        fpe = np.sqrt(np.sum(np.take(weight_errs**2,falseposind)))
#        
#        if tp == 0: tpre = 0.
#        else: tpre = tpr * np.sqrt(tpe**2/tp**2 + sigerr**2/sigtotal**2 - 2*tpe**2/(tp*sigtotal))
#        
#        if fp == 0: fpre = 0.
#        else: fpre = fpr * np.sqrt(fpe**2/fp**2 + bkgerr**2/bkgtotal**2 - 2*fpe**2/(fp*bkgtotal))
#        
#        fprs.append(fpr)
#        tprs.append(tpr)
#        fpres.append(fpre)
#        tpres.append(tpre)
#        
#    return fprs, tprs, fpres, tpres

fprlin = np.arange(0,1.001,.001)
tprlin = np.arange(0,1.001,.001)

def compare_rocs(dfs=[], names=[], sigs=[["Hcc"]], bkgs=[["Hbb"]], norm=False, pt=[300,2000],
                 tagger_names=None,
                 flip = None,
                 title=None, 
                 ignore = None, 
                 wps = None,
                 applySFs = None,
                 measure_wps = True,                 
                 plotSF = False,
                 supp=False,
                 paper=False,
                 flip_anot = None,
                 cutstrings = None,
                 customLeg = [],
                 plotname="", colors=[0,1], styles=['-','-'], year='2016', use_tagger=[False], log=True):
    c_list = ['darkorange', 'steelblue', 'firebrick', 'purple', 'orangered']
    f, ax = plt.subplots(figsize=(11, 10))
    #f, ax = plt.subplots()
    if tagger_names == None: tagger_names = ['fj_doubleb']*len(dfs)
    if ignore == None: ignore = [False]*len(dfs)
    if flip == None: flip = [False]*len(dfs)
    if wps == None: wps = [False]*len(dfs)
    if cutstrings == None: cutstrings = [""]*len(dfs)
    for frame, tagger, name, sig, bkg, col, sty, db_id, show_wps, skip, flip_this, applySF, cutstring in zip(dfs, tagger_names, names, sigs, bkgs, colors, styles, use_tagger*len(colors), wps, ignore, flip, applySFs, cutstrings):
        print "\n",tagger,name
        if skip: continue
        mlow = 40; mhigh = 200
        frame = frame[(frame['Jet_pt'] > pt[0]) & (frame['Jet_pt'] < pt[1])]
#        frame = cut(frame,  ptlow=pt[0] , pthigh =pt[1], mlow = mlow, mhigh = mhigh)
        if not cutstring == "": frame = frame[(frame['Jet_jetId'] > cutstring)]
        truth, predict, db, weights, weightSysts, weightStat, systNames =  roc_input(frame, signal=sig, include = sig+bkg, norm=norm, tagger=tagger, applySF=applySF, doSysts=applySF)
        if flip_this: predict = 1 - predict

        if not db_id:
            fpr, tpr, threshold = roc_curve(truth, predict, sample_weight=weights)            
        else:
            fpr, tpr, threshold = roc_curve(truth, db, sample_weight=weights)
            if applySF: fpr2, tpr2, fpre, tpre, threshold = roc_curve_with_stats(truth, db, sample_weight=weights, weight_err=weightStat)
            
        centralauc = auc(fpr,tpr)
        print centralauc 
        centralint = interp1d(tpr,fpr)
        fprlincent = centralint(tprlin)

        if compresspdf and applySF:
            
            tpreint = interp1d(tpr,tpre)
            fpreint = interp1d(fpr,fpre)
            
            fpr = fprlincent
            tpr = tprlin
            tpre = tpreint(tpr)
            fpre = fpreint(fpr)
        
        unccont = {}
        uncbins = np.arange(0,1,0.1)
        uncbinning = [(i,i+0.1) for i in uncbins]
        unccontbin = {}
        
        if applySF:
            negareastaty = 1.-auc(tpr,fpr+fpre)
            posareastaty = 1.-auc(tpr,fpr-fpre)
            
            posareastatx = auc(fpr,tpr+tpre)
            negareastatx = auc(fpr,tpr-tpre)
        
            unccont["Stat"] = max(max(centralauc-negareastaty,centralauc-negareastaty), max(posareastaty-centralauc,  posareastatx-centralauc))

            # ylineup = np.vstack([tpr,fpr+fpre]).T
            # ylinedown = np.vstack([tpr,fpr-fpre]).T
            # xlineright = np.vstack([tpr+tpre,fpr]).T
            # xlineleft = np.vstack([tpr-tpre,fpr]).T
            # hull = ConvexHull(np.concatenate([ylineup,ylinedown,xlineright,xlineleft]))

            # unccont["Stat"] = hull.area
            # print "Stat area:", hull.area

            unccontbin["Stat"] = {}
            '''
            for uncbin in uncbinning:
                ulow = uncbin[0]
                uhigh = uncbin[1]
                ih = np.where(threshold == find_nearest(threshold,ulow))[0][0]
                il = np.where(threshold == find_nearest(threshold,uhigh))[0][0]
                # print il,ih
                centralaucloc = auc(fpr[il:ih],tpr[il:ih])
                print centralaucloc

                negareastaty = 1.-auc(tpr[il:ih],fpr[il:ih]+fpre[il:ih])
                posareastaty = 1.-auc(tpr[il:ih],fpr[il:ih]-fpre[il:ih])
                
                posareastatx = auc(fpr[il:ih],tpr[il:ih]+tpre[il:ih])
                negareastatx = auc(fpr[il:ih],tpr[il:ih]-tpre[il:ih])
                unccontbin["Stat"][uncbin] = max(max(centralaucloc-negareastaty,centralaucloc-negareastaty) , max(posareastaty-centralaucloc,  posareastatx-centralaucloc))
            '''
        possysts2 = np.zeros(len(tpr))
        negsysts2 = np.zeros(len(tpr))
        
        possysts2x = np.zeros(len(tpr))
        negsysts2x = np.zeros(len(tpr))
        
        if applySF:
            exportuncs = {}
            # exportuncs["x-axis"] = threshold
            # exportuncs["central"] = tpr
            # exportuncs["Stat_up"] = tpr+tpre
            # exportuncs["Stat_down"] = tpr-tpre
        
        for iw, weight in enumerate(weightSysts):
            #print weight
            fprt, tprt, thresholdt = roc_curve(truth, db, sample_weight=weight)
            
            #for exporting
            # interf = interp1d(thresholdt, tprt)
            # newtprexp = interf(threshold)
            # exportuncs[systNames[iw]] = newtprexp
            #

            interf = interp1d(tprt, fprt)
            newfpr = interf(tpr)
            newfprlin = interf(tprlin)
            fprdiff = newfpr-fpr
            fprdiffpos = fprdiff.copy()
            fprdiffpos[fprdiffpos<0] = 0
            fprdiffneg = fprdiff.copy()
            fprdiffneg[fprdiffneg>=0] = 0
            
            possysts2 += fprdiffpos**2
            negsysts2 += fprdiffneg**2
            
            negareay = 1.-auc(tpr,fpr+fprdiffpos)
            posareay = 1.-auc(tpr,fpr+fprdiffneg)
            
            #print systNames[iw], np.sqrt(np.sum(fprdiffpos**2)), np.sqrt(np.sum(fprdiffneg**2))
            
            interf2 = interp1d(fprt, tprt)
            newtpr = interf2(fpr)
            tprdiff = newtpr-tpr
            tprdiffpos = tprdiff.copy()
            tprdiffpos[tprdiffpos<0] = 0
            tprdiffneg = tprdiff.copy()
            tprdiffneg[tprdiffneg>=0] = 0
            
            possysts2x += tprdiffpos**2
            negsysts2x += tprdiffneg**2
            
            posareax = auc(fpr,tpr+tprdiffpos)
            negareax = auc(fpr,tpr+tprdiffneg)

            # linecent = np.vstack([tpr,fpr]).T
            # linesyst = np.vstack([tprt,fprt]).T
            # hull = ConvexHull(np.concatenate([linecent,linesyst]))
            # print systNames[iw],"area:", hull.area
            
            # points = np.concatenate([linecent,linesyst])
            # plt.plot(points[:,0], points[:,1], 'o')
            # for simplex in hull.simplices:
            #     plt.plot(points[simplex, 0], points[simplex, 1], 'k-')
            # plt.savefig('test.png')
            # sys.exit()

            # unccont[systNames[iw]] = hull.area

            fprup = np.where(newfprlin > fprlincent, newfprlin, fprlincent)
            fprdown = np.where(newfprlin < fprlincent, newfprlin, fprlincent)
            unccont[systNames[iw]] = auc(tprlin,fprup) - auc(tprlin,fprdown)

            # unccont[systNames[iw]] = abs(auc(tpr,fpr) - auc(tprt,fprt))
            # print systNames[iw],auc(tpr,fpr) - auc(tprt,fprt)
            
            # unccont[systNames[iw]] = max(max(centralauc-negareax,centralauc-negareay), max(posareay-centralauc,  posareax-centralauc))
            '''
            unccontbin[systNames[iw]] = {}
            for uncbin in uncbinning:
                ulow = uncbin[0]
                uhigh = uncbin[1]
                ih = np.where(threshold == find_nearest(threshold,ulow))[0][0]
                il = np.where(threshold == find_nearest(threshold,uhigh))[0][0]
                centralaucloc = auc(fpr[il:ih],tpr[il:ih])

                negareay = 1.-auc(tpr[il:ih],fpr[il:ih]+fprdiffpos[il:ih])
                posareay = 1.-auc(tpr[il:ih],fpr[il:ih]+fprdiffneg[il:ih])
                
                posareax = auc(fpr[il:ih],tpr[il:ih]+tprdiffpos[il:ih])
                negareax = auc(fpr[il:ih],tpr[il:ih]+tprdiffneg[il:ih])
                unccontbin[systNames[iw]][uncbin] = max(max(centralaucloc-negareax,centralaucloc-negareay) , max(posareay-centralaucloc,  posareax-centralaucloc))
            '''
            #print systNames[iw], np.sqrt(np.sum(tprdiffpos**2)), np.sqrt(np.sum(tprdiffneg**2))
            
        #print "Total:", np.sqrt(np.sum(possysts2x)), np.sqrt(np.sum(negsysts2x))
        # for i in sorted(unccont):
        #     unccont[i] /= centralauc 
        totalcont = sum(unccont.values())
        for i in sorted(unccont):
            print i, unccont[i]/totalcont*100, '%'
        
        possysts = np.sqrt(possysts2)
        negsysts = np.sqrt(negsysts2)
        possystsx = np.sqrt(possysts2x)
        negsystsx = np.sqrt(negsysts2x)
            
        if type(col) == int: color_toplot = c_list[col]
        else: color_toplot = col
        #if not name.startswith("raw:"): lab = "DeepDouble{}, AUC = {:.1f}\%".format(name, auc(fpr,tpr)*100)
        #else: lab = "{}, AUC = {:.1f}\%".format(name[len('raw:'):], auc(fpr,tpr)*100)
        if not name.startswith("raw:"): lab = "DeepDouble{}".format(name)
        else: lab = "{}".format(name[len('raw:'):])
        
        
        if applySF:           
            
            # pickle.dump(exportuncs,open("rocs/exportUncs_%s.pkl"%tagger,'w'))
            # print "Dumped uncertainties."
            pickle.dump(unccont,open("rocs/unccont_%s.pkl"%tagger,'w'))
            print "Dumped uncertainties."
            
            #Syst only
            #ax.fill_between(tpr,fpr-negsysts,fpr+possysts,facecolor=adjust_lightness(color_toplot,1.4), interpolate=True)
            #ax.fill_betweenx(fpr,tpr-negsystsx,tpr+possystsx,facecolor=adjust_lightness(color_toplot,1.4), interpolate=True)
            
            #Stat+syst
            ytoterrpos = np.sqrt(possysts2 + fpre**2)
            ytoterrneg = np.sqrt(negsysts2 + fpre**2)
            xtoterrpos = np.sqrt(possysts2x + tpre**2)
            xtoterrneg = np.sqrt(negsysts2x + tpre**2)
            
            ax.fill_between(tpr,fpr-ytoterrneg,fpr+ytoterrpos,facecolor=adjust_lightness(color_toplot,1.7), interpolate=True, hatch='\\\\', alpha=0.3)
            ax.fill_betweenx(fpr,tpr-xtoterrneg,tpr+xtoterrpos,facecolor=adjust_lightness(color_toplot,1.7), interpolate=True, hatch='\\\\', alpha=0.3)
            
            #Stat only
            ax.fill_between(tpr,fpr-fpre,fpr+fpre,facecolor=adjust_lightness(color_toplot,1), interpolate=True)
            ax.fill_betweenx(fpr,tpr-tpre,tpr+tpre,facecolor=adjust_lightness(color_toplot,1), interpolate=True)
            
            #central
            ax.plot(tpr, fpr, lw=1, color="black")    
            #ax.plot(tpr2, fpr2, lw=4, label=lab, color=adjust_lightness(color_toplot,.6), linestyle=sty)
            
            
        else:
            ax.plot(tpr, fpr, lw=4, color=adjust_lightness(color_toplot,1), linestyle=sty)
        
        # Annot WPs
        if show_wps != False:
            effs = [];  cut_vals = []
            if measure_wps:
                if "DeepDoubleB" or "ZHbb" in lab: mts = [0.003,0.005, 0.01, 0.02, 0.05];  wp_ns = ['T2', 'T1', "M2", 'M1', "L"]
                elif "DeepDoubleCvL" or "ZHcc"  in lab: mts = [0.01, 0.02, 0.05, 0.1];  wp_ns = ['T', "M2", 'M1', "L"]
                elif "DeepDoubleCvB" in lab: mts = [0.012, 0.02, 0.05, 0.1];  wp_ns = ['T', "M", 'L', "UL2" "UL1"]
            else:     
                #if "CvL" in lab and "CSV" in lab: effs=[]; mts = [];  wp_ns = [r'VH(H $\rightarrow c\bar{c})$' +'\nWorking Point']; cut_vals = [0.4]
                #elif "CvB" in lab and "CSV" in lab: effs=[]; mts = [];  wp_ns = [r'VH(H $\rightarrow c\bar{c})$' +'\nWorking Point']; cut_vals = [0.2]
                if "CvL" in lab and "CSV" in lab: effs=[]; mts = [];  wp_ns = [r'CvL = 0.4']; cut_vals = [0.4]
                elif "CvB" in lab and "CSV" in lab: effs=[]; mts = [];  wp_ns = [r'CvB = 0.2']; cut_vals = [0.2]    
                elif "DeepDoubleB" in lab: effs = []; mts = []; wp_ns = ['L', 'M1', "M2", 'T1', "T2"]; cut_vals = [0.7,0.86, 0.89, 0.91, 0.92]
                elif "DeepDoubleCvL" in lab: effs = []; mts = []; wp_ns = ['L', 'M1', "M2", 'T']; cut_vals = [0.59,0.7, 0.79, 0.83]
                elif "ZHbb" in lab: effs = []; mts = []; wp_ns = ['L', 'M1', "M2", 'T1', "T2"]; cut_vals = [0.67,0.90, 0.95, 0.97, 0.98]
            if "double-b" in lab: effs = []; mts = [];  wp_ns = ['L', "M1", 'M2', "T"]; cut_vals = [0.3,0.6, 0.8, 0.9]    
            if len(mts) < 1: # Find effs/mts for cuts
                for cut_val in cut_vals : # % mistag rate
                    idx, val = find_nearest(threshold, cut_val)
                    mts.append(fpr[idx])
                    effs.append(tpr[idx])
            else: # Find cuts/effs for mts - measure WPs
                for wp in mts: 
                    idx, val = find_nearest(fpr, wp)
                    effs.append(tpr[idx])
                    cut_vals.append(threshold[idx])
            print(lab, "WPs:")
            print(np.round(cut_vals,3))
            print("MTs", np.round(mts,3))
            print("Effs", np.round(effs,3))
                    
            va = 'bottom'
            if show_wps == 'left': annot_offset = (-7, 0); ha='right'
            elif show_wps == 'right': annot_offset = (10, 0); ha='left'
            elif show_wps == 'top': annot_offset = (0, 7); ha='center'
            elif show_wps == 'bottom' or show_wps == 'bot': annot_offset = (0, -10); ha='center'; va = 'top'
            elif show_wps == 'bottom-right': annot_offset = (10, -10); ha='left'; va = 'top'
            elif show_wps == 'bottom-left': annot_offset = (30, -50); ha='right'; va = 'top'
            else: annot_offset = (-7, 7); ha='right'
            #if not plotSF: 
            if True:
                for wp_n, wp_x, wp_y in zip(wp_ns, effs, mts):
                    ax.annotate(wp_n, xy=(wp_x, wp_y), xytext=annot_offset, color=color_toplot, fontweight='bold',
                           textcoords="offset points", ha=ha, va=va) 
                ax.plot(effs, mts, color=color_toplot, marker='+', mew=5, ms=20, linewidth=0)#s=400, linewidths=20)
            
            if plotSF:
                if "double-b" in lab:
                    SFdf = pd.read_csv('/home/anovak/Work/PyCFIT/SF_DoubleB/DF_resRun{}_DoubleB.csv'.format(year), index_col=0).filter(like='pt350to2000', axis=0)
                elif "BvL" in lab:
                    SFdf = pd.read_csv('/home/anovak/Work/PyCFIT/SF_DoubleB/DF_resRun{}_DDBvL.csv'.format(year), index_col=0).filter(like='pt350to2000', axis=0)
                    effs = effs[::-1]
                    mts  = mts[::-1]
                elif "ZHbb" in lab:
                    SFdf = pd.read_csv('/home/anovak/Work/PyCFIT/SF_DoubleB/DF_resRun{}_DeepAK8ZHbb.csv'.format(year), index_col=0).filter(like='pt350to2000', axis=0)
                    effs = effs[::-1]
                    mts  = mts[::-1]
                vSF = SFdf['SF'].to_numpy()
                vSFup = SFdf['SF'].to_numpy()+SFdf['Combined up'].to_numpy()
                vSFdown = SFdf['SF'].to_numpy()-SFdf['Combined down'].to_numpy()
                # newx, xerrs
                corr = vSF*effs
                corrup = vSFup*effs - vSF*effs
                corrdown = vSF*effs - vSFdown*effs

#                 for wp_n, wp_x, wp_y in zip(wp_ns, corr, mts):
#                     ax.annotate(wp_n, xy=(wp_x, wp_y), xytext=annot_offset, color=color_toplot, fontweight='bold',
#                            textcoords="offset points", ha=ha, va=va)                    
                ax.errorbar(corr, mts, yerr=0, xerr=[corrup, corrdown], color=color_toplot, fmt='o', markerfacecolor='none',
                            markersize = 10, linewidth=3  )
    if plotSF:
        ax.plot([], [], color='grey', marker='o', markersize = 10, markerfacecolor='none', linewidth=3, label="Data/MC SF Adjusted")

        
    ax.set_xlim(0,1)
    ax.set_ylim(0.001,1)
    sigs = sorted(list(set([item for sublist in sigs for item in sublist])))
    bkgs = sorted(list(set([item for sublist in bkgs for item in sublist])))
    #print sigs
    #print bkgs
    if len(sigs) == 1 and len(sigs[0]) == 3 and sigs[0][0] in ["H", "Z", "g"]:
            xlab = '{} \\rightarrow {}'.format(sigs[0][0], sigs[0][-2]+'\\bar{'+sigs[0][-1]+'}') 
            ax.set_xlabel(r'Tagging efficiency ($\mathrm{}$)'.format('{'+xlab+'}'), ha='right', x=1.0)
    else: 
        xlab = ['{} \\rightarrow {}'.format(l[0], l[-2]+'\\bar{'+l[-1]+'}') if l[0][0] in ["H", "Z", "g"] else l for l in sigs ]
        ax.set_xlabel(r'Tagging efficiency ($\mathrm{}$)'.format("{"+", ".join(xlab)+"}"), ha='right', x=1.0)
    if len(bkgs) == 1 and len(bkgs[0]) == 3 and bkgs[0][0] in ["H", "Z", "g"]:
            ylab = '{} \\rightarrow {}'.format(bkgs[0][0], bkgs[0][-2]+'\\bar{'+bkgs[0][-1]+'}') 
            ax.set_ylabel(r'Mistagging rate ($\mathrm{}$)'.format('{'+ylab+'}'), ha='right', y=1.0)
    else:
        ylab = ['{} \\rightarrow {}'.format(l[0], l[-2]+'\\bar{'+l[-1]+'}') if l[0][0] in ["H", "Z"] else l for l in bkgs ]
        ax.set_ylabel(r'Mistagging rate ($\mathrm{}$)'.format("{"+" / ".join(ylab)+"}"), ha='right', y=1.0)
    import matplotlib.ticker as plticker
    ax.xaxis.set_major_locator(plticker.MultipleLocator(base=0.1))
    #ax.xaxis.set_minor_locator(plticker.MultipleLocator(base=0.02))
    #ax.yaxis.set_minor_locator(plticker.MultipleLocator(base=0.02))
    #ax.tick_params(direction='in', axis='both', which='major', labelsize=18, length=12)
    #ax.tick_params(direction='in', axis='both', which='minor' , length=6)
    #ax.xaxis.set_ticks_position('both')
    ax.yaxis.set_ticks_position('both')    
    ax.grid(which='minor', alpha=0.5, axis='y', linestyle='dotted')
    ax.grid(which='major', alpha=0.9, linestyle='dotted')
    
    
    #handles, labels = plt.gca().get_legend_handles_labels()
    handles, labels = [], []
    takencolors = []
    for name, col, applySF, cutstring in zip(names,colors,applySFs,cutstrings):
        if applySF or cutstring==5 or col in takencolors: continue
        temppatch = mpatches.Patch(facecolor=col, label=name, edgecolor='black')
        handles.append(temppatch)
        labels.append(name.lstrip("raw:"))
        takencolors.append(col)
    
    leg = ax.legend(handles, labels, borderpad=1, frameon=False, loc=2, fontsize=18) #handlelength=1,
    legtitle = r"$\mathrm{t\bar{t}}$ events" + "\n"+"AK4Jets "+r"$\mathrm{p_T >}$ "+str(int(round((pt[0]))))+" GeV" 
      #+ "\n "+str(int(round(mlow)))+" $\mathrm{<\ jet\ m_{sd}\ <}$ "+str(int(round(mhigh)))+" GeV"
    leg.set_title(legtitle, prop = {'size':22})
    leg.get_title().set_linespacing(1.5)
    leg._legend_box.align = "left"
    
    if True in applySFs:
        line_patch = Line2D([0], [0], color='grey', linewidth=4, linestyle='--')
        line_patch2 = Line2D([0], [0], color='black', linewidth=1, linestyle='-')
        grey_patch = mpatches.Patch(facecolor='grey', label='With SF: Stat Unc (68% CL)')
        lgrey_patch = mpatches.Patch(facecolor='lightgrey',  label='With SF: Syst Unc (68% CL)', edgecolor='black', hatch='\\\\')
        handles2 = [line_patch,line_patch2,grey_patch,lgrey_patch]
        labels2 = ["MC only","With SF: Central",'With SF: Stat Unc (68% CL)','With SF: Syst Unc (68% CL)']    
        
        plt.gca().add_artist(leg)
        leg2 = ax.legend(handles2, labels2, loc=4, prop={'size': 17})
    
    if len(customLeg) > 0:
         handles3 = []
         labels3 = []
	 for ileg in customLeg:
             line_patch = Line2D([0], [0], color='grey', linewidth=4, linestyle=ileg[0])
             handles3.append(line_patch)
             labels3.append(ileg[1])
         plt.gca().add_artist(leg)
         leg3 = ax.legend(handles3, labels3, loc=4, prop={'size': 17})

    if 5 in cutstrings:
        line_patch = Line2D([0], [0], color='black', linewidth=4, linestyle='--')
        line_patch2 = Line2D([0], [0], color='black', linewidth=4, linestyle=':')
        handles2 = [line_patch,line_patch2]
        labels2 = ["Jet ID Tight","Jet ID TightLepVeto"]    
        
        plt.gca().add_artist(leg)
        leg2 = ax.legend(handles2, labels2, loc=4, prop={'size': 20})
    
    
#     ax.annotate(r'{} (13 TeV)'.format(year), xy=(1, 1.015), xycoords='axes fraction', fontsize=22,  fontname='Helvetica', 
#                 ha='right', annotation_clip=False)
#     ax.annotate('$\mathbf{CMS}$', xy=(0.001, 1.015), xycoords='axes fraction', fontname='Helvetica', fontsize=28,
#                 ha='left', annotation_clip=False)
    import mplhep.cms as cms
    
    if paper:
        if supp:
            ax = cms.cmslabel(ax, year=year, paper=True, supplementary=True)    
        else:
            ax = cms.cmslabel(ax, year=year, paper=True)
    else:
        ax = cms.cmslabel(ax=ax, year=year, data=(sum(applySFs)>0), paper=True, lumi = 41.54 if (sum(applySFs)>0) else None) #41.54

    if title != None: ax.set_title(title)

    if log: 
        ax.semilogy()
        #for tick in ax.get_yticklabels():#+ax.get_xticklabels():
        #    tick.set_fontname("Fira Sans")
        
    print(ax.get_window_extent().transformed(f.dpi_scale_trans.inverted()).width)
    print(ax.get_window_extent().transformed(f.dpi_scale_trans.inverted()).height)
    def set_size(w,h, ax=None):
        """ w, h: width, height in inches """
        if not ax: ax=plt.gca()
        l = ax.figure.subplotpars.left
        r = ax.figure.subplotpars.right
        t = ax.figure.subplotpars.top
        b = ax.figure.subplotpars.bottom
        figw = float(w)/(r-l)
        figh = float(h)/(t-b)
        ax.figure.set_size_inches(figw, figh)

    set_size(8,8)
    print(ax.get_window_extent().transformed(f.dpi_scale_trans.inverted()).width)
    print(ax.get_window_extent().transformed(f.dpi_scale_trans.inverted()).height)
        
    if len(plotname) > 1:
        f.savefig(os.path.join(savedir, "ROCComparison_"+plotname+year+"pt{}-{}".format(pt[0], pt[1])+".pdf"), transparent=False)
        f.savefig(os.path.join(savedir, "ROCComparison_"+plotname+year+"pt{}-{}".format(pt[0], pt[1])+".png"), transparent=False, dpi=500)
    else:
        if norm: f.savefig(os.path.join(savedir, "ROCNormComparison_"+year+"_"+"+".join(names)+"pt{}-{}".format(pt[0], pt[1])+".pdf"), transparent=True)
        else: f.savefig(os.path.join(savedir, "ROCComparison_"+year+"_"+"+".join(names)+"pt{}-{}".format(pt[0], pt[1])+".pdf"), transparent=True)
        if norm: f.savefig(os.path.join(savedir, "ROCNormComparison_"+year+"_"+"+".join(names)+"pt{}-{}".format(pt[0], pt[1])+".png"), transparent=True)
        else: f.savefig(os.path.join(savedir, "ROCComparison_"+year+"_"+"+".join(names)+"pt{}-{}".format(pt[0], pt[1])+".png"), dpi=300 , transparent=True)
    #print(ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted()).width)
    #print(ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted()).height)
    print(ax.get_window_extent())
    plt.show()

savedir = 'rocs/'
os.system('mkdir -p %s'%savedir)
plt.style.use(hep.cms.style.ROOT)
import warnings
warnings.filterwarnings("ignore")
'''
compare_rocs(dfs=[df17, df17], 
        names=["raw:DeepCSV - CvsB","raw:DeepJet - CvsB"],
        tagger_names = ['dCvB', 'dfCvB',], #, 'dfCvB', 'dfCvL'],
        use_tagger = [True, True], #, True, True],
        ignore = [False, False], #, False, False],
        colors=['blue', 'red'],
        pt = [20, 2000],
        supp=False,
        styles=['-', '-'], 
        sigs=[["c"], ["c"]], 
        bkgs=[["b"], ["b"]],
        applySFs=[False, False],
        plotname="CvsB_MC", year="2017")

compare_rocs(dfs=[df17, df17], 
        names=["raw:DeepCSV - CvsL","raw:DeepJet - CvsL"],
        tagger_names = ['dCvL', 'dfCvL',], #, 'dfCvB', 'dfCvL'],
        use_tagger = [True, True], #, True, True],
        ignore = [False, False], #, False, False],
        colors=['blue', 'red'],
        pt = [20, 2000],
        supp=False,
        styles=['-', '-'], 
        sigs=[["c"], ["c"]], 
        bkgs=[["udsg"], ["udsg"]],
        applySFs=[False, False],
        plotname="CvsL_MC", year="2017")
'''


compare_rocs(dfs=[df17, df17, df17, df17], 
        names=["raw:DeepCSV - CvsB", "raw:DeepCSV - CvsB - SF applied", "raw:DeepJet - CvsB", "raw:DeepJet - CvsB - SF applied"],
        tagger_names = ['dCvB', 'dCvB', 'dfCvB', 'dfCvB'], #, 'dfCvB', 'dfCvL'],
        use_tagger = [True, True, True, True], #, True, True],
        ignore = [False, False, False, False], #, False, False],
        colors=['blue', 'blue', 'red' , 'red'],
        pt = [20, 2000],
        supp=True,
        styles=['--', '-', '--', '-'], 
        sigs=[["c"], ["c"], ["c"] , ["c"]], 
        bkgs=[["b"], ["b"], ["b"], ["b"]],
        applySFs=[False, True, False, True],
        plotname="CvsB_nolog", year="2017", log=False)
compare_rocs(dfs=[df17, df17, df17, df17], 
        names=["raw:DeepCSV - CvsL", "raw:DeepCSV - CvsL - SF applied", "raw:DeepJet - CvsL", "raw:DeepJet - CvsL - SF applied"],
        tagger_names = ['dCvL', 'dCvL', 'dfCvL', 'dfCvL'], #, 'dfCvB', 'dfCvL'],
        use_tagger = [True, True, True, True], #, True, True],
        ignore = [False, False, False, False], #, False, False],
        colors=['blue', 'blue', 'red' , 'red'],
        pt = [20, 2000],
        supp=True,
        styles=['--', '-', '--', '-'], 
        sigs=[["c"], ["c"], ["c"] , ["c"]], 
        bkgs=[["udsg"], ["udsg"], ["udsg"], ["udsg"]],
        applySFs=[False, True, False, True],
        plotname="CvsL_nolog", year="2017", log=False)
'''
compare_rocs(dfs=[df17, df17],
        names=["raw:DeepJet - CvsB", "raw:DeepJet - CvsB - SF applied"],
        tagger_names = ['dfCvB', 'dfCvB'], #, 'dfCvB', 'dfCvL'],
        use_tagger = [True, True], #, True, True],
        ignore = [False, False], #, False, False],
        colors=['red' , 'red'],
        pt = [20, 2000],
        supp=True,
        styles=['--', '-'],
        sigs=[["c"] , ["c"]],
        bkgs=[["b"], ["b"]],
        applySFs=[False, True],
        plotname="CvsB_DJ", year="2017")
compare_rocs(dfs=[ df17, df17],
        names=["raw:DeepJet - CvsL", "raw:DeepJet - CvsL - SF applied"],
        tagger_names = ['dfCvL', 'dfCvL'], #, 'dfCvB', 'dfCvL'],
        use_tagger = [True, True], #, True, True],
        ignore = [False, False], #, False, False],
        colors=['red' , 'red'],
        pt = [20, 2000],
        supp=True,
        styles=['--', '-'],
        sigs=[["c"] , ["c"]],
        bkgs=[["udsg"], ["udsg"]],
        applySFs=[False, True],
        plotname="CvsL_DJ", year="2017")

compare_rocs(dfs=[df17, df17, df18, df18],
        names=["raw:DeepCSV - CvsL (2017)", "raw:DeepCSV - CvsL (2018)", "raw:DeepJet - CvsL (2017)", "raw:DeepJet - CvsL (2018)"],
        tagger_names = ['dCvL', 'dCvL', 'dfCvL', 'dfCvL'], #, 'dfCvB', 'dfCvL'],
        use_tagger = [True, True, True, True], #, True, True],
        ignore = [False, False, False, False], #, False, False],
        colors=['blue', 'blue', 'red' , 'red'],
        pt = [20, 2000],
        supp=True,
        styles=['--', '-', '--', '-'],
        sigs=[["c"], ["c"], ["c"] , ["c"]],
        bkgs=[["udsg"], ["udsg"], ["udsg"], ["udsg"]],
        applySFs=[True, True, True, True],
        plotname="CvsL", year="2017,2018")


compare_rocs(dfs=[df17, df17, df17, df17], 
        names=["raw:DeepCSV - CvsL", "raw:DeepCSV - CvsL", "raw:DeepJet - CvsL", "raw:DeepJet - CvsL"],
        tagger_names = ['dCvL', 'dCvL', 'dfCvL', 'dfCvL'], #, 'dfCvB', 'dfCvL'],
        use_tagger = [True, True,  True, True], #, True, True],
        ignore = [False, False,  False, False], #, False, False],
        colors=['blue', 'darkblue',  'red', 'darkred'],
        pt = [20, 2000],
        supp=True,
        styles=['--', ':', '--', ':'], 
        sigs=[["c"], ["c"], ["c"], ["c"]], 
        bkgs=[["udsg"], ["udsg"], ["udsg"], ["udsg"]],
        applySFs=[False, False, False, False, False, False],
        cutstrings=[0, 5, 0, 5],
        plotname="CvsL", year="2017")

compare_rocs(dfs=[df17, df17, df17, df17], 
        names=["raw:DeepCSV - CvsB", "raw:DeepCSV - CvsB", "raw:DeepJet - CvsB", "raw:DeepJet - CvsB"],
        tagger_names = ['dCvB', 'dCvB', 'dfCvB', 'dfCvB'], #, 'dfCvB', 'dfCvL'],
        use_tagger = [True, True,  True, True], #, True, True],
        ignore = [False, False,  False, False], #, False, False],
        colors=['blue', 'darkblue',  'red', 'darkred'],
        pt = [20, 2000],
        supp=True,
        styles=['--', ':', '--', ':'], 
        sigs=[["c"], ["c"], ["c"], ["c"]], 
        bkgs=[["b"], ["b"], ["b"], ["b"]],
        applySFs=[False, False, False, False, False, False],
        cutstrings=[0, 5, 0, 5],
        plotname="CvsB", year="2017")'''

'''
compare_rocs(dfs=[df17, df17, df17, df17, df17],      
        names=["raw:DeepJet - CvsL", "raw:DeepJet - CvsUDS", "raw:DeepJet - CvsG", "raw:DeepJet - CvsL", "raw:DeepJet - CvsL"],
        tagger_names = ['dfCvL', 'dfCvUDS', 'dfCvG',"dfCvL",'dfCvL'], #, 'dfCvB', 'dfCvL'],
        use_tagger = [True, True, True, True, True], #, True, True],
        ignore = [False, True, True, False, False],
        colors=['green', 'red', 'blue', "green","green"],
        pt = [20, 2000],
        supp=True,
        styles=['-', '--', ':','--',':'],
        sigs=[["c"], ["c"], ["c"],["c"],["c"]],
        bkgs=[["udsg"], ["uds"], ["g"], ["uds"], ["g"]],
        applySFs=[False, False, False, False, False],
        plotname="CvsL_UDS_G", year="2017",
        customLeg=[['-',"Against udsg"],['--', "Against uds"],[":","Against g"]])

compare_rocs(dfs=[df17, df17],      
        names=["raw:DeepJet - UDSvsG", "raw:Quark-Gluon Likelihood"],
        tagger_names = ['dfUDSvG','Jet_qgl'], #, 'dfCvB', 'dfCvL'],
        use_tagger = [True, True], #, True, True],
        ignore = [False, False],
        colors=['red', 'blue'],
        pt = [20, 2000],
        supp=True,
        styles=['-', '-'],
        sigs=[["uds"], ["uds"]],
        bkgs=[["g"], ["g"]],
        applySFs=[False, False],
        plotname="UDSvG_PUID0_linear_", year="2017", log=False
        #customLeg=[['-',"Against udsg"],['--', "Against uds"],[":","Against g"]])
)
'''
                                 