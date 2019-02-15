	OUTPUTDIR=/nfs/dust/cms/user/spmondal/ctag_condor/190213_TT_pt20_2/
	OUTPUTNAME=outTree.root

	CONDOR_CLUSTER_ID=$1
	CONDOR_PROCESS_ID=$2
	INPFILE=$3

        export PATH=/afs/desy.de/common/passwd:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:/cvmfs/grid.cern.ch/emi3ui-latest/bin:/cvmfs/grid.cern.ch/emi3ui-latest/sbin:/cvmfs/grid.cern.ch/emi3ui-latest/usr/bin:/cvmfs/grid.cern.ch/emi3ui-latest/usr/sbin:$PATH
        echo "echo PATH:"
        echo $PATH
        echo "arguments: " $1 $2 $3
        echo "username and group"
        id -n -u
        id -n -g

        echo "creating tempdir and copy"
        tmp_dir=$(mktemp -d)
        cp -r ../TTbSelection.py ../nuSolutions.py ../scalefactors $tmp_dir

        echo "setting up the environment"
        cd /cvmfs/cms.cern.ch/slc6_amd64_gcc630/cms/cmssw/CMSSW_10_2_0_pre6/src
        source /cvmfs/cms.cern.ch/cmsset_default.sh
        eval `scramv1 runtime -sh`
        echo "echo PATH:"
        echo $PATH
        source /cvmfs/grid.cern.ch/etc/profile.d/setup-cvmfs-ui.sh

        echo "changing to tempdir"
        cd $tmp_dir
        pwd
        ls

        #xrdcp root://xrootd-cms.infn.it//${INPFILE} ./infile.root
        echo "running python script"
        python TTbSelection.py ${INPFILE}
        rc=$?
        if [[ $rc != 0 ]]
        then
            echo "got exit code from python code: " $rc
            exit $rc
        fi
        echo "done running, now copying output to DUST"

        echo "copying output"
	SAMPNAME=$(bash dirName.sh)
        mkdir -p ${OUTPUTDIR}${SAMPNAME}
	until cp -vf ${OUTPUTNAME} ${OUTPUTDIR}${SAMPNAME}"/outTree_"${CONDOR_PROCESS_ID}".root"; do
		echo "copying output failed. Retrying..."
		sleep 60
	done
	echo "copied output successfully"

#        python -c "import sys,ROOT; f=ROOT.TFile(''); sys.exit(int(f.IsZombie() and 99))"
#        rc=$?
#        if [[ $rc != 0 ]]
#        then
#            echo "copy failed (either bad output from cp or file is Zombie)"
#            exit $rc
#        fi

        echo "delete tmp dir"
        cd $TMP
        rm -r $tmp_dir

        echo "all done!"
