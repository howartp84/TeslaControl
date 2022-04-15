#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# Tesla Control plugin for indigo
#
# This plugin was written and published by Greg Glockner
# https://github.com/gglockner/indigo-teslacontrol
# https://github.com/gglockner/teslajson
#
# No updates to the plugin have been made in over 12 months, including no provision of data/states from the vehicle,
# so i've taken it on and developed it further.
#
# Based on sample code that is:
# Copyright (c) 2014, Perceptive Automation, LLC. All rights reserved.
# http://www.indigodomo.com

import indigo
import teslapy

import time

from math import sin, cos, sqrt, atan2, radians

#from urllib2 import HTTPError
import traceback

## TODO
# 1. Exception handling
# 2. Method to set temperature (with menu for F/C)
# 3. Events and refreshing

################################################################################
class Plugin(indigo.PluginBase):
	########################################
	def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
		indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
		self.debug = pluginPrefs.get("showDebugInfo", True)
		self.version = pluginVersion

		self.vehicles = []
		self.forceRefresh = True
		self.forceDevID = 0
		self.forceVehicleID = 0
		#self.debug = True

		self.states = {}

		self.strstates = {}
		self.numstates = {}
		self.boolstates = {}

		self.resetStates = False
		self.lastReturnedStateList = None

		self.cmdStates = {}

		#self.cmdStates["navigation_request"] = ""  #TODO
		self.cmdStates["actuate_trunk"] = ""
		self.cmdStates["auto_conditioning_start"] = "climate_state"
		self.cmdStates["auto_conditioning_stop"] = "climate_state"
		self.cmdStates["charge_max_range"] = "charge_state"
		self.cmdStates["charge_port_door_close"] = "charge_state"
		self.cmdStates["charge_port_door_open"] = "charge_state"
		self.cmdStates["charge_standard"] = "charge_state"
		self.cmdStates["charge_start"] = "charge_state"
		self.cmdStates["charge_stop"] = "charge_state"
		self.cmdStates["door_lock"] = "vehicle_state"
		self.cmdStates["door_unlock"] = "vehicle_state"
		self.cmdStates["flash_lights"] = "vehicle_state"
		self.cmdStates["honk_horn"] = ""
		self.cmdStates["remote_seat_heater_request"] = ""
		self.cmdStates["remote_start_drive"] = ""
		self.cmdStates["remote_steering_wheel_heater_request"] = ""
		self.cmdStates["reset_valet_pin"] = ""
		self.cmdStates["set_charge_limit"] = "charge_state"
		self.cmdStates["set_sentry_mode"] = ""
		self.cmdStates["set_temps"] = "climate_state"
		self.cmdStates["set_valet_mode"] = ""
		self.cmdStates["sun_roof_control"] = "vehicle_state"
		self.cmdStates["speed_limit_activate"] = "vehicle_state"
		self.cmdStates["speed_limit_deactivate"] = "vehicle_state"
		self.cmdStates["speed_limit_set_limit"] = "vehicle_state"
		self.cmdStates["speed_limit_clear_pin"] = "vehicle_state"





	########################################
	#def startup(self):
		#self.debugLog("Username: %s" % self.pluginPrefs.get("username","(Not yet saved)"))
		#self.debugLog("Username: %s" % self.un)
		#self.getVehicles()

	def closedPrefsConfigUi(self, valuesDict, userCancelled):
		# Since the dialog closed we want to set the debug flag - if you don't directly use
		# a plugin's properties (and for debugLog we don't) you'll want to translate it to
		# the appropriate stuff here.
		if not userCancelled:
			self.debug = valuesDict.get("showDebugInfo", False)
			if self.debug:
				indigo.server.log("Debug logging enabled")
			else:
				indigo.server.log("Debug logging disabled")

	def getDeviceStateList(self, dev): #Override state list
		stateList = indigo.PluginBase.getDeviceStateList(self, dev)
		if stateList is not None:
