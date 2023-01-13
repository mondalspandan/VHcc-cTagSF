from ROOT import TFile,array,std,TLorentzVector,TH1F,TTree
from array import array

import glob, sys, time, os, sys
import numpy as np
import nuSolutions as nu
import types, math, json
import itertools
from getJEC import *
start_time = time.time()

from processInput import *

print "#########"*10
print "start_time : ",time.ctime()
print "processing on : ",fullName

oFile = TFile("outTree.root",'RECREATE')
oFile.cd()

# ====================== Declare leaf variables/vectors ========================
h_total = TH1F('h_total','h_total',2,0,2)
h_nEvent = TH1F('h_nEvent','h_nEvent',2,0,2)
h_postp = TH1F('h_postp','h_postp',2,0,2)

run              = array('d',[0])
lumiBlock        = array('d',[0])
event            = array('d',[0])
LHE_HT           = array('d',[0])
LHE_Njets        = array('d',[0])

eventWeight      = array('d',[0])
signWeight       = array('d',[0])
genWeight        = array('d',[0])
PUWeight         = array('d',[0])
EleIDSF          = array('d',[0])
MuIDSF           = array('d',[0])
# MuIsoSF          = array('d',[0])
eventWeightnoPU  = array('d',[0])
eventWeightUnsigned  = array('d',[0])

PUWeight_up         = array('d',[0])
PUWeight_down       = array('d',[0])
EleIDSF_up          = array('d',[0])
EleIDSF_down        = array('d',[0])
MuIDSF_up           = array('d',[0])
MuIDSF_down         = array('d',[0])
# MuIsoSF_up          = array('d',[0])
# MuIsoSF_down        = array('d',[0])
LHEScaleWeight_muR_up    = array('d',[0])
LHEScaleWeight_muR_down  = array('d',[0])
LHEScaleWeight_muF_up  = array('d',[0])
LHEScaleWeight_muF_down  = array('d',[0])

muTrig           = array('d',[0])
eleTrig          = array('d',[0])

E_Mass           = std.vector('double')()
E_Pt             = std.vector('double')()
E_Eta            = std.vector('double')()
E_Phi            = std.vector('double')()
E_Charge         = std.vector('double')()
E_RelIso         = std.vector('double')()
E_sip3d          = std.vector('double')()
E_ip3d           = std.vector('double')()
E_dxy            = std.vector('double')()
E_dz             = std.vector('double')()
hardE_Jet_PtRatio = array('d',[0])

M_Pt             = std.vector('double')()
M_Eta            = std.vector('double')()
M_Phi            = std.vector('double')()
M_Charge         = std.vector('double')()
M_RelIso         = std.vector('double')()
M_sip3d          = std.vector('double')()
M_ip3d           = std.vector('double')()
M_dxy            = std.vector('double')()
M_dz             = std.vector('double')()
hardMu_Jet_PtRatio = array('d',[0])

HT               = array('d',[0])
jet_Pt             = std.vector('double')()
jet_Eta            = std.vector('double')()
jet_Phi            = std.vector('double')()
jet_Mass           = std.vector('double')()
jet_CvsL           = std.vector('double')()
jet_CvsB           = std.vector('double')()
jet_DeepFlavCvsL   = std.vector('double')()
jet_DeepFlavCvsB   = std.vector('double')()
jet_qgl            = std.vector('double')()

jet_chEmEF         = std.vector('double')()
jet_jetId          = std.vector('double')()
jet_muonIdx1       = std.vector('double')()
jet_muEF           = std.vector('double')()
jet_muPtRatio      = std.vector('double')()
jet_nMuons         = std.vector('double')()
jet_lepFiltCustom  = std.vector('double')()

jet_btagCMVA       = std.vector('double')()
jet_btagCSVV2      = std.vector('double')()
jet_btagDeepB      = std.vector('double')()
jet_btagDeepC      = std.vector('double')()
jet_btagDeepFlavB  = std.vector('double')()

jetMu_Pt           = array('d',[0])
jetMu_iso          = array('d',[0])
jetMu_dz           = array('d',[0])
jetMu_dxy          = array('d',[0])
jetMu_sip3d        = array('d',[0])
muJet_idx          = array('d',[0])
dR_jet_jetMu       = array('d',[0])
dR_Z_jet           = array('d',[0])
dR_lep_jet_min      = array('d',[0])
nMuJet             = array('d',[0])
dPhi_muJet_MET     = array('d',[0])
min_dPhi_jet_MET   = array('d',[0])
jetMuPt_by_jetPt   = array('d',[0])
jetMu_PtRel        = array('d',[0])

leadCvsL_jetidx      = array('d',[0])
leadCvsB_jetidx      = array('d',[0])

QCDveto             = array('d',[0])

nPV                 = array('d',[0])
nPVGood             = array('d',[0])
nSV                 = array('d',[0])

if isMC:
    jet_hadronFlv      = std.vector('double')()
    jet_isHardLep      = std.vector('double')()
    
jet_nJet           = array('d',[0])
met_Pt             = array('d',[0])
met_signif         = array('d',[0])
is_E               = array('d',[0])
is_M               = array('d',[0])
# is_H_mass_CR       = array('d',[0])
# is_W_mass_CR       = array('d',[0])

Z_Mass           = array('d',[0])
Z_Pt             = array('d',[0])
Z_Eta            = array('d',[0])
Z_Phi            = array('d',[0])

Z_Mass_best      = array('d',[0])
dR_mu_mu_best    = array('d',[0])

W_Mass           = array('d',[0])
W_Pt             = array('d',[0])
W_Eta            = array('d',[0])
W_Phi            = array('d',[0])

W_Mass_nuSol     = array('d',[0])
W_Pt_nuSol       = array('d',[0])
W_Eta_nuSol      = array('d',[0])
W_Phi_nuSol      = array('d',[0])

numOf_cJet       = array('d',[0])
numOf_bJet       = array('d',[0])
numOf_lJet       = array('d',[0])
pt_Of_cJet       = std.vector('double')()
pt_Of_bJet       = std.vector('double')()
pt_Of_lJet       = std.vector('double')()
eta_Of_cJet       = std.vector('double')()
eta_Of_lJet       = std.vector('double')()
phi_Of_cJet       = std.vector('double')()
phi_Of_lJet       = std.vector('double')()
pt_CvsLJet1       = array('d',[0])
pt_CvsLJet2       = array('d',[0])
eta_CvsLJet1      = array('d',[0])
eta_CvsLJet2      = array('d',[0])
phi_CvsLJet1      = array('d',[0])
phi_CvsLJet2      = array('d',[0])
CvsL_CvsLJet1     = array('d',[0])
CvsL_CvsLJet2     = array('d',[0])
CvsB_CvsLJet1     = array('d',[0])
CvsB_CvsLJet2     = array('d',[0])
if isMC:
    hadronFlavour_CsvLJet1  = array('d',[0])
    hadronFlavour_CsvLJet2  = array('d',[0])
    is_ZtoCCorBB       = array('d',[0])
HIGGS_Pt         = array('d',[0])
HIGGS_FL         = array('d',[0])
HIGGS_CvsL_Mass  = array('d',[0])
HIGGS_CvsL_Pt    = array('d',[0])
HIGGS_CvsL_Eta   = array('d',[0])
HIGGS_CvsL_Phi   = array('d',[0])
HIGGS_CvsB       = array('d',[0])
HIGGS_CvsB_CvsL  = array('d',[0])
HIGGS_CvsB_CvsL2 = array('d',[0])

cc_HIGGS_Pt         = array('d',[0])
cc_HIGGS_FL         = array('d',[0])
cc_HIGGS_CvsL       = array('d',[0])
cc_HIGGS_CvsB       = array('d',[0])
cc_HIGGS_CvsB_CvsL  = array('d',[0])
cc_HIGGS_CvsB_CvsL2 = array('d',[0])

co_HIGGS_Pt         = array('d',[0])
co_HIGGS_FL         = array('d',[0])
co_HIGGS_CvsL       = array('d',[0])
co_HIGGS_CvsB       = array('d',[0])
co_HIGGS_CvsB_CvsL  = array('d',[0])
co_HIGGS_CvsB_CvsL2 = array('d',[0])

oo_HIGGS_Pt         = array('d',[0])
oo_HIGGS_FL         = array('d',[0])
oo_HIGGS_CvsL       = array('d',[0])
oo_HIGGS_CvsB       = array('d',[0])
oo_HIGGS_CvsB_CvsL  = array('d',[0])
oo_HIGGS_CvsB_CvsL2 = array('d',[0])

