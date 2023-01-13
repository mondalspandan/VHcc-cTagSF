	OUTPUTDIR=/nfs/dust/cms/user/spmondal/ctag_condor/systPlots/Plots_221013_thesis2018valid/
	OUTPUTNAME=output_2017

	CONDOR_CLUSTER_ID=$1
	CONDOR_PROCESS_ID=$2

        export PATH=/afs/desy.de/common/passwd:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:/cvmfs/grid.cern.ch/emi3ui-latest/bin:/cvmfs/grid.cern.ch/emi3ui-latest/sbin:/cvmfs/grid.cern.ch/emi3ui-latest/usr/bin:/cvmfs/grid.cern.ch/emi3ui-latest/usr/sbin:$PATH
        echo "echo PATH:"
        echo $PATH
        echo "arguments: " $1 $2 $3
        echo "username and group"
        id -n -u
        id -n -g

        echo "creating tempdir and copy"
        tmp_dir=$(mktemp -d)
        cp -r ../Stacker.py cmdList.txt ../Deep*.root ../samplesDict.py $tmp_dir

        echo "setting up the environment"
        cd /cvmfs/cms.cern.ch/slc7_amd64_gcc820/cms/cmssw/CMSSW_11_1_0_p3_ROOT618/src/
        source /afs/desy.de/user/s/spmondal/private/ctag/VHcc-cTagSF/Analyzer/condorDESY/cmsset_default.sh #source /cvmfs/cms.cern.ch/cmsset_default.sh
        eval `scramv1 runtime -sh`
        echo "echo PATH:"
        echo $PATH
        source /cvmfs/grid.cern.ch/etc/profile.d/setup-cvmfs-ui.sh

        echo "changing to tempdir"
        cd $tmp_dir
        pwd
        ls
        ulimit -s unlimited	
    	echo "running python script"
        python -c $'import Stacker; f=open("cmdList.txt","r"); ln=f.readlines(); thisline=ln['$2$'];\nfor cmd in thisline.split("NEWLINE"): exec(cmd)'
       	rc=$?
        if [[ $rc != 0 ]]
        then
            echo "got exit code from python code: " $rc
            exit $rc
        fi
      	echo "done running, now copying output to DUST"

        echo "copying output"
        mkdir -p ${OUTPUTDIR}
	until cp -vr ${OUTPUTNAME}* ${OUTPUTDIR}; do
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
    