#			for key in self.states.iterkeys():
#				dynamicState1 = self.getDeviceStateDictForStringType(key, key, key)
#				stateList.append(dynamicState1)
			#self.debugLog(str(stateList))
			for key in self.strstates.keys():   #for key in self.strstates.iterkeys():
				if ((self.resetStates) and (key in stateList)):
					stateList.remove(key)
				dynamicState1 = self.getDeviceStateDictForStringType(key, key, key)
				stateList.append(dynamicState1)
			for key in self.numstates.keys():
				if ((self.resetStates) and (key in stateList)):
					stateList.remove(key)
				dynamicState1 = self.getDeviceStateDictForNumberType(key, key, key)
				stateList.append(dynamicState1)
			for key in self.boolstates.keys():
				if ((self.resetStates) and (key in stateList)):
					stateList.remove(key)
				dynamicState1 = self.getDeviceStateDictForBoolTrueFalseType(key, key, key)
				stateList.append(dynamicState1)
			if self.lastReturnedStateList is not None and self.lastReturnedStateList != stateList:
				self.debugLog("state list changed")
				self.debugLog("old state list: %s" % str(self.lastReturnedStateList))
				self.debugLog("new state list: %s" % str(stateList))
			self.lastReturnedStateList = stateList
		#self.debugLog(type(stateList))
		#self.debugLog(stateList)
		return stateList

	def getVehicles(self):
		if not self.vehicles:
			indigo.server.log("Fetching vehicles...")
			try:
				#connection = teslajson.Connection(self.pluginPrefs['username'],self.pluginPrefs['password'])
				#self.debugLog("Using API token: {}".format(connection.oauth['client_id']))
				tesla = teslapy.Tesla(self.pluginPrefs['username'])
				if not tesla.authorized:
					tesla.refresh_token(refresh_token=self.pluginPrefs['refreshToken'])
				teslaVehicles = tesla.vehicle_list()
				#self.debugLog(vehicles[0].get_vehicle_data()['vehicle_state']['car_version'])
				#self.debugLog("148 TV: ")
				#self.debugLog(teslaVehicles)
				#self.debugLog("150 __TV: ")
			except Exception as e:
				self.errorLog(e)
				self.errorLog("Error creating connection")
				self.errorLog("Plugin version: {}".format(self.version))
				self.debugLog(traceback.format_exc())
				return
			self.vehicles = dict(((v['id']),v) for v in teslaVehicles)
			indigo.server.log("{} vehicles found".format(len(self.vehicles)))
			#self.debugLog("159 SV: ")
			#self.debugLog(self.vehicles)
			for v in self.vehicles:
				self.debugLog(u"Vehicle %s: %s [%s]" % (v,self.vehicles[v]['display_name'],self.vehicles[v]['vin']))
			#self.debugLog("163 __SV: ")
		return self.vehicles

	# Generate list of cars
	def carListGenerator(self, filter="", valuesDict=None, typeId="", targetId=0):
		cars = [(k, "%s (%s)" % (v['display_name'], v['vin']))
				for k,v in self.getVehicles().items()]
		self.debugLog("carListGenerator: %s" % str(cars))
		return cars

	def closedDeviceConfigUi(self, valuesDict, userCancelled, typeId, devId):
		self.debugLog("Device ID: %s" % devId)
		vehicleId = valuesDict['car']
		#self.debugLog(valuesDict)
		#statusName="charge_state"
		#self.vehicleStatus2(statusName,vehicleId,devId)
		self.forceDevID = devId
		self.forceVehicleID = vehicleId
		self.forceRefresh = True
		indigo.server.log("ForceRefresh set:  Vehicle will refresh all data within 60 seconds.")
		return True

	### ACTIONS
	def validateActionConfigUi(self, valuesDict, typeId, actionId):
		if typeId=='set_charge_limit':
			try:
				percent = int(valuesDict['percent'])
				if percent > 100 or percent < 50:
					raise ValueError
				valuesDict['percent'] = percent
			except ValueError:
				errorsDict = indigo.Dict()
				errorsDict['percent'] = "A percentage between 50 and 100"
				return (False, valuesDict, errorsDict)
		return (True, valuesDict)

	def vehicleCommand(self, action, dev):
		vehicleId = dev.pluginProps['car']
		commandName = action.pluginTypeId
		indigo.server.log("Tesla command %s for vehicle %s" % (commandName, vehicleId))
		try:
			vehicle = self.getVehicles()[int(vehicleId)]
		except KeyError:
			self.errorLog(u"Vehicle ID %s not recognised.  Please edit your Tesla Vehicle device and re-select the appropriate car." % vehicleId)
			dev = indigo.devices[devId]
			self.debugLog(u"Indigo device '%s' holds vehicleId of %s but this no longer exists in the vehicle list held by Tesla." % (dev.name,vehicleId))
			return
		if commandName == "wake_up":
			try:
				self.response = vehicle.sync_wake_up()
				self.debugLog(self.response)
			except teslapy.VehicleError as h:
				self.errorLog(h)
				self.errorLog("Unable to wake vehicle")
			return
		data = action.props
		#self.debugLog(data)
		i = 0
		validReasons = ["already on", "already off",""]
		invalidReasons = ["cabin comfort remote settings not enabled"]
		self.response = "Incomplete"
		while True:
			try:
				self.response = vehicle.command(commandName, data)
				#self.debugLog(self.response)
			except teslapy.VehicleError as h:
				self.errorLog(h)
				self.errorLog("Unable to perform command: {}".format(commandName))
			except Exception as e:
				self.errorLog(e)
				self.errorLog("Error issuing command: {} {}".format(commandName,str(data)))
				self.errorLog("Plugin version: {}".format(self.version))
				self.debugLog(traceback.format_exc())


			#self.debugLog(self.response)


			if (self.response == "Incomplete"):
				break
			if (self.response["response"]["reason"] in validReasons) or self.response["response"]["result"] == True:
				indigo.server.log("Sent %s successfully.  Refreshing appropriate states..." % commandName)
				self.debugLog("Sent %s successfully.  Refreshing appropriate states..." % commandName)
				action.pluginTypeId = self.cmdStates[commandName]
				self.vehicleStatus(action,dev)
				break
			if (self.response["response"]["reason"] in invalidReasons):
				indigo.server.log("Command %s declined:  %s" % (commandName,self.response["response"]["reason"]))
				self.debugLog("Command %s declined:  %s" % (commandName,self.response["response"]["reason"]))
				break
			if "vehicle unavailable" in self.response["response"]["error"] or "mothership" in self.response["response"]["error"]:
				indigo.server.log("Command %s declined:  Vehicle unavailable" % commandName)
				self.debugLog("Command %s declined:  Vehicle unavailable" % commandName)
				indigo.server.log(u"Automatically sending wake_up command before retrying...")
				self.debugLog(u"Automatically sending wake_up command before retrying...")
				vehicle.wake_up() #Try waking it up
				indigo.server.log(u"Waiting 30 seconds before retrying...")
				time.sleep(30) #20 seconds here because loop waits 10 itself
			else:
				self.debugLog(u"Failed attempt %s/5 because: %s" % (i,self.response["response"]["reason"]))
				if i > 3:
					self.debugLog(u"Automatically sending wake_up command before retrying...")
					vehicle.wake_up() #Try waking it up
					self.debugLog(u"Waiting 30 seconds before retrying...")
					time.sleep(20) #20 seconds here because loop waits 10 itself
				else:
					self.debugLog(u"Retrying in 10 seconds...")
			if i >= 5:
				self.debugLog(u"%s failed after 5 attempts." % commandName)
				indigo.server.log(u"%s failed after 5 attempts." % commandName)
				break
			i= i+1
			time.sleep(10)

	def vehicleStatus(self, action, dev):
		vehicleId = dev.pluginProps['car']
		statusName = action.pluginTypeId
		#self.debugLog(str(dev))
		if (statusName == ""):
			return
		self.vehicleStatus2(statusName,vehicleId,dev.id)

	def vehicleStatus2(self,statusName,vehicleId,devId):
		if (vehicleId == 0):
			#self.debugLog("Hold your horses, i'm not ready yet!")
			return
		indigo.server.log("Tesla request %s for vehicle %s: Initialising" % (statusName, vehicleId))
		try:
			vehicle = self.getVehicles()[int(vehicleId)]
		except KeyError:
			self.errorLog(u"Vehicle ID %s not recognised.  Please edit your Tesla Vehicle device and re-select the appropriate car." % vehicleId)
			self.errorLog(self.getVehicles())
			dev = indigo.devices[devId]
			self.debugLog(u"Indigo device '%s' holds vehicleId of %s but this no longer exists in the vehicle list held by Tesla." % (dev.name,vehicleId))
			return
		dev = indigo.devices[devId]

		#self.debugLog(statusName)