M_Mass              = std.vector('double')()
met_Phi             = array('d',[0])
eta_Of_bJet         = std.vector('double')()
phi_Of_bJet         = std.vector('double')()
Flag_W_jet          = array('d',[0])
solver_chi2         = array('d',[0])

########################## MVA VARIABLES ##########################
SoftActivityJetHT       = array('d',[0])
SoftActivityJetNjets2   = array('d',[0])
SoftActivityJetNjets5   = array('d',[0])
SoftActivityJetNjets10  = array('d',[0])

DPhi_VH             = array('d',[0])
DPhi_METlep         = array('d',[0])
W_Tmass             = array('d',[0])
top_Mass            = array('d',[0])
DR_cc               = array('d',[0])
lepDR_cc            = array('d',[0])
M_lep_c             = array('d',[0])
centrality          = array('d',[0])
avgCvsLpT           = array('d',[0])
FWmoment_1         = array('d',[0])
FWmoment_2         = array('d',[0])
FWmoment_3         = array('d',[0])
FWmoment_4         = array('d',[0])

###################################################################
# ==============================================================================

# =============================== Declare output branches =====================
outputTree = TTree("Events","Events")

outputTree.Branch('run'              ,run           ,'run/D'        )
outputTree.Branch('lumiBlock'        ,lumiBlock     ,'lumiBlock/D'  )
outputTree.Branch('event'            ,event         ,'event/D'      )
outputTree.Branch('LHE_HT'           ,LHE_HT        ,'LHE_HT/D'     )
outputTree.Branch('LHE_Njets'        ,LHE_Njets     ,'LHE_Njets/D'     )

outputTree.Branch('eventWeight'      ,eventWeight   ,'eventWeight/D'     )
outputTree.Branch('signWeight'       ,signWeight    ,'signWeight/D'     )
outputTree.Branch('genWeight'        ,genWeight     ,'genWeight/D'     )
outputTree.Branch('PUWeight'         ,PUWeight      ,'PUWeight/D'     )
outputTree.Branch('EleIDSF'          ,EleIDSF       ,'EleIDSF/D'     )
outputTree.Branch('MuIDSF'           ,MuIDSF        ,'MuIDSF/D'     )
# outputTree.Branch('MuIsoSF'           ,MuIsoSF        ,'MuIsoSF/D'     )
outputTree.Branch('eventWeightnoPU'  ,eventWeightnoPU   ,'eventWeightnoPU/D'     )
outputTree.Branch('eventWeightUnsigned'      ,eventWeightUnsigned   ,'eventWeightUnsigned/D'     )

outputTree.Branch('PUWeight_up'         ,PUWeight_up      ,'PUWeight_up/D'     )
outputTree.Branch('PUWeight_down'       ,PUWeight_down    ,'PUWeight_down/D'     )
outputTree.Branch('EleIDSF_up'          ,EleIDSF_up       ,'EleIDSF_up/D'     )
outputTree.Branch('EleIDSF_down'          ,EleIDSF_down       ,'EleIDSF_down/D'     )
outputTree.Branch('MuIDSF_up'           ,MuIDSF_up        ,'MuIDSF_up/D'     )
outputTree.Branch('MuIDSF_down'           ,MuIDSF_down        ,'MuIDSF_down/D'     )
# outputTree.Branch('MuIsoSF_up'           ,MuIsoSF_up        ,'MuIsoSF_up/D'     )
# outputTree.Branch('MuIsoSF_down'           ,MuIsoSF_down        ,'MuIsoSF_down/D'     )
LHEScaleWeight_muF_up  = array('d',[0])
outputTree.Branch('LHEScaleWeight_muR_up'           ,LHEScaleWeight_muR_up        ,'LHEScaleWeight_muR_up/D'     )
outputTree.Branch('LHEScaleWeight_muR_down'         ,LHEScaleWeight_muR_down      ,'LHEScaleWeight_muR_down/D'     )
# outputTree.Branch('LHEScaleWeight_muF_up'           ,LHEScaleWeight_muF_up        ,'LHEScaleWeight_muF_up/D'     )
outputTree.Branch('LHEScaleWeight_muF_down'         ,LHEScaleWeight_muF_down      ,'LHEScaleWeight_muF_down/D'     )
outputTree.Branch('LHEScaleWeight_muF_up'         ,LHEScaleWeight_muF_up      ,'LHEScaleWeight_muF_up/D'     )

outputTree.Branch('muTrig'           ,muTrig        ,'muTrig/D'          )
outputTree.Branch('eleTrig'          ,eleTrig       ,'eleTrig/D'         )

outputTree.Branch('E_Mass'           ,E_Mass        )
outputTree.Branch('E_Pt'             ,E_Pt          )
outputTree.Branch('E_Eta'            ,E_Eta         )
outputTree.Branch('E_Phi'            ,E_Phi         )
outputTree.Branch('E_Charge'         ,E_Charge      )
outputTree.Branch('E_RelIso'         ,E_RelIso      )
outputTree.Branch('E_dz'             ,E_dz      )
outputTree.Branch('E_dxy'            ,E_dxy      )
outputTree.Branch('E_sip3d'          ,E_sip3d      )
outputTree.Branch('E_ip3d'           ,E_ip3d      )
outputTree.Branch('hardE_Jet_PtRatio'         ,hardE_Jet_PtRatio      ,'hardE_Jet_PtRatio/D')

outputTree.Branch('M_Mass'           ,M_Mass        )
outputTree.Branch('M_Pt'             ,M_Pt          )
outputTree.Branch('M_Eta'            ,M_Eta         )
outputTree.Branch('M_Phi'            ,M_Phi         )
outputTree.Branch('M_Charge'         ,M_Charge      )
outputTree.Branch('M_RelIso'         ,M_RelIso      )
outputTree.Branch('M_dz'             ,M_dz      )
outputTree.Branch('M_dxy'            ,M_dxy      )
outputTree.Branch('M_sip3d'          ,M_sip3d      )
outputTree.Branch('M_ip3d'           ,M_ip3d      )
outputTree.Branch('hardMu_Jet_PtRatio'         ,hardMu_Jet_PtRatio      ,'hardMu_Jet_PtRatio/D')

outputTree.Branch('HT'               ,HT            ,'HT/D'     )
outputTree.Branch('jet_Pt'           ,jet_Pt        )
outputTree.Branch('jet_Eta'          ,jet_Eta       )
outputTree.Branch('jet_Phi'          ,jet_Phi       )
outputTree.Branch('jet_Mass'         ,jet_Mass      )
outputTree.Branch('jet_nJet'         ,jet_nJet      ,'jet_nJet/D')
outputTree.Branch('jet_CvsL'         ,jet_CvsL      )
outputTree.Branch('jet_CvsB'         ,jet_CvsB      )
outputTree.Branch('jet_DeepFlavCvsL' ,jet_DeepFlavCvsL      )
outputTree.Branch('jet_DeepFlavCvsB' ,jet_DeepFlavCvsB      )
outputTree.Branch('jet_qgl'          ,jet_qgl      )

outputTree.Branch('jet_chEmEF'          ,jet_chEmEF      )
outputTree.Branch('jet_jetId'           ,jet_jetId      )
outputTree.Branch('jet_muonIdx1'        ,jet_muonIdx1      )
outputTree.Branch('jet_muEF'            ,jet_muEF      )
outputTree.Branch('jet_muPtRatio'            ,jet_muPtRatio      )
outputTree.Branch('jet_nMuons'          ,jet_nMuons      )
outputTree.Branch('jet_lepFiltCustom'   ,jet_lepFiltCustom      )

outputTree.Branch('jet_btagCMVA'    ,jet_btagCMVA      )
outputTree.Branch('jet_btagDeepB'   ,jet_btagDeepB      )
outputTree.Branch('jet_btagDeepC'   ,jet_btagDeepC      )
outputTree.Branch('jet_btagDeepFlavB'   ,jet_btagDeepFlavB      )
outputTree.Branch('jet_btagCSVV2'   ,jet_btagCSVV2     )

