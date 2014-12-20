#!/usr/bin/python
import json
import requests
from optparse import OptionParser
import sys


class CustomError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)



parser = OptionParser()
parser.add_option("-f", "--file", action="store", type="string", dest="filename", help="specify filename with list of fqdns to check")
parser.add_option("-n", "--name", action="store", type="string", dest="name", help="specify single name entry")
options, args = parser.parse_args()






if options.filename and options.name:
	raise CustomError("Can't specifiy both filename and name")
	sys.exit(1)

def getAlias(fqdn):
	url = 'https://infoblox.fq.dn/wapi/'
	
	response = requests.get(url + 'record:host?name=' + fqdn + '&_return_fields=aliases', verify=False, auth=('user', 'password'))
	rt = json.loads(response.text.encode('ascii'))
	try:
        	aliaslist = rt[0]['aliases']
        	joined = ','.join(aliaslist)
		someline = fqdn + ":" + joined
		return someline
	except Exception:
        	return None

	
if options.filename:
	
	filename = options.filename
	try:
		this_file = open(filename, 'r')
	except IOError as Exception:
		raise CustomError("Can't open filename %s" % (filename))
		sys.exit(1)

	for n in this_file.readlines():
		line = n.rstrip()
		this_alias = getAlias(line)
		if this_alias:
			print(this_alias)
	sys.exit(1)

if options.name:
		name = options.name
		this_alias = getAlias(name)
		if this_alias:
			print(this_alias)	
		sys.exit(1)