#		if (statusName == "doRefresh"):
#			action = "charge_state"
#			self.vehicleStatus2(action,vehicleId,devId)
#			action = "drive_state"
#			self.vehicleStatus2(action,vehicleId,devId)
#			action = "climate_state"
#			self.vehicleStatus2(action,vehicleId,devId)
#			action = "vehicle_state"
#			self.vehicleStatus2(action,vehicleId,devId)
#			action = "gui_settings"
#			self.vehicleStatus2(action,vehicleId,devId)
#			action = "vehicle_config"
#			self.vehicleStatus2(action,vehicleId,devId)
#			return
		self.response = "Incomplete"
		try:
			if (vehicle.available() == False):
				vehicle.sync_wake_up() #Loops until online or raises VehicleError if wakeup times out
			self.response = vehicle.get_vehicle_data()
		except teslapy.HTTPError as h:
			self.errorLog(h)
			return
			#self.errorLog("Timeout retrieving status: {}".format(statusName))
			#self.debugLog(traceback.format_exc())
		except teslapy.VehicleError as h:
			self.errorLog(h)
			self.errorLog("Unable to refresh vehicle states")
#		except HTTPError as h:
#			self.errorLog(h)
#			self.errorLog("Timeout retrieving status: {}".format(statusName))
#			self.debugLog(traceback.format_exc())
		except Exception as e:
			self.errorLog(e)
			self.errorLog("Timeout retrieving status: {}".format(statusName))
			self.debugLog(traceback.format_exc())


		#self.debugLog(u"Response: %s" % str(self.response))
		#self.debugLog("331 if you want a response printout")


		if (self.response == None):
			self.errorLog("No reply...")
			return
		if (self.response == "Incomplete"):
			self.errorLog("Incomplete...")
			return
		if 'response' in self.response:
			if self.response['response'] == None:
				#self.debugLog("We don't appear to have an answer")
				if 'error' in self.response:
					#self.debugLog("ERROR ALERT")
					if "vehicle unavailable" in self.response["error"]:
						indigo.server.log("Command %s declined:  Vehicle unavailable" % statusName)
						self.debugLog("Command %s declined:  Vehicle unavailable" % statusName)
					elif "mothership" in self.response["error"]:
						indigo.server.log("Command %s declined:  Mothership unavailable" % statusName)
						self.debugLog("Command %s declined:  Mothership unavailable" % statusName)
					else:
						self.debugLog(u"No motherships found")
						return
					indigo.server.log(u"Automatically sending wake_up command before retrying...")
					self.debugLog(u"Automatically sending wake_up command before retrying...")
					vehicle.wake_up() #Try waking it up
					indigo.server.log(u"Waiting 30 seconds before retrying...")
					time.sleep(30) #30 seconds
					self.vehicleStatus2(statusName,vehicleId,devId)
					return
				else:
					self.debugLog(u"No errors")
					return
			else:
				indigo.server.log("Tesla request %s for vehicle %s: Data received" % (statusName, vehicleId))
		for k,v in self.response.items():
			#self.debugLog("State %s, value %s, type %s" % (k,v,type(v)))
			self.states[k] = v
			if (type(v) is teslapy.JsonDict):
				#indigo.server.log(u"Skipping state %s: JSON Dict found" % (k))
				#self.debugLog(v)
				#self.debugLog("370")
				for innerv in v:
					#self.debugLog("State %s, value %s, type %s" % (innerv,v[innerv],type(v[innerv])))
					#self.debugLog("373 about to updateTheState with a dict")
					self.updateTheState("%s_%s" % (k,innerv),v[innerv],dev)
				#self.debugLog("375")
			else:
				#self.debugLog("377 updateTheState with a value")
				self.updateTheState(k,v,dev)
		if (self.resetStates):
			indigo.server.log("Tesla request %s for vehicle %s: New states found - reinitialising" % (statusName, vehicleId))
			dev.stateListOrDisplayStateIdChanged()
			self.resetStates = False
			self.vehicleStatus2(statusName,vehicleId,devId) #Re-do this request now the states are reset
			return
		indigo.server.log("Tesla request %s for vehicle %s: Completed" % (statusName, vehicleId))

		#self.debugLog(str(dev.states))
		if (statusName in ["drive_state","vehicle_data"]):
			self.latLongHome = dev.ownerProps.get("latLongHome","37.394838,-122.150389").split(",")
			self.latLongWork = dev.ownerProps.get("latLongWork","37.331820,-122.03118").split(",")
			fromHomeKm = self.getDistance(dev.states['latitude'],dev.states['longitude'],float(self.latLongHome[0]),float(self.latLongHome[1]))
			fromWorkKm = self.getDistance(dev.states['latitude'],dev.states['longitude'],float(self.latLongWork[0]),float(self.latLongWork[1]))
			fromHomeM = fromHomeKm * 0.62137119223733
			fromWorkM = fromWorkKm * 0.62137119223733
			dev.updateStateOnServer("distanceFromHomeKm",round(fromHomeKm,2), uiValue=str(round(fromHomeKm,2))+"km")
			dev.updateStateOnServer("distanceFromWorkKm",round(fromWorkKm,2), uiValue=str(round(fromWorkKm,2))+"km")
			dev.updateStateOnServer("distanceFromHomeM",round(fromHomeM,2), uiValue=str(round(fromHomeM,2))+"m")
			dev.updateStateOnServer("distanceFromWorkM",round(fromWorkM,2), uiValue=str(round(fromWorkM,2))+"m")

	def updateTheState(self,inKey,inValue,dev):
		inKey = inKey.replace("vehicle_state_","")
		inKey = inKey.replace("vehicle_config_","")
		inKey = inKey.replace("charge_state_","")
		inKey = inKey.replace("climate_state_","")
		inKey = inKey.replace("drive_state_","")
		if (inKey in dev.states) and (self.resetStates == False):
			#self.debugLog("%s: %s (%s)" % (inKey,inValue,str(type(inValue))))
			if (type(inValue) is list):
				inValue = ','.join(map(str, inValue)) #Join all elements into a string
			if (type(inValue) is teslapy.JsonDict):
				for key, value in inValue.items():
					newkey = "%s_%s" % (inKey,key)
					self.updateTheState(newkey,value,dev)
				return
			try:
				dev.updateStateOnServer(inKey,inValue)
			except TypeError as t:
				self.errorLog("418 %s: %s : %s" % (str(inKey),str(inValue),t))
			if (inKey == dev.ownerProps.get("stateToDisplay","")):
				dev.updateStateOnServer("displayState",inValue)
		else:
			#self.debugLog("New states found - recreating state list...")
			self.resetStates = True #We obviously need to reset states if we've got data for one that doesn't exist
			if (inValue == None):
				self.strstates[inKey] = inValue
			elif (type(inValue) is float):
				self.numstates[inKey] = inValue
			elif (type(inValue) is int):
				self.numstates[inKey] = inValue
			elif (type(inValue) is bool):
				self.boolstates[inKey] = inValue
			elif (type(inValue) is str):
				self.strstates[inKey] = inValue
			else:
				self.strstates[inKey] = inValue

	def getDistance(self,atLat,atLong,fromLat,fromLong):
		# approximate radius of earth in km
		R = 6373.0

		lat1 = radians(float(atLat))   #Where is vehicle at
		lon1 = radians(float(atLong))
		lat2 = radians(float(fromLat)) #Where are we testing from, eg Home
		lon2 = radians(float(fromLong))

		dlon = lon2 - lon1
		dlat = lat2 - lat1

		a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
		c = 2 * atan2(sqrt(a), sqrt(1 - a))

		distance = R * c

		#self.debugLog(u"Result: %s" % distance)
		#self.debugLog(u"Should be: 278.546 km")
		return distance

	def runConcurrentThread(self):
		try:
			while True:
				if not self.vehicles:
					self.getVehicles()
				if self.forceRefresh:
					self.vehicleStatus2("vehicle_data",self.forceVehicleID,self.forceDevID)
					self.forceRefresh = False
				self.sleep(60) # in seconds
		except self.StopThread:
			# do any cleanup here
			pass