outputTree.Branch('jetMu_Pt'         ,jetMu_Pt      ,'jetMu_Pt/D')
outputTree.Branch('jetMu_PtRel'      ,jetMu_PtRel   ,'jetMu_PtRel/D')
outputTree.Branch('jetMu_iso'        ,jetMu_iso     ,'jetMu_iso/D')
outputTree.Branch('jetMu_dz'         ,jetMu_dz      ,'jetMu_dz/D')
outputTree.Branch('jetMu_dxy'        ,jetMu_dxy     ,'jetMu_dxy/D')
outputTree.Branch('jetMu_sip3d'      ,jetMu_sip3d   ,'jetMu_sip3d/D')
outputTree.Branch('muJet_idx'        ,muJet_idx     ,'muJet_idx/D')
outputTree.Branch('nMuJet'           ,nMuJet        ,'nMuJet/D')
outputTree.Branch('dR_jet_jetMu'     ,dR_jet_jetMu  ,'dR_jet_jetMu/D')
outputTree.Branch('dR_Z_jet'       ,dR_Z_jet    ,'dR_Z_jet/D')
outputTree.Branch('dR_lep_jet_min'       ,dR_lep_jet_min    ,'dR_lep_jet_min/D')
outputTree.Branch('dPhi_muJet_MET'   ,dPhi_muJet_MET,'dPhi_muJet_MET/D')
outputTree.Branch('min_dPhi_jet_MET' ,min_dPhi_jet_MET,'min_dPhi_jet_MET/D')
outputTree.Branch('jetMuPt_by_jetPt' ,jetMuPt_by_jetPt,'jetMuPt_by_jetPt/D')

outputTree.Branch('leadCvsB_jetidx'        ,leadCvsB_jetidx     ,'leadCvsB_jetidx/D')
outputTree.Branch('leadCvsL_jetidx'        ,leadCvsL_jetidx     ,'leadCvsL_jetidx/D')

outputTree.Branch('QCDveto'        ,QCDveto     ,'QCDveto/D')

outputTree.Branch('nPV'     ,nPV        ,'nPV/D')
outputTree.Branch('nPVGood' ,nPVGood    ,'nPVGood/D')
outputTree.Branch('nSV'     ,nSV        ,'nSV/D')

if isMC:
    outputTree.Branch('jet_hadronFlv'    ,jet_hadronFlv )
    outputTree.Branch('jet_isHardLep'    ,jet_isHardLep )
outputTree.Branch('met_Pt'           ,met_Pt          ,'met_Pt/D'     )
outputTree.Branch('met_Phi'          ,met_Phi         ,'met_Phi/D')
outputTree.Branch('met_signif'       ,met_signif      ,'met_signif/D')

outputTree.Branch('Z_Mass'           ,Z_Mass          ,'Z_Mass/D'     )
outputTree.Branch('Z_Pt'             ,Z_Pt            ,'Z_Pt/D'     )
outputTree.Branch('Z_Eta'            ,Z_Eta           ,'Z_Eta/D'     )
outputTree.Branch('Z_Phi'            ,Z_Phi           ,'Z_Phi/D'     )

outputTree.Branch('Z_Mass_best'      ,Z_Mass_best     ,'Z_Mass_best/D'     )
outputTree.Branch('dR_mu_mu_best'    ,dR_mu_mu_best   ,'dR_mu_mu_best/D'     )


outputTree.Branch('W_Mass'           ,W_Mass          ,'W_Mass/D'     )
outputTree.Branch('W_Pt'             ,W_Pt            ,'W_Pt/D'     )
outputTree.Branch('W_Eta'            ,W_Eta           ,'W_Eta/D'     )
outputTree.Branch('W_Phi'            ,W_Phi           ,'W_Phi/D'     )

outputTree.Branch('W_Mass_nuSol'     ,W_Mass_nuSol    ,'W_Mass_nuSol/D'     )
outputTree.Branch('W_Pt_nuSol'       ,W_Pt_nuSol      ,'W_Pt_nuSol/D'     )
outputTree.Branch('W_Eta_nuSol'      ,W_Eta_nuSol     ,'W_Eta_nuSol/D'     )
outputTree.Branch('W_Phi_nuSol'      ,W_Phi_nuSol     ,'W_Phi_nuSol/D'     )

outputTree.Branch('is_E'     ,is_E    ,'is_E/D'     )
outputTree.Branch('is_M'     ,is_M    ,'is_M/D'     )

# outputTree.Branch('is_H_mass_CR'     ,is_H_mass_CR    ,'is_H_mass_CR/D'     )
# outputTree.Branch('is_W_mass_CR'     ,is_W_mass_CR    ,'is_W_mass_CR/D'     )

outputTree.Branch('Flag_W_jet'       ,Flag_W_jet      ,'Flag_W_jet/D'     )
outputTree.Branch('solver_chi2'      ,solver_chi2     ,'solver_chi2/D'     )
outputTree.Branch('numOf_cJet'       ,numOf_cJet      ,'numOf_cJet/D'     )
outputTree.Branch('numOf_bJet'       ,numOf_bJet      ,'numOf_bJet/D'     )
outputTree.Branch('numOf_lJet'       ,numOf_lJet      ,'numOf_lJet/D'     )

outputTree.Branch('pt_Of_cJet'       ,pt_Of_cJet    )
outputTree.Branch('pt_Of_bJet'       ,pt_Of_bJet    )
outputTree.Branch('pt_Of_lJet'       ,pt_Of_lJet    )

outputTree.Branch('eta_Of_cJet'       ,eta_Of_cJet  )
outputTree.Branch('eta_Of_bJet'       ,eta_Of_bJet  )
outputTree.Branch('eta_Of_lJet'       ,eta_Of_lJet  )

outputTree.Branch('phi_Of_cJet'       ,phi_Of_cJet  )
outputTree.Branch('phi_Of_bJet'       ,phi_Of_bJet  )
outputTree.Branch('phi_Of_lJet'       ,phi_Of_lJet  )

outputTree.Branch('pt_CvsLJet1'       ,pt_CvsLJet1      ,'pt_CvsLJet1/D'     )
outputTree.Branch('pt_CvsLJet2'       ,pt_CvsLJet2      ,'pt_CvsLJet2/D'     )

outputTree.Branch('eta_CvsLJet1'       ,eta_CvsLJet1      ,'eta_CvsLJet1/D'     )
outputTree.Branch('eta_CvsLJet2'       ,eta_CvsLJet2      ,'eta_CvsLJet2/D'     )

outputTree.Branch('phi_CvsLJet1'       ,phi_CvsLJet1      ,'phi_CvsLJet1/D'     )
outputTree.Branch('phi_CvsLJet2'       ,phi_CvsLJet2      ,'phi_CvsLJet2/D'     )

outputTree.Branch('CvsL_CvsLJet1'       ,CvsL_CvsLJet1      ,'CvsL_CvsLJet1/D'     )
outputTree.Branch('CvsL_CvsLJet2'       ,CvsL_CvsLJet2      ,'CvsL_CvsLJet2/D'     )

outputTree.Branch('CvsB_CvsLJet1'       ,CvsB_CvsLJet1      ,'CvsB_CvsLJet1/D'     )
outputTree.Branch('CvsB_CvsLJet2'       ,CvsB_CvsLJet2      ,'CvsB_CvsLJet2/D'     )
if isMC:
    outputTree.Branch('hadronFlavour_CsvLJet1' ,hadronFlavour_CsvLJet1 ,'hadronFlavour_CsvLJet1/D'     )
    outputTree.Branch('hadronFlavour_CsvLJet2' ,hadronFlavour_CsvLJet2 ,'hadronFlavour_CsvLJet2/D'     )
    outputTree.Branch('is_ZtoCCorBB'     ,is_ZtoCCorBB    ,'is_ZtoCCorBB/D'     )
outputTree.Branch('HIGGS_Pt'         ,HIGGS_Pt        ,'HIGGS_Pt/D'       )
outputTree.Branch('HIGGS_CvsL_Mass'  ,HIGGS_CvsL_Mass ,'HIGGS_CvsL_Mass/D')
outputTree.Branch('HIGGS_CvsL_Pt'    ,HIGGS_CvsL_Pt   ,'HIGGS_CvsL_Pt/D')
outputTree.Branch('HIGGS_CvsL_Eta'   ,HIGGS_CvsL_Eta  ,'HIGGS_CvsL_Eta/D')
outputTree.Branch('HIGGS_CvsL_Phi'   ,HIGGS_CvsL_Phi  ,'HIGGS_CvsL_Phi/D')
outputTree.Branch('HIGGS_CvsB'       ,HIGGS_CvsB      ,'HIGGS_CvsB/D'     )
outputTree.Branch('HIGGS_CvsB_CvsL'  ,HIGGS_CvsB_CvsL ,'HIGGS_CvsB_CvsL/D')
outputTree.Branch('HIGGS_CvsB_CvsL2' ,HIGGS_CvsB_CvsL2,'HIGGS_CvsB_CvsL2/D')

