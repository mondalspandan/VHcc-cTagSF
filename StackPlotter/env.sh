        export ORIG_DIR=$PWD
        cd /cvmfs/cms-ib.cern.ch/week1/slc7_amd64_gcc820/cms/cmssw/CMSSW_11_1_ROOT620_X_2020-04-20-2300/src/
        source     /cvmfs/cms.cern.ch/cmsset_default.sh
        eval     `scramv1 runtime -sh`
        cd $ORIG_DIR
