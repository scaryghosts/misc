#!/usr/bin/python

import json
import requests
import collections
import pickle
import smtplib
import codecs
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



class infobloxNetwork:

	def __init__ (self, network=None, comment=None):
		self.network = network
		self.comment = comment

	def __repr__(self):
		return "%s_%s" % (self.network, self.comment)




#url = 'https://150.212.156.88/wapi/v1.0/'

infile = open('infobloxlist.pickle', 'r')
oldiblist = pickle.load(infile)
infile.close()
#oldiblist= {}

url = 'https://infoblox.fq.dn/wapi/v1.0/'


body = ''
email_needs_sent = 0



try:

	response = requests.get(url + 'network?_max_results=-100000&_return_type=json&network~=', verify=False, auth=('user', 'password'))
except Exception:
	body += 'API call to infoblox failed'
	sender = '"Infoblox Check - API FAILED" <helperpanda@example.com'
        recipients = ['"Weasel, Tom" <theking@weasels.org>']
        msg = MIMEMultipart('related')
        msg['Subject'] = 'Interface Change detected'
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)
        part1 = MIMEText(body, 'html')
        msg.attach(part1)
        s = smtplib.SMTP('smtp.server.org')
        s.sendmail(sender, recipients, msg.as_string())
        s.quit()


a = response.text
response_text = json.loads(a.encode('ascii'))


iblist = collections.defaultdict(infobloxNetwork)

for net in response_text:
	comment = 'NO COMMENT'
	network = 'none'

	if 'network' in net.keys():
		network = net['network']
	else:
		body += 'Network key not found - %s' % net
		email_needs_sent += 1
		continue

	if 'comment' in net.keys():
		unicode_hunter = net['comment']
		uh = "%s" % unicode_hunter.encode('ascii', 'replace') 
		comment = uh
		

	iblist[network].network = network
	iblist[network].comment = comment


for key in iblist.keys():
        if key in oldiblist.keys():
                if str(iblist[key]) != str(oldiblist[key]):
                        body += "CHANGE: Current = %s <br> \n &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;Old = %s <br> \n" % (iblist[key], oldiblist[key])
                        email_needs_sent += 1
        else:
                body += "NEW: %s not present on old list, must be new <br> \n" % (iblist[key])
                email_needs_sent += 1
for key in oldiblist.keys():
        if key not in iblist.keys():
                body += "REMOVED: %s was present on old list but not current <br> \n" % (oldiblist[key])
		email_needs_sent += 1




#for key in iblist.keys():
#	body += "%s <br> \n" % iblist[key]



if email_needs_sent > 0:
        sender = '"Infoblox Check" <pandahelper@pandas.org>'
        recipients = ['"some dude" <somedude@whitehouse.gov']
        msg = MIMEMultipart('related')
        msg['Subject'] = 'Interface Change detected'
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)
        part1 = MIMEText(body, 'html')
        msg.attach(part1)
        s = smtplib.SMTP('smtp.pandas.use.this.org')
        s.sendmail(sender, recipients, msg.as_string())
        s.quit()



outfile = open('infobloxlist.pickle', 'w')
pickle.dump(iblist, outfile)
outfile.close()

exit()


