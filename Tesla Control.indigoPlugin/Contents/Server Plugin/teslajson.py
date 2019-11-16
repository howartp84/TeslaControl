""" Simple Python class to access the Tesla JSON API
https://github.com/gglockner/teslajson

The Tesla JSON API is described at:
http://docs.timdorr.apiary.io/

Example:

import teslajson
c = teslajson.Connection('youremail', 'yourpassword')
v = c.vehicles[0]
v.wake_up()
v.data_request('charge_state')
v.command('charge_start')
"""

try: # Python 3
	from urllib.parse import urlencode
	from urllib.request import Request, urlopen
except: # Python 2
	from urllib import urlencode
	from urllib2 import Request, urlopen
import json
import datetime
import calendar

import requests #instead of urllib2.request

import logging
logger = logging.getLogger("Plugin.Tesla") #Can call it whatever I like

class Connection(object):
	"""Connection to Tesla Motors API"""
	def __init__(self,
			email='',
			password='',
			access_token='',
			baseurl="https://owner-api.teslamotors.com",
			api="/api/1/"):
		"""Initialize connection object

		Sets the vehicles field, a list of Vehicle objects
		associated with your account

		Required parameters:
		email: your login for teslamotors.com
		password: your password for teslamotors.com

		Optional parameters:
		access_token: API access token
		baseurl: base URL for the API
		api: API string
		"""
		self.baseurl = baseurl
		self.api = api
		self.expiration = float('inf')
		self.__sethead(access_token)
		if not access_token:
			tesla_client = self.__open2("/raw/pS7Z6yyP", baseurl="http://pastebin.com") #This is TimDorr's version, without id and api
			#logger.debug("PAH Test")
			self.oauth = {
				"grant_type" : "password",
				"client_id" : tesla_client[0],
				"client_secret" : tesla_client[1],
				"email" : email,
				"password" : password }
			self.expiration = 0 # force refresh
		treply = self.get('vehicles')
		#logger.debug(treply)
		self.vehicles = [Vehicle(v, self) for v in self.get('vehicles')['response']]  #  $array['response']

	def get(self, command):
		"""Utility command to get data from API"""
		return self.post(command, None)

	def post(self, command, data={}):
		"""Utility command to post data to API"""
		now = calendar.timegm(datetime.datetime.now().timetuple())
		if now > self.expiration:
			logger.debug(u"Token expired - renewing oauth token for 44 days...")
			auth = self.__open("/oauth/token", data=self.oauth)
			self.expiration = auth['created_at'] + auth['expires_in'] - 86400  #45 days minus 24 hours
			self.__sethead(auth['access_token'])
		return self.__open("%s%s" % (self.api, command), headers=self.head, data=data)

	def __sethead(self, access_token):
		"""Set HTTP header"""
		self.head = {"Authorization": "Bearer %s" % access_token}

	def __open(self, url, headers={}, data=None, baseurl=""):
		"""Raw urlopen command"""
		if not baseurl:
			baseurl = self.baseurl
		#req = Request("%s%s" % (baseurl, url), headers=headers)
		#try:
			#req.data = urlencode(data).encode('utf-8') # Python 3
		#except:
			#try:
				#req.add_data(urlencode(data)) # Python 2
			#except:
				#pass
		if (data == None):
			#resp = urlopen(req)
			resp = requests.get("%s%s" % (baseurl, url), headers=headers)
		else:
			try:
				data2 = urlencode(data)
				resp = requests.post("%s%s" % (baseurl, url), headers=headers, data=data2)
			except:
				resp = requests.post("%s%s" % (baseurl, url), headers=headers)
		
		#charset = resp.info().get('charset', 'utf-8')
		resp.encoding = 'utf-8'
		#return json.loads(resp.read().decode(charset))
		#logger.debug(resp)
		logger.debug("Pre-JSON: %s" % resp.text)
		#logger.debug(json.loads(resp.text))
		return json.loads(resp.text)

	def __open2(self, url, headers={}, data=None, baseurl=""):
		"""Raw urlopen command"""
		if not baseurl:
			baseurl = self.baseurl
		req = Request("%s%s" % (baseurl, url), headers=headers)
		resp = urlopen(req)
		charset = resp.info().get('charset', 'utf-8')
		raw = resp.read().decode(charset).splitlines()
		tID = raw[0][16:]
		tSecret = raw[1][20:]
		#raise ValueError("{} {}".format(tID,tSecret)) #For testing
		return tID, tSecret

class Vehicle(dict):
	"""Vehicle class, subclassed from dictionary.

	There are 3 primary methods: wake_up, data_request and command.
	data_request and command both require a name to specify the data
	or command, respectively. These names can be found in the
	Tesla JSON API."""
	def __init__(self, data, connection):
		"""Initialize vehicle class

		Called automatically by the Connection class
		"""
		super(Vehicle, self).__init__(data)
		self.connection = connection

	def data_request(self, name):
		"""Get vehicle data"""
		result = self.get('data_request/%s' % name)
		return result

	def wake_up(self):
		"""Wake the vehicle"""
		return self.post('wake_up')

	def command(self, name, data={}):
		"""Run the command for the vehicle"""
		return self.post('command/%s' % name, data)

	def get(self, command):
		"""Utility command to get data from API"""
		return self.connection.get('vehicles/%i/%s' % (self['id'], command))

	def post(self, command, data={}):
		"""Utility command to post data to API"""
		return self.connection.post('vehicles/%i/%s' % (self['id'], command), data)
