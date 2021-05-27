import matplotlib
matplotlib.use('Agg')
import pickle, os, sys, mplhep as hep, numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
import seaborn as sns
plt.style.use(hep.style.ROOT)
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

isPaper = True

def lighten_color(color, amount=0.5):
    """
    Lightens the given color by multiplying (1-luminosity) by the given amount.
    Input can be matplotlib color string, hex string, or RGB tuple.

    Examples:
    >> lighten_color('g', 0.3)
    >> lighten_color('#F034A3', 0.6)
    >> lighten_color((.3,.55,.1), 0.5)
    """
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2])

#print sys.path
with open('/net/scratch_cms3a/mondal/ROC_with_SF/nanott17_small.pkl', 'rb') as f:
    df17 = pickle.load(f)
df17 = df17[ ((df17['Jet_puId'] >= 6) | (df17['Jet_pt'] > 50)  ) & (df17['Jet_pt'] > 20) & (df17['Jet_jetId'] >= 5) & (abs(df17['Jet_eta']) < 2.5)]

def cut(tdf, ptlow=20, pthigh=2000, mlow = 20, mhigh = 220):
    cdf = tdf[(tdf.fj_pt < pthigh) & (tdf.fj_pt>ptlow) ]#&(tdf.fj_sdmass < mhigh) & (tdf.fj_sdmass>mlow)]
    return cdf

def roc3d(df, tag='d', w=None):   
    df = cut(df, ptlow=20, pthigh=2000)
    #print(df.keys())
    ar1,ar2,ar3 = [],[],[]
    cvb, cvl = [],[]
    dim = 40
    for i in np.linspace(0,1,dim+1):
        for j in np.linspace(0,1,dim+1):
            #print(j)
            # if tag=='d' and i == 0.2 and j == 0.4: 
            #     print(i,j,np.sum(tdf['truthudsg'])/np.sum(df['truthudsg']), np.sum(tdf['truthb'])/np.sum(df['truthb']), np.sum(tdf['truthc'])/np.sum(df['truthc']))
            tdf = df[(df[tag+'CvB'] > i) & (df[tag+'CvL']>j)]
            cvb.append(i)
            cvl.append(j)
            #print(i,j)
            if w is None:
                ar1.append(float(np.sum(tdf['truthudsg']))/np.sum(df['truthudsg']))
                ar2.append(float(np.sum(tdf['truthb']))/np.sum(df['truthb']))
                ar3.append(float(np.sum(tdf['truthc']))/np.sum(df['truthc']))
            else:
                ar1.append(float(np.sum(tdf['truthudsg'] * tdf[w]))/np.sum(df['truthudsg'] * df[w]))
                ar2.append(float(np.sum(tdf['truthb'] * tdf[w]))/np.sum(df['truthb'] * df[w]))
                ar3.append(float(np.sum(tdf['truthc'] * tdf[w]))/np.sum(df['truthc'] * df[w]))
    return (ar1, ar2, ar3, cvb, cvl)
#wtf(df16)
#ar1, ar2, ar3, cvb, cvl = roc3d(df16)
#print(np.array(ar1).reshape(6, 6))

roctup17d = roc3d(df17, tag='d')
roctup17df = roc3d(df17, tag='df')
roctup17dSF = roc3d(df17, tag='d', w='DeepCSVWt_central')
roctup17dfSF = roc3d(df17, tag='df', w='DeepFlavWt_central')

def find_nearest(array, value):
    A = np.asarray(array)
    idx = np.unravel_index(np.abs(A - value).argmin(), A.shape)
    print(array[idx])
    return idx

def find_nearest2D(A, B, a, b):
    A = np.asarray(A)
    B = np.asarray(B)
    cost = np.sqrt(np.abs(A - a)**2 + np.abs(B - b)**2)
    idx = np.unravel_index(cost.argmin(), A.shape)
    #print(A[idx], B[idx])
    return idx

