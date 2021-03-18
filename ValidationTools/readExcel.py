import pandas as pd, ezodf, matplotlib.pyplot as plt, os

doc = ezodf.opendoc("SFscan.ods")
os.system("mkdir -p SFscanout")

print("Spreadsheet contains %d sheet(s)." % len(doc.sheets))
for sheet in doc.sheets:
    print("-"*40)
    print("   Sheet name : '%s'" % sheet.name)
    print("Size of Sheet : (rows=%d, cols=%d)" % (sheet.nrows(), sheet.ncols()) )

# convert the first sheet to a pandas.DataFrame
sheet = doc.sheets[0]
df_dict = {}
for i, row in enumerate(sheet.rows()):
    # row is a list of cells
    # assume the header is on the first row
    if i == 0:
        # columns as lists in a dictionary
        df_dict = {cell.value:[] for cell in row}
        # create index for the column headers
        col_index = {j:cell.value for j, cell in enumerate(row)}
        continue
    for j, cell in enumerate(row):
        # use header instead of column index
        df_dict[col_index[j]].append(cell.value)
# and convert to a DataFrame


df = pd.DataFrame(df_dict)

def form(inp):
    return inp.replace("max",r"$b_{max}$").replace("min",r"$b_{min}$").replace("err",r"$\epsilon_{max}$").replace("dist",r"Adaptive direction")


def plotScan(var1,var2,var3,var3val,var4="dist",var4val="CvsL"):
    colnames = ["CvsB_DYm","CvsB_TTme","CvsB_Wce",
                "CvsL_DYm","CvsL_TTme","CvsL_Wce"]
               

    for iplot in range(6):
        var1fact = 1.
        var2fact = 1.
        var3txt = var3val
        var4txt = var4val
        if "min" in var1 or "max" in var1: var1fact = 0.02
        if "min" in var2 or "max" in var2: var2fact = 0.02
        if "min" in var3 or "max" in var3: var3txt *= 0.02
        if "min" in var4 or "max" in var4: var4txt *= 0.02
        
        for icount, iv2 in enumerate(sorted(list(df[var2].unique()))):
            cols = [col for col in df.columns if col.startswith('Cvs')]
            df2 = df[df[var4]==var4val][df[var2]==iv2][df[var3]==var3val].sort_values(by=var1)
            if icount==0:        
    #            coltoplot = df2[cols].std().sort_values(ascending=False).head().index[iplot]
                coltoplot = colnames[iplot]
#            print df2[[var1,coltoplot]]
            plt.plot(df2[var1]*var1fact,df2[coltoplot],'o-',label=form("%s=%.2f"%(var2,iv2*var2fact)))
        #    
        plt.xlabel(form(var1))
        plt.ylabel(r"$\Delta s/s$ (%)")
        
        if "DY" in coltoplot:
            yrange = (-97,-70)
        elif "TT" in coltoplot:
            yrange = (-62,-49)
        elif "Wc" in coltoplot:
            yrange = (-60,-42)
        
        plt.ylim(yrange)
        plt.title(form("%s: %s = %s"%(coltoplot,var3,var3txt)))     #,var4,var4txt
        plt.legend()
        flname = "%s_%s_%s_%.2f_%s_%s.png"%(var1,var2,var3,var3txt,var4txt,coltoplot)
        plt.savefig("SFscanout/scan_"+flname)
        plt.cla()

plotScan("max","min","err",0.05)
plotScan("max","min","err",0.02)
#plotScan("max","min","err",0.15)

#plotScan("min","max","err",0.02)
#plotScan("min","max","err",0.15)

plotScan("err","min","max",5)
#plotScan("err","min","max",15)
