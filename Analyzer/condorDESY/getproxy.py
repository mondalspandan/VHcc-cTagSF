
import os
x509_file = '/tmp/x509up_u'+str(os.getuid())
if os.path.isfile(x509_file):
#    print "Found the file, renaming it and adding to the list of files to transfer to condor"
    os.system('cp '+x509_file+' x509up_user.pem')
#    inputs_to_transfer.append('x509up_user.pem')
else:
    print "The X509 file does not exist! Name: ", x509_file
    print "Run voms-proxy-init --rfc --voms cms before proceeding"
    sys.exit(1)
