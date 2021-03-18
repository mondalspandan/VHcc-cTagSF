from ROOT import *
import sys,os
indir = sys.argv[1]

cflCvsB = "jet_CvsB_muJet_idx+is_M_1-1+Z_Mass_85-95+Z_Mass_0-12+jetMuPt_by_jetPt_0-0.4+jet_nJet_0-4.root"
cflCvsL = "jet_CvsB_muJet_idx+is_M_1-1+Z_Mass_85-95+Z_Mass_0-12+jetMuPt_by_jetPt_0-0.4+jet_nJet_0-4.root"

bflCvsB = "jet_CvsB_muJet_idx+is_M_1-1+Z_Mass_85-95+Z_Mass_0-12+jetMuPt_by_jetPt_0-0.4+jet_nJet_5-100+diLepVeto_0-0.root"
bflCvsL = "jet_CvsL_muJet_idx+is_M_1-1+Z_Mass_85-95+Z_Mass_0-12+jetMuPt_by_jetPt_0-0.4+jet_nJet_5-100+diLepVeto_0-0.root"

subdirs = [i for i in os.listdir(indir) if os.path.isdir(i)]

for fl in []