outputTree.Branch('cc_HIGGS_Pt'         ,cc_HIGGS_Pt        ,'cc_HIGGS_Pt/D'       )
outputTree.Branch('cc_HIGGS_CvsL'       ,cc_HIGGS_CvsL      ,'cc_HIGGS_CvsL/D'     )
outputTree.Branch('cc_HIGGS_CvsB'       ,cc_HIGGS_CvsB      ,'cc_HIGGS_CvsB/D'     )
outputTree.Branch('cc_HIGGS_CvsB_CvsL'  ,cc_HIGGS_CvsB_CvsL ,'cc_HIGGS_CvsB_CvsL/D')
outputTree.Branch('cc_HIGGS_CvsB_CvsL2' ,cc_HIGGS_CvsB_CvsL2,'cc_HIGGS_CvsB_CvsL2/D')

outputTree.Branch('co_HIGGS_Pt'         ,co_HIGGS_Pt        ,'co_HIGGS_Pt/D'       )
outputTree.Branch('co_HIGGS_CvsL'       ,co_HIGGS_CvsL      ,'co_HIGGS_CvsL/D'     )
outputTree.Branch('co_HIGGS_CvsB'       ,co_HIGGS_CvsB      ,'co_HIGGS_CvsB/D'     )
outputTree.Branch('co_HIGGS_CvsB_CvsL'  ,co_HIGGS_CvsB_CvsL ,'co_HIGGS_CvsB_CvsL/D')
outputTree.Branch('co_HIGGS_CvsB_CvsL2' ,co_HIGGS_CvsB_CvsL2,'co_HIGGS_CvsB_CvsL2/D')

outputTree.Branch('oo_HIGGS_Pt'         ,oo_HIGGS_Pt        ,'oo_HIGGS_Pt/D'       )
outputTree.Branch('oo_HIGGS_CvsL'       ,oo_HIGGS_CvsL      ,'oo_HIGGS_CvsL/D'     )
outputTree.Branch('oo_HIGGS_CvsB'       ,oo_HIGGS_CvsB      ,'oo_HIGGS_CvsB/D'     )
outputTree.Branch('oo_HIGGS_CvsB_CvsL'  ,oo_HIGGS_CvsB_CvsL ,'oo_HIGGS_CvsB_CvsL/D')
outputTree.Branch('oo_HIGGS_CvsB_CvsL2' ,oo_HIGGS_CvsB_CvsL2,'oo_HIGGS_CvsB_CvsL2/D')

########################## MVA VARIABLES ##########################
outputTree.Branch('SoftActivityJetHT'                 ,SoftActivityJetHT                  ,'SoftActivityJetHT/D'            )
outputTree.Branch('SoftActivityJetNjets2'             ,SoftActivityJetNjets2              ,'SoftActivityJetNjets2/D'        )
outputTree.Branch('SoftActivityJetNjets5'             ,SoftActivityJetNjets5              ,'SoftActivityJetNjets5/D'        )
outputTree.Branch('SoftActivityJetNjets10'            ,SoftActivityJetNjets10             ,'SoftActivityJetNjets10/D'       )
outputTree.Branch('DPhi_VH'                     ,DPhi_VH          ,'DPhi_VH/D'          )
outputTree.Branch('DPhi_METlep'                 ,DPhi_METlep      ,'DPhi_METlep/D'      )
outputTree.Branch('W_Tmass'                     ,W_Tmass          ,'W_Tmass/D'          )
outputTree.Branch('top_Mass'                    ,top_Mass         ,'top_Mass/D'     )
outputTree.Branch('DR_cc'                       ,DR_cc            ,'DR_cc/D'         )
outputTree.Branch('lepDR_cc'                    ,lepDR_cc         ,'lepDR_cc/D'   )
outputTree.Branch('M_lep_c'                     ,M_lep_c          ,'M_lep_c/D'       )
outputTree.Branch('centrality'                  ,centrality       ,'centrality/D'       )
outputTree.Branch('avgCvsLpT'                   ,avgCvsLpT        ,'avgCvsLpT/D'        )
# outputTree.Branch('FWmoment_0'                 ,FWmoment_0      ,'FWmoment_0/D'      )
outputTree.Branch('FWmoment_1'                 ,FWmoment_1      ,'FWmoment_1/D'      )
outputTree.Branch('FWmoment_2'                 ,FWmoment_2      ,'FWmoment_2/D'      )
outputTree.Branch('FWmoment_3'                 ,FWmoment_3      ,'FWmoment_3/D'      )
outputTree.Branch('FWmoment_4'                 ,FWmoment_4      ,'FWmoment_4/D'      )
###################################################################
# ==============================================================================

# ==================== Hacks to run with NanoAOD (1 of 2) ======================
validBranches = [str(br.GetName()) for br in inputTree.GetListOfBranches()]
nEntries = inputTree.GetEntries()
count = 0
# ==============================================================================

# Begin event loop
print "Beginning loop..."
loop_time = time.time()
for entry in inputTree:
    if maxEvents > 0 and count >= maxEvents: break

    if count%10000 ==0:
        perc = float(count)/nEntries*100
        elap = time.time()-loop_time
        if perc > 0:
            eTA = "%.1f"%((100-perc)*elap/perc)
        else:
            eTA = "unknown"
        print "Number of events processed: %d of %d. %.2f%% in %.1f seconds. ETA: %s seconds."%(count,nEntries,perc,elap,eTA)
    count+=1
    h_postp.Fill(1.)


    # ====================== Initialize variables/vectors ======================
    TriggerPass = False
    elec                = []
    muon                = []

    el_List             = []
    mu_List             = []
    jetList             = []
    jet_FL_List         = []
    jet_Pt_List         = []
    jet_CvsL_List       = []
    jet_CvsB_List       = []
    jet_CvsB_CvsL_List  = []
    jet_CvsB_CvsL_List2 = []

    e_Pt_List                = []
    e_Eta_List               = []
    e_Phi_List               = []
    e_Charge_List            = []
    e_Mass_List              = []
    hardE_Jet_PtRatio[0]     = -1000

    m_Pt_List                = []
    m_Eta_List               = []
    m_Phi_List               = []
    m_Charge_List            = []
    m_Mass_List              = []
    hardMu_Jet_PtRatio[0]    = -1000
    
    lep_List                   = []
    lep_plus_List              = []
    lep_minus_List             = []

    j_Pt_List                = []
    j_Eta_List               = []
    j_Phi_List               = []
    j_Mass_List              = []
    j_CvsL_List              = []
    j_CvsB_List              = []
    j_qgl_List               = []
    if isMC:
        j_hadronFlv_List         = []
        is_ZtoCCorBB[0]     = -100
    isElec              = True
    isMuon              = True
