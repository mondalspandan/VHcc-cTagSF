samplesDict2016 = {
#    Name       FileName                                                                                XSec        XSecUnc
    "WJets" : [
                ["WJetsToLNu_TuneC",                                  61526.7,    2312    ],
                ["W1JetsToLNu_TuneC",                                 11786.1,    31.57   ],
                ["W2JetsToLNu_TuneC",                                 3854.2,     11.22   ],
                ["W3JetsToLNu_TuneC",                                 1273.6,     3.36    ],
                ["W4JetsToLNu_TuneC",                                 701.4,      1.85    ]
                # ["WJetsToLNu_TuneCP5",                                       61526.7,    2312    ],
                # ["W1JetsToLNu_TuneCP5",                                      9625,       31.57   ],
                # ["W2JetsToLNu_TuneCP5",                                      3161,       11.22   ],
                # ["W3JetsToLNu_TuneCP5",                                      1468,       3.36    ],
                # ["W4JetsToLNu_TuneCP5",                                      494,        1.85    ]
              ],
    "DYJets": [
                ["DYJetsToLL_M-50_TuneC",                              6225.42 ,   124.5   ],
                ["DYJetsToLL_M-10to50_TuneC",                               18610,      0       ]
              ],
    "ttbar" : [
                ["TT_TuneCUETP8M2T4",                                    730.6,      0.5572   ],
                ["TTTo2L2Nu_TuneCP5/",                                   88.29,      4.82   ],
                ["TTToHadronic_TuneCP5/",                                377.96,      20.647   ],
                ["TTToSemiLeptonic_TuneCP5",                                      365.34,      19.95   ]
              ],
    "ST" :    [
                ["ST_s-channel",                              10.12,      0.01334 ],
                ["ST_t-channel_antitop", 26.38,      1.32    ],
                ["ST_t-channel_top",     44.33,      1.76    ],
                ["ST_tW_antitop_5f",                  35.85,      1.7     ],
                ["ST_tW_top_5f",                      35.85,      1.7     ]
              ],
    "VV" :    [
                ["WW_TuneCUETP8M1",                                                       64.3,       0.02817 ],
                ["WZ_TuneCUETP8M1",                                                       23.43,      0.01048 ],
                ["ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8",                                         3.222,      0.004901],
                ["ZZ_TuneCUETP8M1",                                                       10.16,      0.005141]
              ]
}

samplesDict2017 = {
#    Name       FileName                                                                                XSec        XSecUnc
    "WJets" : [
                ["WJetsToLNu_TuneCP5",                                       61526.7,    2312    ],
                ["W1JetsToLNu_TuneCP5",                                      9625,       31.57   ],
                ["W2JetsToLNu_TuneCP5",                                      3161,       11.22   ],
                ["W3JetsToLNu_TuneCP5",                                      1468,       3.36    ],
                ["W4JetsToLNu_TuneCP5",                                      494,        1.85    ]
              ],
    "DYJets": [
                ["DYJetsToLL_M-50_TuneCP5",                                  6225.42,    124.5   ],
                
                #["DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/",                                 6225.42,    124.5   ],
                
                ["DYJetsToLL_M-50_HT-100to200_TuneCP5",                      147.4*1.23, 0.09*1.23],
                ["DYJetsToLL_M-50_HT-200to400_TuneCP5",                      40.99*1.23, 0.04*1.23],
                ["DYJetsToLL_M-50_HT-400to600_TuneCP5",                      5.678*1.23, 0.005*1.23],
                ["DYJetsToLL_M-50_HT-600to800_TuneCP5",                      1.367*1.23, 0.0     ],
                ["DYJetsToLL_M-50_HT-800to1200_TuneCP5",                     0.6304*1.23,0.0     ],
                ["DYJetsToLL_M-50_HT-1200to2500_TuneCP5",                    0.1514*1.23,0.0     ],
                ["DYJetsToLL_M-50_HT-2500toInf_TuneCP5",                     0.003565*1.23,0.0   ],
                
                ["DYJetsToLL_M-4to50_HT-100to200_TuneCP5",                   204.0*1.23, 0.5852*1.23],
                ["DYJetsToLL_M-4to50_HT-200to400_TuneCP5",                   54.39*1.23, 0.1579*1.23],
                ["DYJetsToLL_M-4to50_HT-400to600_TuneCP5",                   5.697*1.23, 0.01672*1.23],
                ["DYJetsToLL_M-4to50_HT-600toInf_TuneCP5",                   1.85*1.23,  0.005466*1.23],
                
                ["DYJetsToLL_M-10to50_TuneCP5",                              18610,      0       ]
              ],
    "ttbar" : [
                ["TTTo2L2Nu_TuneCP5/",                                   88.29,      4.82   ],
                ["TTToHadronic_TuneCP5/",                                377.96,      20.647   ],
                ["TTToSemiLeptonic_TuneCP5",                                      365.34,      19.95   ]
              ],
    "ST" :    [
                ["ST_s-channel_4f",               3.74,       0.003591],
                ["ST_t-channel_antitop",      67.91,      0.3487  ],
                ["ST_t-channel_top",          113.3,      0.6404  ],
                ["ST_tW_antitop_5f",                       34.97,      0.02827 ],
                ["ST_tW_top_5f",                 34.91,      0.02817 ]
              ],
    "VV" :    [
                ["WW_TuneCP5",                                                            75.8,       0.1123	],
                ["WZ_TuneCP5",                                                            27.6,       0.04    ],
                ["ZZ_TuneCP5",                                                            12.14,      0.01964 ]
              ]
              #,
#    "QCD" :   [
#                ["QCD_HT100to200_TuneCP5_13TeV-madgraph-pythia8/",                                      23700000,   68560   ],
#                ["QCD_HT200to300_TuneCP5_13TeV-madgraph-pythia8/",                                      1547000,	4596    ],
#                ["QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8/",                                      322600, 	967.5   ],
#                ["QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/",                                      29980,  	90.33   ],
#                ["QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/",                                     6334,   	19.18   ],
#                ["QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/",                                    1088,   	3.319   ],
#                ["QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/",                                    99.11,  	0.3031	],
#                ["QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/",                                     20.23,  	0.06244	]
#              ]
}

