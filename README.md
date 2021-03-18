# VHcc - cTag SF
Repository for c-tagging scale factor measurement for the resolved VHcc Analysis
## Introduction
This repository utilizes post-processed NanoAOD tuples as input. The post-processing code is at https://github.com/vhbb/vhbb-nano.
The workflow for c-tag SF measurement is structued in the following sequence:
 -   Run Analyzer on post-processor output (three different analyzers for three selections)
 -   Run StackPlotter on Analyzer outputs
 -   Run SFExtractor on Plotter outputs

The outputs of the workflow are the scale factors for three components (SFc, SFb and SFl), in a 2D plane of CvsL-CvsB, along with statistical and systemtic variations.
The last step (SF Extraction) is performed using iterative fit.

Instructions to run the code are explained as follows.

## I. Analyzer
There are three analyzers for three different selection:
1. W+c Selection (c enriched): `WcSelection.py`
2. TT->bb Dileptonic Selection (b enriched): `TTbSelection.py`
3. DY+light Selection (light enriched): `DYJetSelection.py`

The analyzers run on (post-processed) NanoAOD. The recommended way to run them is to use HTCondor. Condor scripts suited to run on the DESY BIRD cluster are included in the repository.

1. ```cd ./Analyzer/condorDESY```
2. ```python fileListMaker.py path-to-ntuple-directory```
The input directory is expected to contain one sub-directory for each process. This command creates a new directory, `filelists`, with several `process_name.txt` files, each of which contains path to one .root file per line. Divide these into three non-mutually-exclusive directories so that each contains all MC/data required for Wc/TT/DY selections. Example set of input files for each analyzer is included in inputs_* directories.
3. There are several *.sh condor scripts in the directory. `condor_runscript_common.sh` is the script to run the analyzer on all JEC variations. `condor_runscript_common_NoJEC.sh` is a similar script, sans JES/R variations (only JEC central values and hence are ~5x faster). `condor_runscript_common_splitJEC.sh` processes JES/R variations but does one variation per job, suitable when some of your `condor_runscript_common.sh` jobs failed due to limited time and you want to reprocess them with one JEC variation per job.
Create the corresponding submit file by running:
```python make_submit.py inputs_XX XX``` XX being Wc, TT or DY.
This creates new `submit.sub` and `cmdList.txt` files. `submit.sub` can be edited as per requirements, e.g., you might want to choose the executable (all/NoJEC).
**Tip:** Once you are an expert, you can repeat `make_submit.py` for all three selections and concatenate each of the `cmdList.txt` into a single file which contains command list for all three selections.
4. Make sure all the `condor_runscript_*.sh` files are executable by running `chmod +x *.sh`
5. Open all `condor_runscript_common*.sh` files and replace the first line with the desired output directory.
6. Initiate voms-proxy using `voms-proxy-init --voms cms --valid 168:00` if not initiated already. Submit condor jobs using:
```condor_submit submit.sub```
7. Job progress can be checked using `condor_q`. `resubmitHelper.py` can help you resubmit any failed jobs.
8. Repeat for other Analyzers. Make sure the output directory (first line of `condor_runscript_common*.sh`) is different for each Analyzer, or you use `$4` in the directory name to automatically make them unique.

## II. StackPlotter
This step produces flat histograms (1D or 2D) from trees that are produced in the previous step. This step takes the outputs of the Analyzer code as inputs. This code can be run locally or on HTCondor.

***For a batch production, move to section II C.***

### II A. `Stacker.py`
The main code is `StackPlotter/Stacker.py`. Details about the code are added in `StackPlotter/README.md`, but you can usually skip the details and call the script externally using steps IIB and IIC. Skip to IIC if you want to run on batch mode.

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
1. Open `systStackerv2_condor/systStacker_condor.py` to edit.
2. Edit outDir to the name of the output directory.
3. Edit WcPath, TTPath, DYPath to the corresponding directories of the Analyzer outputs.
4. Edit `systs` to indicate the required systematics (comment out JES/R if you selected the NoJEC versions of the Analyzers).
5. Edit `plotExtra`, `plotsysts`, `plotBinSlices`, `validateSFs` booleans depending on what you want to do. If you want bin slices for central values only, set `plotBinSlices` to `True`, and others to `False`. If you want systematic variations, set `plotsysts` to `True` as well.
6. Open `condor_runscript.sh` and set OUTPUTDIR to desired output path. Change OUTPUTNAME to match outDir set in step 2.
7. Make sure `condor_runscript.sh` is executable by running `chmod +x condor_runscript.sh`
8. Run `python systStackerv2_condor.py`. This creates a new file `cmdList.txt` containing all the Stacker commands to be executed.
9. Submit jobs for all the commands using `condor_submit submit.sub`.
10. Job progress can be checked using `condor_q`. `resubmitHelper.py` can help you resubmit any failed jobs.

## III. SF Extractor
This section calculates the c-tagging scale factors from the files produced by the StackPlotter.
**Tip:** The simplest way to avoid confusion between DeepCSV and DeepJet files is to make separate directories for each. You can make a copy of the output directory produced by the StackPlotter, then delete DeepJet from one copy using ```rm -f Dir1_DeepCSV/*/*DeepFlav*```, and then DeepCSV from the other using ```rm -f Dir2_DeepJet/*/*jet_Cvs*```.
1. ```cd SFExtractor```
2. ```python AdaptiveFit.py -r prep```. Add `--doDeepJet` flag to this and steps 2-5 if you are deriving SFs for DeepJet.
3. ```parallel python AdaptiveFit.py -i path/to/centraldir -r :::: rangelist.txt```
4. ```python AdaptiveFit.py -i path/to/centraldir -r comb```
5. For systematics, use: ```parallel python AdaptiveFit.py -i ::: path/to/alldirs* ::: -r :::: rangelist.txt``` followed by ```parallel python AdaptiveFit.py -r comb -i ::: path/to/alldirs*'```
6. Combine all systematics and derive final SFs using ```python GetUncertainties.py -i /path/to/parentdir```

The final output .root file along with .png files can be found in the `parentdir/*_central` sub-directory.
