dir=Plots_PASv1
python plotFromROOT.py -i Plots_201207_validwithUnc/output_2017_central -o $dir/Before/ --prelim
python plotFromROOT.py -i Plots_201207_validwithUnc/output_2017_central_2017_pTincl_v3_2/ -o $dir/After/ -p --prelim
python plotFromROOT.py -i ../ValidationTools/data/Plots_210225_MuBiasTestSemiTcEnrNoBTagger/output_2017_central/ -o $dir/mubias_before/ --prelim
python plotFromROOT.py -i ../ValidationTools/data/Plots_210225_MuBiasTestSemiTcEnrNoBTagger/output_2017_central_2017_pTincl_v3_2/ -o $dir/mubias_after/ -p --prelim
python plotFromROOT.py -i Plots_201207_MuBiasTT_validwithUnc/output_2017_central -o $dir/mubiasTT_before/ --prelim
python plotFromROOT.py -i Plots_201207_MuBiasTT_validwithUnc/output_2017_central_2017_pTincl_v3_2/ -o $dir/mubiasTT_after/ -p --prelim
