mport xmlrpclib
import os
from optparse import OptionParser


optparser = OptionParser()

optparser.add_option("-p", "--path", type="string", dest="path", help="Specify path to check quota")


optparser.add_option("-v", "--volume", type="string", dest="vol", help="Specify volume where path lives")
(options, args) = optparser.parse_args()




gserver = ''


if options.path is None:
        optparser.error("Must specify path to check with -p or --path and volume with -v or --volume")

if options.vol is None:
        optparser.error("Must specify volume to check with -v or --volume and volume with -v or --volume")





if options.vol == 'vol_home':
        gserver = 'http://storage1.example.com:9001'
elif options.vol == 'vol_global_scratch':
        gserver = 'http://storage2.example.com:9001'
elif options.vol == 'vol_span':
        gserver = 'http://storage0-dev.example.com:9001'
else:
        print("{0} is not a valid volume".format(vol))
        exit(1)





try:
        client = xmlrpclib.ServerProxy(gserver)
        result = client.getquota(options.path, options.vol)
except:
        print("Could not connect to {0}".format((gserver[7:])[:-5]))
        exit(1)

print result
exit()