def findeffs(ar1, ar2, ar3, cvb, cvl, cvbcut, cvlcut):
    dim = int(np.sqrt(len(ar1)))
    cvb = np.array(cvb).reshape(dim, dim)
    cvl = np.array(cvl).reshape(dim, dim)

    a1 = np.array(ar1).reshape(dim, dim)
    a2 = np.array(ar2).reshape(dim, dim)
    a3 = np.array(ar3).reshape(dim, dim)

    idx = find_nearest2D(cvb, cvl, cvbcut, cvlcut)
    
    print(a2[idx], a1[idx],  a3[idx])
    
def find3rd(tuple_in, b=None, l=None, c=None, cvb=None, cvl=None):
    dim = int(np.sqrt(len(tuple_in[0])))
    c_arr = np.array(tuple_in[-3]).reshape(dim, dim)
    b_arr = np.array(tuple_in[-4]).reshape(dim, dim)
    l_arr = np.array(tuple_in[0]).reshape(dim, dim)
    cvbar = np.array(tuple_in[-2]).reshape(dim, dim)
    cvlar = np.array(tuple_in[-1]).reshape(dim, dim)

    if b is not None and l is not None:
        idx = find_nearest2D(b_arr, l_arr, b, l)
    elif c is not None and l is not None:
        idx = find_nearest2D(c_arr, l_arr, c, l)
    elif b is not None and c is not None:
        idx = find_nearest2D(b_arr, c_arr, b, c)
    elif b is None and c is None and l is None and cvb is not None and cvl is not None:
        idx = find_nearest2D(cvbar, cvlar, cvb, cvl)
        
    return b_arr[idx], l_arr[idx], c_arr[idx], cvbar[idx], cvlar[idx]




