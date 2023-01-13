	export OUTPUTDIR=/nfs/dust/cms/user/spmondal/ctag_condor/220327_UL2017_$4/
	OUTPUTNAME=outTree.root

	CONDOR_CLUSTER_ID=$1
	CONDOR_PROCESS_ID=$2
	INPFILE=$3

        if  [[ $4 == "Wc" ]]; then
             PYFILE="WcSelection.py"
        elif  [[ $4 == "DY" ]]; then
             PYFILE="DYJetSelection.py"
        elif  [[ $4 == "TT" ]]; then
             PYFILE="TTbSelection.py"
	elif  [[ $4 == "TTNoMu" ]]; then
             PYFILE="TTbNoMuSelection.py"
        elif  [[ $4 == "WcNoMu" ]]; then
             PYFILE="WcNoMuSelection.py"
        fi
        
 
        #export PATH=/afs/desy.de/common/passwd:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:/cvmfs/grid.cern.ch/emi3ui-latest/bin:/cvmfs/grid.cern.ch/emi3ui-latest/sbin:/cvmfs/grid.cern.ch/emi3ui-latest/usr/bin:/cvmfs/grid.cern.ch/emi3ui-latest/usr/sbin:$PATH
        echo "arguments: " $1 $2 $3
        echo "username and group"
        id -n -u
        id -n -g

        echo "creating tempdir and copy"
        tmp_dir=$(mktemp -d)
        cp -r ../${PYFILE} ../nuSolutions.py ../scalefactors* ../getJEC.py ../processInput.py ../SkimNano.py x509up_user.pem $tmp_dir

        echo "setting up the environment"
        source /cvmfs/grid.cern.ch/centos7-umd4-ui-4_200423/etc/profile.d/setup-c7-ui-example.sh
        source /cvmfs/cms.cern.ch/common/crab-setup.sh
        source /cvmfs/cms.cern.ch/cmsset_default.sh
        cd /cvmfs/cms.cern.ch/slc7_amd64_gcc900/cms/cmssw/CMSSW_11_3_0_pre3/src
        eval "$(scramv1 runtime -sh)"
    
        echo "successfully set up the enviroment"

        echo "changing to tempdir"
        cd $tmp_dir
        pwd
        ls

        if [ -f "x509up_user.pem" ]; then
           export X509_USER_PROXY=x509up_user.pem
        fi
        voms-proxy-info

#        echo "setting up the environment"
#        source /cvmfs/cms.cern.ch/cmsset_default.sh
#        cd /cvmfs/cms.cern.ch/slc7_amd64_gcc900/cms/cmssw/CMSSW_11_3_0_pre3/src/
#        cmsenv
#        echo "echo PATH:"
#        echo $PATH

#        echo "changing to tempdir"
#        cd $tmp_dir
#        pwd
#        ls
#        if [ -f "x509up_user.pem" ]; then
#          export X509_USER_PROXY="$(pwd)"/x509up_user.pem 
#        fi
#        echo "Proxy info:"
#        voms-proxy-info
#        echo $X509_USER_PROXY

        #xrdcp root://xrootd-cms.infn.it//${INPFILE} ./infile.root
#        cp -v ${INPFILE} infile.root

        rng=4
        if [[ ${INPFILE} == *"Single"* ]]  || [[ ${INPFILE} == *"Double"* ]] || [[ ${INPFILE} == *"EGamma"* ]] || [[ ${INPFILE} == *"MuonEG"* ]]; then
             rng=2
        fi
        echo "will run "$rng" times."
        for (( JEC=0; JEC<=$rng; JEC++ ));   do
                echo "running python script"
                echo "running "$JEC"/"$rng" times."
                python ${PYFILE} ${INPFILE} ${JEC}
                rc=$?
                if [[ $rc == 99 ]]
                then
                    echo "Output file already exists." $rc
                    if [[ ${INPFILE} == *"Single"* ]]  || [[ ${INPFILE} == *"Double"* ]] || [[ ${INPFILE} == *"EGamma"* ]] || [[ ${INPFILE} == *"MuonEG"* ]]; then
                        break
                    fi
                    continue
                fi
                if [[ $rc != 0 ]]
                then
                    echo "got exit code from python code: " $rc
                    exit $rc
                fi
                echo "done running, now copying output to DUST"

                echo "copying output"
                SAMPNAME=$(bash dirName.sh)
                FLNAME=$(bash flName.sh)
                mkdir -p ${OUTPUTDIR}${SAMPNAME}
                until scp ${OUTPUTNAME} ${OUTPUTDIR}${SAMPNAME}"/outTree_"${FLNAME}".root"; do
                        echo "copying output failed. Retrying..."
                        sleep 60
                done
                echo "copied output successfully"
        done


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