#     is_H_mass_CR[0]     = 0
#     is_W_mass_CR[0]     = 0

    is_E[0]             = False
    is_M[0]             = False

    run[0]              = -1000
    lumiBlock[0]        = -1000
    event[0]            = -1000
    LHE_HT[0]           = -1000
    LHE_Njets[0]        = -1000

    muTrig[0]           = -1
    eleTrig[0]          = -1

    HT[0]               = -1000

    Z_Mass[0]           = -1000
    Z_Pt[0]             = -1000
    Z_Eta[0]            = -1000
    Z_Phi[0]            = -1000

    Z_Mass_best[0]      = -1000
    dR_mu_mu_best[0]    = -1000

    W_Mass[0]           = -1000
    W_Pt[0]             = -1000
    W_Eta[0]            = -1000
    W_Phi[0]            = -1000

    W_Mass_nuSol[0]     = -1000
    W_Pt_nuSol[0]       = -1000
    W_Eta_nuSol[0]      = -1000
    W_Phi_nuSol[0]      = -1000

    HIGGS_CvsL_Mass[0]  = -1000
    HIGGS_CvsL_Pt[0]    = -1000
    HIGGS_CvsL_Eta[0]   = -1000
    HIGGS_CvsL_Phi[0]   = -1000

    pt_Of_cJet.clear()
    pt_Of_bJet.clear()
    pt_Of_lJet.clear()

    eta_Of_cJet.clear()
    eta_Of_bJet.clear()
    eta_Of_lJet.clear()

    phi_Of_cJet.clear()
    phi_Of_bJet.clear()
    phi_Of_lJet.clear()

    jetMu_Pt[0]            = -1.
    jetMu_PtRel[0]         = -1000.
    jetMu_iso[0]           = -1.
    jetMu_dz[0]            = -1000.
    jetMu_dxy[0]           = -1000.
    jetMu_sip3d[0]         = -1000.
    muJet_idx[0]           = -1.
    nMuJet[0]              = -1.
    dR_Z_jet[0]            = -1000
    dR_lep_jet_min[0]       = -1000
    dR_jet_jetMu[0]        = -1000
    dPhi_muJet_MET[0]      = -1
    min_dPhi_jet_MET[0]    = -1
    jetMuPt_by_jetPt[0]    = -1
    leadCvsB_jetidx[0]        = -1
    leadCvsL_jetidx[0]        = -1
    QCDveto[0]              = -1

    nPV[0]                 = -1
    nPVGood[0]             = -1
    nSV[0]                 = -1

    jet_nJet[0]            = -1
    Flag_W_jet[0]          = -1000
    solver_chi2[0]         = -1000
    numOf_cJet[0]          = -1
    numOf_bJet[0]          = -1
    numOf_lJet[0]          = -1

    cc_HIGGS_Pt[0]         = -1
    cc_HIGGS_CvsL[0]       = -1
    cc_HIGGS_CvsB[0]       = -1
    cc_HIGGS_CvsB_CvsL[0]  = -1
    cc_HIGGS_CvsB_CvsL2[0] = -1

    co_HIGGS_Pt[0]         = -1
    co_HIGGS_CvsL[0]       = -1
    co_HIGGS_CvsB[0]       = -1
    co_HIGGS_CvsB_CvsL[0]  = -1
    co_HIGGS_CvsB_CvsL2[0] = -1

    oo_HIGGS_Pt[0]         = -1
    oo_HIGGS_CvsL[0]       = -1
    oo_HIGGS_CvsB[0]       = -1
    oo_HIGGS_CvsB_CvsL[0]  = -1
    oo_HIGGS_CvsB_CvsL2[0] = -1

    pt_CvsLJet1[0]       = -1
    pt_CvsLJet2[0]       = -1
    eta_CvsLJet1[0]      = -1000
    eta_CvsLJet2[0]      = -1000
    phi_CvsLJet1[0]      = -1000
    phi_CvsLJet2[0]      = -1000
    CvsL_CvsLJet1[0]     = -1
    CvsL_CvsLJet2[0]     = -1
    CvsB_CvsLJet1[0]     = -1
    CvsB_CvsLJet2[0]     = -1

    SoftActivityJetHT[0]       = -1000.0
    SoftActivityJetNjets2[0]   = -1000
    SoftActivityJetNjets5[0]   = -1000
    SoftActivityJetNjets10[0]  = -1000
    DPhi_VH[0]                 = -1000.0
    DPhi_METlep[0]             = -1000.0
    W_Tmass[0]                 = -1000.0
    top_Mass[0]                = -1000.0
    DR_cc[0]                   = -1000.0
    lepDR_cc[0]                = -1000.0
    M_lep_c[0]                 = -1000
    centrality[0]              = -1000.0
    avgCvsLpT[0]               = -1000.0

    if isMC:
        hadronFlavour_CsvLJet1[0] = -100
        hadronFlavour_CsvLJet2[0] = -100
    E_Mass.clear()
    E_Pt.clear()
    E_Eta.clear()
    E_Phi.clear()
    E_Charge.clear()
    E_RelIso.clear()
    E_dz.clear()
    E_dxy.clear()
    E_sip3d.clear()
    E_ip3d.clear()

    M_Mass.clear()
    M_Pt.clear()
    M_Eta.clear()
    M_Phi.clear()
    M_Charge.clear()
    M_RelIso.clear()
    M_dz.clear()
    M_dxy.clear()
    M_sip3d.clear()
    M_ip3d.clear()

    jet_Pt.clear()
    jet_Eta.clear()
    jet_Phi.clear()
    jet_Mass.clear()
    jet_CvsL.clear()
    jet_CvsB.clear()
    jet_DeepFlavCvsL.clear()
    jet_DeepFlavCvsB.clear()
    jet_qgl.clear()

    jet_chEmEF.clear()
    jet_jetId.clear()
    jet_muonIdx1.clear()
    jet_muEF.clear()
    jet_muPtRatio.clear()
    jet_nMuons.clear()
    jet_lepFiltCustom.clear()

    jet_btagCMVA.clear()
    jet_btagDeepB.clear()
    jet_btagDeepC.clear()
    jet_btagCSVV2.clear()
    jet_btagDeepFlavB.clear()

    if isMC:
        jet_hadronFlv.clear()
        jet_isHardLep.clear()

    met_Pt[0]             = -1
    met_Phi[0]            = -1000
    met_signif[0]         = -1000
    # ==========================================================================

    
    # =========================== JECs and MET and stuff ===============================
    if "Jet_Pt" in validBranches:
        #This is post processed Nano
        if JECName=="nom":
            jetPt = entry.Jet_Pt
            jetMass = entry.Jet_mass
            metPt = entry.MET_Pt
            metPhi = entry.MET_Phi
        else:
            exec("jetPt = entry.Jet_pt_"+JECName)
            exec("jetMass = entry.Jet_mass_"+JECName)
            exec("metPt = entry.MET_T1Smear_pt_"+JECName)
            exec("metPhi = entry.MET_T1Smear_phi_"+JECName)
    else:
        #This is raw nano
        jetPt, jetMass, metPt, metPhi = doJECCorr(entry, isMC, era, JECName)
    # ==========================================================================


    # =========================== Nano v7 vs v8+ ===============================
    if "Jet_CvsL" in validBranches:
        #This is nano v7- after post-processing
        DeepCSVCvsL = entry.Jet_CvsL
        DeepCSVCvsB = entry.Jet_CvsB
        DeepJetCvsL = entry.Jet_DeepFlavCvsL
        DeepJetCvsB = entry.Jet_DeepFlavCvsB
    else:
        #This is nano v8+ stock
        DeepCSVCvsL = entry.Jet_btagDeepCvL
        DeepCSVCvsB = entry.Jet_btagDeepCvB
        DeepJetCvsL = entry.Jet_btagDeepFlavCvL
        DeepJetCvsB = entry.Jet_btagDeepFlavCvB
    # ==========================================================================


    # =========================== Select Leptons ===============================
    if era == 2016: ElectronID = entry.Electron_mvaSpring16GP_WP80
    elif era == 2017 or era == 2018 or era == "UL2017" or era == "UL2018" or "UL2016" in era:
        if "Electron_mvaFall17V2Iso_WP80" in validBranches:
            ElectronID = entry.Electron_mvaFall17V2Iso_WP80
        else:
            ElectronID = entry.Electron_mvaFall17Iso_WP80
    
    if "Muon_pt_corrected" in validBranches: Muon_pt = entry.Muon_pt_corrected
    elif "Muon_corrected_pt" in validBranches: Muon_pt = entry.Muon_corrected_pt
    else: Muon_pt = entry.Muon_pt
    
    if debug == True:
        print "Preselection 1 : Single Lepton"
        print "                 electron selection : pt > 20 and eta<2.5"
        print "                 electron selection : Electron_mvaSpring16GP_WP80 > 0 "                # cutBased >= 3 (Medium)"
        # print "                 electron selection : Electron_pfRelIso03_all <= 0.15"
        print "                 muon selection : pt > 12 and eta<2.4"
        print "                 muon selection : Muon_tightId > 0"
        print "                 muon selection : Muon_pfRelIso04_all <= 0.15"

    for i in range(0, len(entry.Electron_pt)):
        if entry.Electron_pt[i]<15 or abs(entry.Electron_eta[i])>2.5: continue
        if abs(entry.Electron_eta[i]) > 1.442 and abs(entry.Electron_eta[i]) < 1.556: continue
        if ElectronID[i]<=0: continue
        # if entry.Electron_cutBased[i]<3: continue
        # if entry.Electron_pfRelIso03_all[i]>0.15: continue
        e_Pt_List.append(entry.Electron_pt[i])
        e_Eta_List.append(entry.Electron_eta[i])
        e_Phi_List.append(entry.Electron_phi[i])
        e_Charge_List.append(entry.Electron_charge[i])
        e_Mass_List.append(entry.Electron_mass[i])

        #Additions to check quality of hard ele
        E_RelIso.push_back(entry.Electron_pfRelIso03_all[i])
        E_dz.push_back(entry.Electron_dz[i])
        E_dxy.push_back(entry.Electron_dxy[i])
        E_sip3d.push_back(entry.Electron_sip3d[i])
        E_ip3d.push_back(entry.Electron_ip3d[i])
        hardE_jetidx = entry.Electron_jetIdx[i]
        if hardE_jetidx >= 0:
            hardE_Jet_PtRatio[0] = entry.Electron_pt[i]/jetPt[hardE_jetidx]

    for i in range(0, len(Muon_pt)):
        if Muon_pt[i]<12 or abs(entry.Muon_eta[i])>2.4: continue
        if entry.Muon_tightId[i]<=0: continue
        if entry.Muon_pfRelIso04_all[i]>0.15: continue
        m_Pt_List.append(Muon_pt[i])
        m_Eta_List.append(entry.Muon_eta[i])
        m_Phi_List.append(entry.Muon_phi[i])
        m_Charge_List.append(entry.Muon_charge[i])
        m_Mass_List.append(entry.Muon_mass[i])

        #Additions to check quality of hard muon
        M_RelIso.push_back(entry.Muon_pfRelIso04_all[i])
        M_dz.push_back(entry.Muon_dz[i])
        M_dxy.push_back(entry.Muon_dxy[i])
        M_sip3d.push_back(entry.Muon_sip3d[i])
        M_ip3d.push_back(entry.Muon_ip3d[i])
        hardMu_jetidx = entry.Muon_jetIdx[i]
        if hardMu_jetidx >= 0:
            hardMu_Jet_PtRatio[0] = Muon_pt[i]/jetPt[hardMu_jetidx]
    # ==========================================================================

    # ======================= At least 2 u+u- cut ===========================
    if len(m_Pt_List) >= 2 and len(e_Pt_List) < 2:
        isElec = False
        for i, chrg in enumerate(m_Charge_List):
            mu = TLorentzVector()
            mu.SetPtEtaPhiM(m_Pt_List[i],m_Eta_List[i],m_Phi_List[i],m_Mass_List[i])
            lep_List.append(mu)
            if chrg > 0:
                lep_plus_List.append(mu)
            else:
                lep_minus_List.append(mu)        
    
    elif len(e_Pt_List) >= 2 and len(m_Pt_List) < 2:
        isMuon = False
        for i, chrg in enumerate(e_Charge_List):
            el = TLorentzVector()
            el.SetPtEtaPhiM(e_Pt_List[i],e_Eta_List[i],e_Phi_List[i],e_Mass_List[i])
            lep_List.append(el)
            if chrg > 0:
                lep_plus_List.append(el)
            else:
                lep_minus_List.append(el)
                
    if len(lep_plus_List) < 1 or len(lep_minus_List) < 1: continue

    # ==========================================================================

    # ============================= Construct Z ================================
    foundZ = False
    for lep_plus in lep_plus_List:
        if foundZ: break
        for lep_minus in lep_minus_List:
            Z_cand = lep_plus + lep_minus
            if abs(Z_cand.M() - 91.) < 10.:
                foundZ = True
                break

    if not foundZ: continue
    Z_Mass[0] = Z_cand.M()
    Z_Eta[0] = Z_cand.Eta()
    Z_Phi[0] = Z_cand.Phi()
    Z_Pt[0] = Z_cand.Pt()
    # ==========================================================================

    # ============================== Get MET ===================================
    met_Pt[0]              = metPt
    met_Phi[0]             = metPhi
