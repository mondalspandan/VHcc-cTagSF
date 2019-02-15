# VHcc - cTag SF
Repository for c-tagging scale factor measurement for the resolved VHcc Analysis
## Introduction
This repository utilizes post-processed NanoAOD tuples as input. The post-processing code is at https://github.com/vhbb/vhbb-nano.
The workflow for c-tag SF measurement is structued in the following sequence:
 -   Run Analyzer on post-processor output (three different analyzers for three selections)
 -   Run StackPlotter on Analyzer outputs
 -   Run SFExtractor on Plotter outputs

The outputs of the workflow are the scale factors for three components (SFc, SFb and SFl), in a 2D plane of CvsL-CvsB, along with statistical and systemtic variations.
The last step (SF Extraction) is performed using iterative fit and the code has been adapted from ttcc (by Seth Moortgat), https://github.com/smoortga/ttcc.

Instructions to run the code are explained as follows.

## I. Analyzer
There are three analyzers for three different selection:
1. W+c Selection (c enriched): `WcSelection.py`
2. TT->bb Dileptonic Selection (b enriched): `TTbSelection.py`
3. DY+light Selection (light enriched): `DYJetSelection.py`

The analyzers run on (post-processed) NanoAOD. The recommended way to run them is to use HTCondor. Condor scripts suited to run on the DESY BIRD cluster are included in the repository.

1. ```cd ./Analyzer/condorDESY```
2. ```python fileListMaker.py path-to-ntuple-directory```
The input directory is expected to contain one sub-directory for each process. This command creates a new directory, `filelists`, with several `process_name.txt` files, each of which contains path to one .root file per line. Necessary input files for each analyzer is included in inputs_XX directories.
3. There are several *.sh condor scripts in the directory. `condor_runscript_XX.sh` is the script to run the XX analyzer, where XX = Wc, TT or DY.
`condor_runscript_XX_NoJEC.sh` are similar scripts, sans JES/R variations (only JEC central values and hence are ~5x faster).
Create the corresponding submit file by running:
```python make_submit.py filelists condor_runscript_XX.sh```
This creates a new `submit.sub` file which can be edited as per requirements.
4. Open `condor_runscript_XX.sh` and replace the first line with the desired output directory.
5. Initiate voms-proxy using `voms-proxy-init --voms cms --valid 168:00` if not initiated already. Submit condor jobs using:
```condor_submit submit.sub```
6. Job progress can be checked using `condor_q`.
7. Repeat for other Analyzers. Make sure the output directory (first line of `condor_runscript_XX.sh`) is different for each Analyzer.

## II. StackPlotter
This step produces flat histograms (1D or 2D) from trees that are produced in the previous step. This step takes the outputs of the Analyzer code as inputs. This code can be run locally or on HTCondor.

***For a batch production, move to section II C.***

### II A. `Stacker.py`
The main code is `StackPlotter/Stacker.py`. It can be used by importing it in a new python script and running `Stacker.plotStack(<arguments>)`. A list of supported arguments are as follows:
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
    List of variable on which you want to apply cuts. Each item of the list can be a string or a list itself, in the same format as **brNames**. E.g., [["M_RelIso",0],"Z_Mass"].
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

### II B. Run locally
To run the stacker locally, one may use `runStacker.py`, which is a *hack-ish* way to submit multiple shell jobs parallelly.
1. Open runStacker.py to edit.
2. Edit WcPath, TTPath, DYPath to the corresponding directories of the Analyzer outputs.
3. Each line of the large string, `arguments`, is executed as `Stacker.plotStack(line)`. So edit the string to plot the variables you want, using the format explained in II A.
4. Open Stacker.py and change lines 17 to 28 as required. Remember to set `outDir`.
5. Run using `python runStacker.py`. This submits shell jobs if number of uncommented lines in argument > 1, or else runs interactively.
6. For shell jobs the progress of the jobs can be monitored using `tail -f stackerLogs/n.log` where n is the job number.

### II C. Run condor jobs for all systematics
All the required CvsL and CvsB plots along with all systematic variations are prepared automatically by `systStacker_condor`. Instructions for batch jobs are as follows:
1. Open `systStacker_condor/systStacker_condor.py` to edit.
2. Edit outDir to the name of the output directory.
3. Edit WcPath, TTPath, DYPath to the corresponding directories of the Analyzer outputs.
4. Edit `systs` to indicate the required systematics (comment out JES/R if you selected the NoJEC versions of the Analyzers).
5. Open `condor_runscript.sh` and set OUTPUTDIR to desired output path. Change OUTPUTNAME to match outDir set in step 2.
6. Run `python systStacker_condor.py`. This creates a new file `cmdList.txt` containing all the Stacker commands to be executed.
7. Submit jobs for all the commands using `condor_submit submit.sub`.
8. Job progress can be checked using `condor_q`.

## III. SF Extractor
This section calculates the c-tagging scale factors from the files produced by the StackPlotter.
1. ```cd SFExtractor```
2. ```python ExtractSFs.py --indir=path_to_OUTPUTDIR_set_in_Step_II_C_5```
    This step calculates the SFs individually for central and each systematic variation.
3. ```python DeriveSFUncertainties.py --indir=path_to_OUTPUTDIR_set_in_Step_II_C_5```
    This step compares the systematic variations to the central and calculates the total uncertainty in separate .png outputs in the /*_central directory.

The final output .root file along with .png files can be found in the /*_central sub-directory of the Plotter's condor output directory.