samplesDict2017 = {
#    Name       FileName                                                                                XSec        XSecUnc
    "WJets" : [
                ["WJetsToLNu_TuneCP5",                                       61526.7,    2312    ],
                ["W1JetsToLNu_TuneCP5",                                      9625,       31.57   ],
                ["W2JetsToLNu_TuneCP5",                                      3161,       11.22   ],
                ["W3JetsToLNu_TuneCP5",                                      1468,       3.36    ],
                ["W4JetsToLNu_TuneCP5",                                      494,        1.85    ]

                #NLO
                # ["WJetsToLNu_TuneCP5",                                       67350.0,    286.2    ],
                # ["WJetsToLNu_0J_TuneCP5",                                    54500.0,    231    ],
                # ["WJetsToLNu_1J_TuneCP5",                                     8750.0,    35    ],
                # ["WJetsToLNu_2J_TuneCP5",                                     3010.0,    15    ],

                # ["WJetsToLNu_Pt-100To250",                                    763.7,     4.9  ],
                # ["WJetsToLNu_Pt-250To400",                                     27.55,     0.17],
                # ["WJetsToLNu_Pt-400To600",                                     3.47,     0.02],
                # ["WJetsToLNu_Pt-600ToInf",                                     0.5415,     0.003],
              ],
    "DYJets": [
                ["DYJetsToLL_M-50_TuneCP5",                                  6077.22,    121.4   ],
                
                #["DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/",                                 6225.42,    124.5   ],
                
                # ["DYJetsToLL_M-50_HT-100to200_TuneCP5",                      147.4*1.23, 0.09*1.23],
                # ["DYJetsToLL_M-50_HT-200to400_TuneCP5",                      40.99*1.23, 0.04*1.23],
                # ["DYJetsToLL_M-50_HT-400to600_TuneCP5",                      5.678*1.23, 0.005*1.23],
                # ["DYJetsToLL_M-50_HT-600to800_TuneCP5",                      1.367*1.23, 0.0     ],
                # ["DYJetsToLL_M-50_HT-800to1200_TuneCP5",                     0.6304*1.23,0.0     ],
                # ["DYJetsToLL_M-50_HT-1200to2500_TuneCP5",                    0.1514*1.23,0.0     ],
                # ["DYJetsToLL_M-50_HT-2500toInf_TuneCP5",                     0.003565*1.23,0.0   ],
                
                # ["DYJetsToLL_M-4to50_HT-100to200_TuneCP5",                   204.0*1.23, 0.5852*1.23],
                # ["DYJetsToLL_M-4to50_HT-200to400_TuneCP5",                   54.39*1.23, 0.1579*1.23],
                # ["DYJetsToLL_M-4to50_HT-400to600_TuneCP5",                   5.697*1.23, 0.01672*1.23],
                # ["DYJetsToLL_M-4to50_HT-600toInf_TuneCP5",                   1.85*1.23,  0.005466*1.23],
                
                ["DYJetsToLL_M-10to50_TuneCP5",                              18610,      0       ]
              ],
    "ttbar" : [
                ["TTTo2L2Nu_TuneCP5/",                                   88.29,      4.82   ],
                ["TTToHadronic_TuneCP5/",                                377.96,      20.647   ],
                ["TTToSemiLeptonic_TuneCP5",                                      365.34,      19.95   ]
              ],
    "ST" :    [
                ["ST_s-channel_4f",               3.74,       0.003591],
                ["ST_t-channel_antitop",      67.91,      0.3487  ],
                ["ST_t-channel_top",          113.3,      0.6404  ],
                ["ST_tW_antitop_5f",                       34.97,      0.02827 ],
                ["ST_tW_top_5f",                 34.91,      0.02817 ]
              ],
    "VV" :    [
                ["WW_TuneCP5",                                                            75.8,       0.1123	],
                ["WZ_TuneCP5",                                                            27.6,       0.04    ],
                ["ZZ_TuneCP5",                                                            12.14,      0.01964 ]
              ]
}