#    met_signif[0]          = entry.MET_significance

    mW = 80.38
    mH = 125 + mW
    MET = TLorentzVector()
    MET.SetPtEtaPhiM(metPt, 0., metPhi, 0.)
    sigma2 = np.array([((MET.Px()*.1)**2,0),(0,(MET.Py()*.1)**2)])
    # ==========================================================================

    # ============================ Jet selection ===============================
    if debug == True:
        print "                 Jet selection : jet_pt > 20 and jet_eta < 2.4"
        print "                 Jet selection : Jet_jetId >= 3"                 # Tight in 2016
        print "                 Jet selection : Jet_lepFilter = True"           # or Jet Mu EF < 0.8
        print "                 Jet selection : Jet_puId >= 0"

    # # ------------------------ Custom Jet_lepFilter ----------------------------
    # # (different from that in the VHcc postprocessor)
    # jetFilterFlags = [True]*len(jetPt)
    # for i in range(0, len(entry.Electron_pt)):
    #     if entry.Electron_cutBased[i]<3: continue
    #     if entry.Electron_pt[i]<20: continue
    #     # if entry.Electron_pfRelIso03_all[i]>0.15: continue
    #
    #     jetInd = entry.Electron_jetIdx[i]
    #     if jetInd >= 0:
    #         jetFilterFlags[jetInd] = False
    #
    # for i in range(0, len(Muon_pt)):
    #     if entry.Muon_tightId[i]<=0: continue
    #     if entry.Muon_dxy[i]>0.05: continue
    #     if entry.Muon_dz[i]>0.2: continue
    #     if Muon_pt[i]<15: continue
    #     if entry.Muon_pfRelIso04_all[i]>0.5: continue
    #
    #     jetInd = entry.Muon_jetIdx[i]
    #     if jetInd >= 0:
    #         jetFilterFlags[jetInd] = False
    # --------------------------------------------------------------------------

    HT_temp = 0
    totalJetEnergy = 0
    totalJetCvsL = 0
    totalJetCvsLpt = 0
    min_dPhi_jet_MET[0] = 1000
    if era == 2016 or "UL2016" in era: jetetamax = 2.4
    elif era == 2017 or era == 2018 or era == "UL2017" or era == "UL2018": jetetamax = 2.5
    for i in range(0, len(jetPt)):
        if jetPt[i]<20 or abs(entry.Jet_eta[i])>jetetamax: continue
        if entry.Jet_jetId[i] < 2: continue
        if entry.Jet_puId[i] < 4 and jetPt[i] < 50: continue
#        if jetFilterFlags[i] == False: continue

        Jet_muEF = 1 - (entry.Jet_chEmEF[i] + entry.Jet_chHEF[i] + entry.Jet_neEmEF[i] + entry.Jet_neHEF[i])
        # if Jet_muEF > 0.8: continue
        if entry.Jet_muonIdx1[i] >= 0:
            muPtRatio = Muon_pt[entry.Jet_muonIdx1[i]]/jetPt[i]
        else:
            muPtRatio = -1.

        jet =  TLorentzVector()
        jet.SetPtEtaPhiM(jetPt[i],entry.Jet_eta[i],entry.Jet_phi[i],jetMass[i])

