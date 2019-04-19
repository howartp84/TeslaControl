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
import teslajson

import time

from math import sin, cos, sqrt, atan2, radians

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
		self.vehicles = []
		#self.debug = True
		
		self.states = {}
		
		self.strstates = {}
		self.numstates = {}
		self.boolstates = {}
		
		self.resetStates = True
		
		self.cmdStates = {}

		self.cmdStates["set_valet_mode"] = ""
		self.cmdStates["charge_port_door_open"] = "charge_state"
		self.cmdStates["charge_standard"] = "charge_state"
		self.cmdStates["charge_max_range"] = "charge_state"
		self.cmdStates["set_charge_limit"] = "charge_state"
		self.cmdStates["charge_start"] = "charge_state"
		self.cmdStates["charge_stop"] = "charge_state"
		self.cmdStates["flash_lights"] = "vehicle_state"
		self.cmdStates["honk_horn"] = ""
		self.cmdStates["door_unlock"] = "vehicle_state"
		self.cmdStates["door_lock"] = "vehicle_state"
		self.cmdStates["set_temps"] = "climate_state"
		self.cmdStates["auto_conditioning_start"] = "climate_state"
		self.cmdStates["auto_conditioning_stop"] = "climate_state"
		self.cmdStates["sun_roof_control"] = "vehicle_state"
		self.cmdStates["actuate_trunk"] = ""
		self.cmdStates["charge_port_door_close"] = "charge_state"
		self.cmdStates["remote_start_drive"] = ""
		self.cmdStates["set_sentry_mode"] = ""
		self.cmdStates["reset_valet_pin"] = ""
		#self.cmdStates["navigation_request"] = ""  #TODO
		self.cmdStates["remote_seat_heater_request"] = ""
		self.cmdStates["remote_steering_wheel_heater_request"] = ""
		
		
	########################################
	#def startup(self):
		#self.debugLog("Username: %s" % self.pluginPrefs.get("username","(Not yet saved)"))
		#self.debugLog("Username: %s" % self.un)
		#self.getVehicles()

	def getDeviceStateList(self, dev): #Override state list
		stateList = indigo.PluginBase.getDeviceStateList(self, dev)      
		if stateList is not None:
#			for key in self.states.iterkeys():
#				dynamicState1 = self.getDeviceStateDictForStringType(key, key, key)
#				stateList.append(dynamicState1)
			#self.debugLog(str(stateList))
			for key in self.strstates.iterkeys():
				if ((self.resetStates) and (key in stateList)):
					stateList.remove(key)
				dynamicState1 = self.getDeviceStateDictForStringType(key, key, key)
				stateList.append(dynamicState1)
			for key in self.numstates.iterkeys():
				if ((self.resetStates) and (key in stateList)):
					stateList.remove(key)
				dynamicState1 = self.getDeviceStateDictForNumberType(key, key, key)
				stateList.append(dynamicState1)
			for key in self.boolstates.iterkeys():
				if ((self.resetStates) and (key in stateList)):
					stateList.remove(key)
				dynamicState1 = self.getDeviceStateDictForBoolTrueFalseType(key, key, key)
				stateList.append(dynamicState1)
		return sorted(stateList)

	def getVehicles(self):
		if not self.vehicles:
			indigo.server.log("Fetching vehicles...")
			connection = teslajson.Connection(self.pluginPrefs['username'],
											  self.pluginPrefs['password'])
			self.vehicles = dict((unicode(v['id']),v) for v in connection.vehicles)
			indigo.server.log("%i vehicles found" % len(self.vehicles))
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
		statusName="doRefresh"
		self.vehicleStatus2(statusName,vehicleId,devId)
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
		vehicle = self.getVehicles()[vehicleId]
		if commandName == "wake_up":
			response = vehicle.wake_up()
			self.debugLog(response)
			return
		data = action.props
		#self.debugLog(data)
		i = 0
		validReasons = ["already on", "already off",""]
		while True:
			response = vehicle.command(commandName, data)
			self.debugLog(response)
			if (response["response"]["reason"] in validReasons) or response["response"]["result"] == True:
				self.debugLog("Success")
				action.pluginTypeId = self.cmdStates[commandName]
				self.vehicleStatus(action,dev)
				break
			if i >= 5:
				self.debugLog("Failed")
				indigo.server.log(u"%s failed after 5 attempts" % commandName)
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
		indigo.server.log("Tesla request %s for vehicle %s" % (statusName, vehicleId))
		vehicle = self.getVehicles()[vehicleId]
		dev = indigo.devices[devId]
		
		#self.debugLog(statusName)
		
		if (statusName == "doRefresh"):
			action = "charge_state"
			self.vehicleStatus2(action,vehicleId,devId)
			action = "drive_state"
			self.vehicleStatus2(action,vehicleId,devId)
			action = "climate_state"
			self.vehicleStatus2(action,vehicleId,devId)
			action = "vehicle_state"
			self.vehicleStatus2(action,vehicleId,devId)
			action = "gui_settings"
			self.vehicleStatus2(action,vehicleId,devId)
			action = "vehicle_config"
			self.vehicleStatus2(action,vehicleId,devId)
			return
		
		response = vehicle.data_request(statusName)
		self.debugLog(str(response))
		self.debugLog("")
		for k,v in sorted(response.items()):
			self.debugLog("State %s, value %s, type %s" % (k,v,type(v)))
			self.states[k] = v
			if (type(v) is dict):
				indigo.server.log(u"Skipping state %s: JSON Dict found" % (k))
			else:
				if (k in dev.states) and (self.resetStates == False):
					#self.debugLog(str(type(v)))
					dev.updateStateOnServer(k,v)
					if (k == dev.ownerProps.get("stateToDisplay","")):
						dev.updateStateOnServer("displayState",v)
				else:
					self.resetStates = True #We obviously need to reset states if we've got data for one that doesn't exist
					if (v == None):
						self.strstates[k] = v
					elif (type(v) is float):
						self.numstates[k] = v
					elif (type(v) is int):
						self.numstates[k] = v
					elif (type(v) is bool):
						self.boolstates[k] = v
					elif (type(v) is str):
						self.strstates[k] = v
					elif (type(v) is unicode):
						self.strstates[k] = v
					else:
						self.strstates[k] = v
		if (self.resetStates):
			dev.stateListOrDisplayStateIdChanged()
			self.resetStates = False
			self.vehicleStatus2(statusName,vehicleId,devId) #Re-do this request now the states are reset
			return

		#self.debugLog(str(dev.states))
		if (statusName == "drive_state"):
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

		self.debugLog(u"Result: %s" % distance)
		#self.debugLog(u"Should be: 278.546 km")
		return distance
	
#	def runConcurrentThread(self):
#		try:
#			while True:
#				for v in indigo.devices.iter("self.teslacontrol"):
#					if len(v.states) <10:
#						anAction = action()
#						action.pluginTypeId = "doRefresh"
#						self.vehicleStatus(action,dev)
#				# Do your stuff here
#				self.sleep(60) # in seconds
#		except self.StopThread:
#			# do any cleanup here
#			pass