def plotroc3d(tuples,
    colors = [],
    linestyles = [],
    labels = [],
    year="2017",
    annot="DeepCSV",
    paper=True,
    supp=False,
    wp=False,
    data=False,
    flname=""
    ):
    from mpl_toolkits.axes_grid1 import make_axes_locatable, Size
    
    f, ax = plt.subplots(1,figsize=(12,10))
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
        
    set_size(8,8, ax=ax)

    contourlist = []
    if len(tuples)>2: bins = [0.1,0.2,0.3,0.4,0.6,0.8]
    else: bins = np.linspace(0.1,0.8,8)
    for itup, tup in enumerate(tuples):
        ar1, ar2, ar3, cvb, cvl = tup
        dim = int(np.sqrt(len(ar1))-1)
        X = np.array(ar2).reshape(dim+1, dim+1) # b
        Y = np.array(ar1).reshape(dim+1, dim+1) # l
        Z = np.array(ar3).reshape(dim+1, dim+1) # c
        
        # cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["black","midnightblue", "steelblue", "cyan"])

        # cont = ax.contourf(X, Y, Z, 800, cmap=cmap, alpha=0, vmax=1, vmin=-0.3)
        # for c in cont.collections:
        #     c.set_edgecolor("face")

        #contours = ax.contour(X, Y, Z, [0.25, 0.3,0.5,0.7,0.8,0.9], colors='white')
        if len(tuples)>2:
            col = [lighten_color(colors[itup], i) for i in np.linspace(0.4,1.3,len(bins))]
        else:
            col=colors[itup]
        contourlist.append( ax.contour(X, Y, Z, bins, colors=col, linestyles=linestyles[itup], label = labels[itup], linewidths=3) )
    #ax.clabel(contours, contours.levels[:], inline=True, fontsize=16, fmt="%1.1f")



    #divider = make_axes_locatable(ax)
    #cax = divider.append_axes('right', size="7%", pad=0.1)
    cax = f.add_axes([ax.figure.subplotpars.right+0.01,
                      ax.figure.subplotpars.bottom,
                      0.05,
                      ax.figure.subplotpars.top-ax.figure.subplotpars.bottom])

    # cbar = f.colorbar(cont, cax=cax, orientation='vertical', ticks=np.linspace(0,1,6))
    cbar = f.colorbar(contourlist[0],cax=cax)
    # cbar.set_label('c jet efficiency', ha='right', y=1.0)
    cbar.remove()
    ax.set_xlabel("b jet mistag rate", ha='right', x=1.0)
    ax.set_ylabel("Light-flavour jet mistag rate", ha='right', y=1.0)
    ax.set_aspect('equal')
    #ax.set_yticklabels(["", 0.2,0.4,0.5,0.6,0.8,1.0])
    ax.set_yscale('log')
    ax.set_ylim(0.005,1)
    ax.set_xscale('log')
    ax.set_xlim(0.005,1)

    if wp is True:
        ha='center'; va = 'top'
        wpx, wpy = 0.15, 0.05
        ax.plot(wpx, wpy, color='white', marker='+', mew=4, ms=21, linewidth=0)#s=400, linewidths=20)
        ax.annotate(r"VH(H$\rightarrow$cc)"+"\nWorking Point", xy=(wpx, wpy), xytext=(0,-20), color="white", fontweight='bold', fontsize=20,
                                   textcoords="offset points", ha=ha, va=va, multialignment='center') 
    elif wp is not False:
        ha='center'; va = 'top'
        print(find3rd((ar1, ar2, ar3, cvb, cvl), cvb=wp[0], cvl=wp[1]))
        wpx, wpy = find3rd((ar1, ar2, ar3, cvb, cvl), cvb=wp[0], cvl=wp[1])[:2]
        ax.plot(wpx, wpy, color='white', marker='+', mew=4, ms=21, linewidth=0)#s=400, linewidths=20)
        ax.annotate(r"[{},{}]".format(round(wp[0],2), round(wp[1],2)) +"\nWorking Point", xy=(wpx, wpy), xytext=(0,-20), color="white", fontweight='bold', fontsize=20,
                                   textcoords="offset points", ha=ha, va=va, multialignment='center') 
        
    allpts = []
    def getmindist(allp,this):
        if allp == []: return 1
        allp = np.array(allp)
        return min( (allp[:,0]-this[0])**2+(allp[:,1]-this[1])**2 )
    # Define custom postions because default doesn't work for log
    for icon, contours in enumerate(contourlist):
        label_pos = []
        
        for col in contours.collections:
            pts = col.get_paths()[0].vertices
            # offset = 0
            # dist = round(float(len(pts))/4)
            # if len(contourlist) > 2:
            #     if icon < 2:
            #         ix = dist
            #     else:
            #         ix = 3*dist
            # else:
                # Want to label on the diagonal so fetch the minimum between x,y of the plotted contour path

            tomin = abs(pts[:,0]-pts[:,1])
            ix = list(tomin).index(min(tomin))
            newpt = (pts[ix][0], pts[ix][1])
            # while getmindist(allpts,newpt) < 1e-3 and ix < len(pts)-1:
            #     ix += 1
            #     newpt = (pts[ix][0], pts[ix][1])


            label_pos.append(newpt)
            allpts.append(newpt)
        ax.clabel(contours, contours.levels[:], inline=True, fontsize=14, fmt="%1.1f",  manual=label_pos)

    #ax.annotate(r"$\mathrm{t\bar{t}}$ events" + "\n"+"AK4Jets "+r"$\mathrm{p_T > 20}$GeV"+"\n"+annot ,
    #ax.annotate("AK4Jets"+"\n"+r"$\mathrm{p_T > }$20GeV"+"\n"+annot ,
    ax.annotate(annot ,
                xy=(0.05, 0.95), xycoords='axes fraction',  ha='left', va='top',
                bbox={'facecolor':'white', 'edgecolor':'white', 'alpha':0, 'pad':13}, annotation_clip=False)
    
    #if supp: cax.annotate("{} (13 TeV)".format(year), xy=(1.015, 1), xycoords='axes fraction',  ha='right', va='bottom',
    #            bbox={'facecolor':'white', 'edgecolor':'white', 'alpha':0, 'pad':13}, annotation_clip=False)

    ax.grid(which='minor', alpha=0.7, axis='both', linestyle='dotted', lw=1.3)
    ax.grid(which='major', alpha=0.9, linestyle='dotted', lw=2)
    
    handles, leglabels = [], []
    for icol, col in enumerate(colors):
        if labels[icol] == '': continue
        temppatch = mpatches.Patch(facecolor=col, label=labels[icol], edgecolor='black')
        handles.append(temppatch)
        leglabels.append(labels[icol])
    
    if '--' in linestyles:
        line_patch = Line2D([0], [0], color='grey', linewidth=3, linestyle='--')
        line_patch2 = Line2D([0], [0], color='black', linewidth=3, linestyle='-')
        handles.extend([line_patch,line_patch2])
        leglabels.extend(["MC only","With SF"])
    leg = ax.legend(handles, leglabels, borderpad=1, frameon=False, loc=2, fontsize=16, bbox_to_anchor=(-0.02,1.02)) #handlelength=1,
    legtitle = r"$\mathrm{t\bar{t}}$ jets $\mathrm{p_T >}$ 20 GeV" 
    if not any(['c-tagging' in i for i in labels]): legtitle+="\nc-tagging efficiency"
      #+ "\n "+str(int(round(mlow)))+" $\mathrm{<\ jet\ m_{sd}\ <}$ "+str(int(round(mhigh)))+" GeV"
    leg.set_title(legtitle, prop = {'size':18})
    leg.get_title().set_linespacing(1.5)
    leg._legend_box.align = "left"

    # if '--' in linestyles:
    #     line_patch = Line2D([0], [0], color='grey', linewidth=4, linestyle='--')
    #     line_patch2 = Line2D([0], [0], color='black', linewidth=1, linestyle='-')
    #     handles2 = [line_patch,line_patch2,]
    #     labels2 = ["MC only","With SF: Central"]            
    #     plt.gca().add_artist(leg)
    #     leg2 = ax.legend(handles2, labels2, loc='best', facecolor='white', framealpha=1, prop={'size': 18})
    
    if paper:
        if supp:
            ax = hep.cms.cmslabel(ax=ax, paper=True, year=year,data=data, supplementary=True)#, rlabel="")
        else:
            if data:
                ax = hep.cms.cmslabel(ax=ax, paper=isPaper,data=data,rlabel="41.5 fb$^{-1}$ (13 TeV)")
            else:
                ax = hep.cms.cmslabel(ax=ax, paper=isPaper,data=data)
    else:
        ax = hep.cms.cmslabel(ax=ax, paper=False, year=year,data=data)

    
    f.savefig("rocs3d/3droc{}-{}{}{}_{}.png".format(year, annot, "Paper" if paper else "", "WP" if wp!=False else "", flname ), dpi=300, bbox_inches='tight')
    f.savefig("rocs3d/3droc{}-{}{}{}_{}.pdf".format(year, annot, "Paper" if paper else "", "WP" if wp!=False else "", flname ), dpi=300, bbox_inches='tight', pad_inches=0.5)