#        if jet.DeltaR(Z_cand) < 0.5: continue
        lep_jet_dR = min(jet.DeltaR(lep_plus),jet.DeltaR(lep_minus))
        if lep_jet_dR < 0.4: continue
        
        jetList.append(jet)
        if len(jetList) == 1:
            dR_Z_jet[0] = jet.DeltaR(Z_cand)
            dR_lep_jet_min[0] = lep_jet_dR

        dPhi_jet_MET = jet.DeltaPhi(MET)
        if dPhi_jet_MET < min_dPhi_jet_MET[0]: min_dPhi_jet_MET[0] = dPhi_jet_MET

        if isMC:
            jet_FL_List.append(entry.Jet_hadronFlavour[i])
        jet_Pt_List.append(jetPt[i])
        jet_CvsL_List.append(DeepCSVCvsL[i])
        jet_CvsB_List.append(DeepCSVCvsB[i])
        jet_CvsB_CvsL_List.append((DeepCSVCvsB[i])+(DeepCSVCvsL[i]))
        jet_CvsB_CvsL_List2.append((DeepCSVCvsB[i])**2+(DeepCSVCvsL[i])**2)

        HT_temp         += jetPt[i]
        totalJetEnergy  += jet.E()
        if DeepCSVCvsL[i]>0:
            totalJetCvsLpt  += DeepCSVCvsL[i]*jetPt[i]

        j_Pt_List.append(jetPt[i])
        j_Eta_List.append(entry.Jet_eta[i])
        j_Phi_List.append(entry.Jet_phi[i])
        j_Mass_List.append(jetMass[i])
        j_CvsL_List.append(DeepCSVCvsL[i])
        j_CvsB_List.append(DeepCSVCvsB[i])
        j_qgl_List.append(entry.Jet_qgl[i])
        
        jet_DeepFlavCvsL.push_back(DeepJetCvsL[i])
        jet_DeepFlavCvsB.push_back(DeepJetCvsB[i])

        jet_chEmEF.push_back(entry.Jet_chEmEF[i])
        jet_jetId.push_back(entry.Jet_jetId[i])
        jet_muonIdx1.push_back(entry.Jet_muonIdx1[i])
        jet_muEF.push_back(Jet_muEF)
        jet_muPtRatio.push_back(muPtRatio)
        jet_nMuons.push_back(entry.Jet_nMuons[i])
        # jet_lepFiltCustom.push_back(jetFilterFlags[i])

        # jet_btagCMVA.push_back(entry.Jet_btagCMVA[i])
        jet_btagDeepB.push_back(entry.Jet_btagDeepB[i])
        # jet_btagDeepC.push_back(entry.Jet_btagDeepC[i])
        # jet_btagCSVV2.push_back(entry.Jet_btagCSVV2[i])
        jet_btagDeepFlavB.push_back(entry.Jet_btagDeepFlavB[i])

        if isMC:
            j_hadronFlv_List.append(entry.Jet_hadronFlavour[i])
            
            foundLep = False
            for iGen in range(entry.nGenPart):
                if entry.GenPart_status[iGen] != 1: continue
                genPart =  TLorentzVector()
                genPart.SetPtEtaPhiM(entry.GenPart_pt[iGen],entry.GenPart_eta[iGen],entry.GenPart_phi[iGen],entry.GenPart_mass[iGen])                
                if jet.DeltaR(genPart) > 0.4: continue
                if abs(entry.GenPart_pdgId[iGen]) not in [11,13,15]: continue
                if int(str(bin(entry.GenPart_statusFlags[iGen]))[-1]) == 1:
                    foundLep = True
                    break                   
            jet_isHardLep.push_back(foundLep)
            
    HT[0]                  = HT_temp

    if totalJetEnergy!=0:
        centrality[0]          = HT_temp/totalJetEnergy
    if HT_temp!=0:
        avgCvsLpT[0]           = (totalJetCvsLpt+1)/HT_temp

    if debug == True:
        print "Preselection 2 : at least one jet with jet_pt > 20 and jet_eta < 2.4/2.5"
    if len(jetList)<1: continue


    leadCvsB_jetidx[0] = jet_CvsB_List.index(max(jet_CvsB_List))
    leadCvsL_jetidx[0] = jet_CvsL_List.index(max(jet_CvsL_List))

    # Save jets according to hadron flavour
    if isMC:
        for i in range(0,len(j_hadronFlv_List)):
            if j_hadronFlv_List[i] == 4:
                eta_Of_cJet.push_back(j_Eta_List[i])
                pt_Of_cJet.push_back(j_Pt_List[i])
                phi_Of_cJet.push_back(j_Phi_List[i])
            elif j_hadronFlv_List[i] == 5:
                eta_Of_bJet.push_back(j_Eta_List[i])
                pt_Of_bJet.push_back(j_Pt_List[i])
                phi_Of_bJet.push_back(j_Phi_List[i])
            elif j_hadronFlv_List[i] == 0:
                eta_Of_lJet.push_back(j_Eta_List[i])
                pt_Of_lJet.push_back(j_Pt_List[i])
                phi_Of_lJet.push_back(j_Phi_List[i])
    # ==========================================================================

    # ========================= Trigger selection ==============================
    if debug == True:
        print "Preselection 4 : TRIGGERS"
        
    if isMuon:
        if "DoubleEG" in fullName or "EGamma" in fullName: continue
        if era == 2016 or "UL2016" in era:
            if ( entry.HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL == 0 ) and ( entry.HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ == 0 ) \
                and ( entry.HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL == 0 )  and ( entry.HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ == 0 ) : continue
        elif era == 2017 or era == "UL2017" or era == "UL2018":
            # DiMu3p8 = 0
            # if "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8" in validBranches: DiMu3p8 = entry.HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8
            if ( entry.HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8 == 0 ) : continue
        elif era == 2018:
            if ( entry.HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8 == 0 ): continue
    elif isElec:
        if "DoubleMuon" in fullName: continue
        if era == 2016 or "UL2016" in era:
            if ( entry.HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL == 0 ) and ( entry.HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ == 0 ): continue
        elif era == 2017 or era == "UL2017" or era == 2018  or era == "UL2018":
            if ( entry.HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL == 0 ): continue
    else:
        continue
            
         # and ( entry.HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ == 0 ): continue
    TriggerPass = True

    #muTrig[0] = 1

    # if (entry.HLT_Ele27_WPTight_Gsf == 1 ):
    #     eleTrig[0] = 1
    # else:
    #     eleTrig[0] = 0
    # ==========================================================================


    # ============================= Store leptons ==============================
    # if isElec:
    is_E[0] = isElec
    for i, ePt in enumerate(e_Pt_List):
        E_Mass.push_back(e_Mass_List[i])
        E_Pt.push_back(ePt)
        E_Eta.push_back(e_Eta_List[i])
        E_Phi.push_back(e_Phi_List[i])
        E_Charge.push_back(e_Charge_List[i])

    # if isMuon:
    is_M[0] = isMuon
    for i, mPt in enumerate(m_Pt_List):
        M_Mass.push_back(m_Mass_List[i])
        M_Pt.push_back(mPt)
        M_Eta.push_back(m_Eta_List[i])
        M_Phi.push_back(m_Phi_List[i])
        M_Charge.push_back(m_Charge_List[i])
    # ==========================================================================

    # ============================== Store jets ================================
    if isMC:
        numOf_bJet[0] = 0
        numOf_cJet[0] = 0
        numOf_lJet[0] = 0
    for i, jPt in enumerate(j_Pt_List):
        jet_Mass.push_back(j_Mass_List[i])
        jet_Pt.push_back(jPt)
        jet_Eta.push_back(j_Eta_List[i])
        jet_Phi.push_back(j_Phi_List[i])
        jet_CvsL.push_back(j_CvsL_List[i])
        jet_CvsB.push_back(j_CvsB_List[i])
        jet_qgl.push_back(j_qgl_List[i])
        if isMC:
            jet_hadronFlv.push_back(j_hadronFlv_List[i])
            if j_hadronFlv_List[i]==5:
                numOf_bJet[0] += 1
            elif j_hadronFlv_List[i]==4:
                numOf_cJet[0] += 1
            else:
                numOf_lJet[0] += 1
    jet_nJet[0]            = len(j_Pt_List)
    # ==========================================================================


    # ============================ Calculate weights ===========================
    # Sign Weights
    # if isElec:
    #     signWeight[0] = e_Charge_List[0]*jetMu_Charge*(-1.)
    # elif isMuon:
    #     signWeight[0] = m_Charge_List[0]*jetMu_Charge*(-1.)
    # else:
    #     continue

    genWeight[0] = 1.
    PUWeight[0]  = 1.
    PUWeight_up[0] = 1.
    PUWeight_down[0] = 1.
    EleIDSF[0] = 1.
    EleIDSF_up[0] = 1.
    EleIDSF_down[0] = 1.
    MuIDSF[0] = 1.
    MuIDSF_up[0] = 1.
    MuIDSF_down[0] = 1.
    MuIsoSF = 1.
    MuIsoSF_up = 1.
    MuIsoSF_down = 1.
    eventWeightUnsigned[0] = 1.
    eventWeight[0] = 1.
    eventWeightnoPU[0] = 1.
    LHEScaleWeight_muR_up[0] = 1.
    LHEScaleWeight_muR_down[0] = 1.
    # LHEScaleWeight_muF_up[0] = 1.
    LHEScaleWeight_muF_down[0] = 1.
    LHEScaleWeight_muF_up[0] = 1.

    if isMC:
        # MC Gen Weight
        genWeight[0] = entry.genWeight

        # PU Weights
        if era != 2018 and era != "UL2017" and era != "UL2018" and "UL2016" not in era:
            PUWeight[0] = entry.puWeight
            if PUWeight[0]!=0:
                PUWeight_up[0] = entry.puWeightUp/PUWeight[0]
                PUWeight_down[0] = entry.puWeightDown/PUWeight[0]
        else:
            PUWeight[0] = getPUweight(entry.Pileup_nTrueInt,0)
            if PUWeight[0]!=0:
                PUWeight_up[0] = getPUweight(entry.Pileup_nTrueInt,1)/PUWeight[0]
                PUWeight_down[0] = getPUweight(entry.Pileup_nTrueInt,-1)/PUWeight[0]

        # LHE Scale
        if "LHEScaleWeight" in validBranches:
            LHEScaleList = list(entry.LHEScaleWeight)

            if len(LHEScaleList) > 7:
                LHEScaleWeight_muR_up[0] = LHEScaleList[7]
                LHEScaleWeight_muR_down[0] = LHEScaleList[1]

            # LHEScaleWeight_muF_up[0] = LHEScaleList[5]
                LHEScaleWeight_muF_down[0] = LHEScaleList[3]
                LHEScaleWeight_muF_up[0] = LHEScaleList[5]

        # Electron ID
        # if isElec and e_Pt_List[0] < 500:
        #     xbin = EGamma2016histo2d.GetXaxis().FindBin(e_Eta_List[0])
        #     ybin = EGamma2016histo2d.GetYaxis().FindBin(e_Pt_List[0])
        #     EleIDSF[0] = EGamma2016histo2d.GetBinContent(xbin,ybin)
        #     EleIDErr = EGamma2016histo2d.GetBinError(xbin,ybin)
        #     if EleIDSF[0]!=0:
        #         EleIDSF_up[0] = (EleIDSF[0]+EleIDErr)/EleIDSF[0]
        #         EleIDSF_down[0] = (EleIDSF[0]-EleIDErr)/EleIDSF[0]
        
        for i in range(len(e_Pt_List)):
            xbin = EGammaHisto2d.GetXaxis().FindBin(e_Eta_List[i])
            ybin = max(1,min(EGammaHisto2d.GetYaxis().FindBin(e_Pt_List[i]),EGammaHisto2d.GetNbinsY()))
            EleID = EGammaHisto2d.GetBinContent(xbin,ybin)
            EleIDErr = EGammaHisto2d.GetBinError(xbin,ybin)

            EleRecoSF = 1.
            EleRecoErr = 0.
            if era == 2017 or era == "UL2017" or era == 2018 or era == "UL2018" or "UL2016" in era:
                xbin = ERecoHisto2d.GetXaxis().FindBin(e_Eta_List[i])
                ybin = max(1,min(ERecoHisto2d.GetYaxis().FindBin(e_Pt_List[i]),ERecoHisto2d.GetNbinsY()))
                EleRecoSF = ERecoHisto2d.GetBinContent(xbin,ybin)
                EleRecoErr = ERecoHisto2d.GetBinError(xbin,ybin)

            EleIDSF[0] *= EleID * EleRecoSF
            EleIDSF_up[0] *= (EleID+EleIDErr)*(EleRecoSF+EleRecoErr)
            EleIDSF_down[0] *= (EleID-EleIDErr)*(EleRecoSF-EleRecoErr)

        if EleIDSF[0]!=0:
            EleIDSF_up[0] /= EleIDSF[0]
            EleIDSF_down[0] /= EleIDSF[0]
        
        # Muon ID/Iso
        for i in range(len(m_Pt_List)):
            if era == 2016:
                xbin = MuID2016BFhisto2d.GetXaxis().FindBin(m_Eta_List[i])
                ybin = MuID2016BFhisto2d.GetYaxis().FindBin(m_Pt_List[i])
                MuIDBF = MuID2016BFhisto2d.GetBinContent(xbin,max(1,min(6,ybin)))
                MuIDBF_err = MuID2016BFhisto2d.GetBinError(xbin,max(1,min(6,ybin)))

                xbin = MuID2016GHhisto2d.GetXaxis().FindBin(m_Eta_List[i])
                ybin = MuID2016GHhisto2d.GetYaxis().FindBin(m_Pt_List[i])
                MuIDGH = MuID2016GHhisto2d.GetBinContent(xbin,max(1,min(6,ybin)))
                MuIDGH_err = MuID2016GHhisto2d.GetBinError(xbin,max(1,min(6,ybin)))

                MuIDSF[0] *= 0.55*MuIDBF + 0.45*MuIDGH

                MuIDSF_up[0] *= (0.55*(MuIDBF+MuIDBF_err) + 0.45*(MuIDGH+MuIDGH_err))
                MuIDSF_down[0] *= (0.55*(MuIDBF-MuIDBF_err) + 0.45*(MuIDGH-MuIDGH_err))

            elif era == 2017 or era == 2018:
                nbins = MuID1718histo2d.GetNbinsX()
                ybin = MuID1718histo2d.GetYaxis().FindBin(abs(m_Eta_List[i]))
                xbin = MuID1718histo2d.GetXaxis().FindBin(m_Pt_List[i])
                MuIDBF = MuID1718histo2d.GetBinContent(max(1,min(nbins,xbin)),ybin)
                MuIDBF_err = MuID1718histo2d.GetBinError(max(1,min(nbins,xbin)),ybin)
                
                MuIDSF[0] *= MuIDBF
                MuIDSF_up[0] *= (MuIDBF+MuIDBF_err)
                MuIDSF_down[0] *= (MuIDBF-MuIDBF_err)

                nbins = MuIso1718histo2d.GetNbinsX()
                ybin = MuIso1718histo2d.GetYaxis().FindBin(abs(m_Eta_List[i]))
                xbin = MuIso1718histo2d.GetXaxis().FindBin(m_Pt_List[i])
                print nbins,ybin,xbin
                MuIsoBF = MuIso1718histo2d.GetBinContent(max(1,min(nbins,xbin)),ybin)
                MuIsoBF_err = MuIso1718histo2d.GetBinError(max(1,min(nbins,xbin)),ybin)
                
                MuIsoSF *= MuIsoBF
                MuIsoSF_up *= (MuIsoBF+MuIsoBF_err)
                MuIsoSF_down *= (MuIsoBF-MuIsoBF_err)
                
            elif era == "UL2017" or era == "UL2018" or "UL2016" in era:
                nbins = MuID1718histo2d.GetNbinsY()
                xbin = MuID1718histo2d.GetXaxis().FindBin(abs(m_Eta_List[i]))
                ybin = MuID1718histo2d.GetYaxis().FindBin(m_Pt_List[i])
                MuIDBF = MuID1718histo2d.GetBinContent(xbin,max(1,min(nbins,ybin)))
                MuIDBF_err = MuID1718histo2d.GetBinError(xbin,max(1,min(nbins,ybin)))
                
                MuIDSF[0] *= MuIDBF
                MuIDSF_up[0] *= (MuIDBF+MuIDBF_err)
                MuIDSF_down[0] *= (MuIDBF-MuIDBF_err)

                nbins = MuIso1718histo2d.GetNbinsX()
                xbin = MuIso1718histo2d.GetXaxis().FindBin(abs(m_Eta_List[i]))
                ybin = MuIso1718histo2d.GetYaxis().FindBin(m_Pt_List[i])
 
                MuIsoBF = MuIso1718histo2d.GetBinContent(xbin,max(1,min(nbins,ybin)))
                MuIsoBF_err = MuIso1718histo2d.GetBinError(xbin,max(1,min(nbins,ybin)))
                
                MuIsoSF *= MuIsoBF
                MuIsoSF_up *= (MuIsoBF+MuIsoBF_err)
                MuIsoSF_down *= (MuIsoBF-MuIsoBF_err)

        MuIDSF[0] *= MuIsoSF
        MuIDSF_up[0] *= MuIsoSF_up
        MuIDSF_down[0] *= MuIsoSF_down
        if MuIDSF[0]!=0:
            MuIDSF_up[0] /= MuIDSF[0]
            MuIDSF_down[0] /= MuIDSF[0]
    
    eventWeight[0] = genWeight[0] * PUWeight[0] * MuIDSF[0] * EleIDSF[0]
    eventWeightnoPU[0] = genWeight[0] * EleIDSF[0] * MuIDSF[0]
    # print eventWeight[0], PUWeight_up[0],PUWeight_down[0],MuIDSF_up[0],MuIDSF_down[0]

    # ==========================================================================

    # ============================ Fill output tree ============================
    if len(j_Pt_List) >= 1 and TriggerPass:
        run[0]              = entry.run
        lumiBlock[0]        = entry.luminosityBlock
        event[0]            = entry.event
        if "LHE_HT" in validBranches:
            LHE_HT[0]           = entry.LHE_HT
        if "LHE_Njets" in validBranches:
            if type(entry.LHE_Njets) is str:
                LHE_Njets[0]        = ord(entry.LHE_Njets)
            else:
                LHE_Njets[0]        = entry.LHE_Njets

        nPV[0] = entry.PV_npvs
        nPVGood[0] = entry.PV_npvsGood
        nSV[0] = entry.nSV
        outputTree.Fill()
    else:
        continue
    # ==========================================================================

h_postp.Write()
outputTree.Write()

# ========================= Store gen event count ==============================
nEventTree = iFile.Get("Runs")
nEventCount = 0
nEventWeight = 0
if isMC:
    for entry2 in nEventTree:
        nEventCount += entry2.genEventCount
        nEventWeight += entry2.genEventSumw
    print "Total event processed by Nano AOD post processor/Skimmer : ", nEventCount
    h_total.SetBinContent(2,nEventWeight)
    h_nEvent.SetBinContent(2,nEventCount)
h_total.Write()
h_nEvent.Write()
# ==============================================================================

print "Total events processed : ",count
print("--- %s minutes ---" % (round((time.time() - start_time)/60,2)))
