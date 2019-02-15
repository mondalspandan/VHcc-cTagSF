import os, time, sys, Stacker

arguments= '''
            "jetMu_Pt",r"p^{soft #mu}_{T} [GeV] (REG)",25,0,25
            '''

def applyCuts(ln,reg=""):
    ln = ln.replace('ZMASSCUT','[85,95,\"invert\"]')
    ln = ln.replace('ESEL','selections=["is_E","signWeight","muptbyjetpt"]')
    ln = ln.replace('MSEL','selections=["is_M","Z_Mass","signWeight","muptbyjetpt"]')            #,["jet_muEF","muJet_idx"],"jetMu_iso"]')     #["jet_lepFiltCustom","muJet_idx"],
    ln = ln.replace('ECUT','cuts=[[1,1],[-1,1],[0,0.6]]')
    ln = ln.replace('MCUT','cuts=[[1,1],[85,95,\"invert\"],[-1,1],[0,0.4]]')                             #,[-1,0.5],[1,1e4]]
    if not reg=="": ln = ln.replace('REG',reg)
    return ln

args=[applyCuts(line.strip()) for line in arguments.split("\n") if not line.strip()=="" and not line.strip().startswith("#")]

for i, line in enumerate(args):
    tempPy = open("tempPy.py","w")
    tempPy.write("import Stacker\n")
    pythonLine = "muStack, muData = Stacker.plotStack("+line.strip()+",MSEL,MCUT,dataset=\"smu\")"
    tempPy.write(applyCuts(pythonLine,'mu')+'\n')
    pythonLine = "eStack, eData = Stacker.plotStack("+line.strip()+",ESEL,ECUT,dataset=\"sele\")"
    tempPy.write(applyCuts(pythonLine,'e')+'\n')
    pythonLine = "Stacker.plotStack("+line.strip()+",doCombine=True, finalHistList=[muStack,eStack], histoDList=[muData,eData])"
    tempPy.write(applyCuts(pythonLine,'e+mu')+'\n')

    tempPy.close()
    os.system("nohup python -u tempPy.py &> stackerLogs/"+str(i+1)+".log &")
    time.sleep(3)
    print "Submitted %d jobs: "%(i+1) + line.strip()