for pap in [True]:
    plotroc3d([roctup17d,roctup17df],
        ['blue','red'],
        ['-','-'],
        ['DeepCSV','DeepJet'],
        year="2017",
        annot="",
        paper=pap,
        data=False,
        flname="MC"
        # wp=(0.2, 0.4) #cvb, cvl

        )

    # plotroc3d([roctup17d,roctup17df,roctup17dSF,roctup17dfSF],
    #     ['blue','red','blue','red'],
    #     ['--','--','-','-'],
    #     ['DeepCSV','DeepJet','',''],
    #     year="2017",
    #     annot="",
    #     paper=pap,
    #     data=True,
    #     flname="All"
    #     # wp=(0.2, 0.4) #cvb, cvl
    #     )

    plotroc3d([roctup17d,roctup17dSF],
        ['blue','blue'],
        ['--','-'],
        ['DeepCSV c-tagging eff',''],
        year="2017",
        annot="",
        paper=pap,
        data=True,
        flname="DeepCSV"
        # wp=(0.2, 0.4) #cvb, cvl
        )

    plotroc3d([roctup17df,roctup17dfSF],
        ['red','red'],
        ['--','-'],
        ['DeepJet c-tagging eff',''],
        year="2017",
        annot="",
        paper=pap,
        data=True,
        flname="DeepJet"
        # wp=(0.2, 0.4) #cvb, cvl
        )

    # plotroc3d([roctup17dSF,roctup17dfSF],
    #     ['blue','red'],
    #     ['-','-'],
    #     ['DeepCSV','DeepJet'],
    #     year="2017",
    #     annot="",
    #     paper=pap,
    #     data=True,
    #     flname="Data"
    #     # wp=(0.2, 0.4) #cvb, cvl

        # )
        
    break
