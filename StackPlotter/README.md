The main code of the StackPlotter step is `StackPlotter/Stacker.py`. It can be used by importing it in a new python script and running `Stacker.plotStack(<arguments>)`. A (non-exhaustive) list of supported arguments are as follows:
- **brName**: *string or list*
    - Name of the branch (of type float) of the tree that you want to plot, e.g., "met_Pt", *or*
    - List with name of the branch (of type vector<float>) as first element and index as second, e.g., ["jet_CvsL",0] plots CvsL value of jet with index 0, *or*
    - List with name of the branch (of type vector<float>) as first element and name of the index branch (of type float) as second, e.g., ["jet_CvsL","muJet_idx"] plots CvsL value of the jet at index "muJet_idx", which is a float branch in the tuple.
- **brLabel**: *string*
 
    X-axis label for the output plot.
- **nbins**: *integer*
- **start**: *integer*
- **end**: *integer*
- **selections**: *list*, optional

    List of variables on which you want to apply cuts. Each item of the list can be a string or a list itself, in the same format as **brNames**. E.g., [["M_RelIso",0],"Z_Mass"].
- **cuts**: *list*, optional

    List of the range of each allowed selection. Each element of the list is a list of the format [min,max], so that `min < selection < max` is selected. If the cut needs to be inverted (selection ∉ [min,max]), use [min,max,"somestring"]. E.g., [[0,0.05],[85,95,"invert"]]
- **dataset**: *string*, optional

    Select dataset to plot, e.g. "smu", "sele", "dmu", "deg" or "mue". Defined in lines 674-683 and 347-351. Leave empty to plot MC alone.
- **isLog**: *boolean*, optional, *False* by default
- **filePre**: *string*, optional

    Prefix for output .png/.root file.
- **MCWeightName**: *string*, optional

    Name of branch that stores the event weight. E.g., "eventWeight", "genWeight". Supports division: "eventWeight/PUweight", and multiplication: "eventWeight*MuIDSF_up".
- **DataWeightName**: *string*, optional
- **nminus1**: *boolean*, optional, *False* by default

    Removes the cut on the variable being plotted (**brName**) from the list of **selections**.
- **doCombine**: *boolean*, optional, *False* by default

    Used when you want to combine outputs from two channels.
- **brName2D**: *string*, optional

    Name of the branch to be plotted on the y-axis when plotting 2D. Same format as **brName**.
- **brLabel2**, **nbins2**, **start2**, **end2**: optional

    Same as **brLabel**, **nbins**, **start**, **end**, for the variable on y-axis.
- **finalHistList**, **histoDList**: optional

    Needed when using **doCombine**.
- **drawStyle**: *string*, optional

    Parameters for TH2->Draw() when using 2D plotting. Example: "colz text error"
- **varBin1**, **varBin2**: *list*, optional

    List in the form of histogram bins, used for variable binning, for x and y axis respectively. Overrides **start** and **end**.
- **makeROOT**: *boolean*, optional, *False* by default

    Output a .root file with each histogram of the stack along with a .png output.
- **noRatio**: *boolean*, optional, *False* by default

    Do not plot the Data/MC section. *True* by default is **dataset** is not provided.
- **yTitle**: *string*, optional

    Label of the y-axis for 1D plots, and z-axis for 2D plots.
- **outDir**: *string*, optional

    Overrides hardcoded output directory.
- **rootPath**: *string*, optional

    Overrides hardcoded `rootPath` (input directory).
- **pathSuff**: *string*, optional

    Adds a suffix to the end of the directory path of each process. Useful for JES/R systematics. E.g.: "_JERup"
- **useXSecUnc**: *string*, optional

    Shifts crosssection of a process by up or down. Allowed values: "XSec_W_up", "XSec_W_down", "XSec_DY_up", "XSec_DY_down", "XSec_TT_up", "XSec_TT_down", "XSec_ST_up", "XSec_ST_down", "XSec_VV_up", "XSec_VV_down".
- **MCStat**: *string*, optional

    Shifts all MC up or down by one sigma of statistical uncertainty. E.g. "MCStat_up", "MCStat_down"
- **dataStat**: *string*, optional

    Shifts up or down by one sigma of statistical uncertainty. E.g. "dataStat_up", "dataStat_down"