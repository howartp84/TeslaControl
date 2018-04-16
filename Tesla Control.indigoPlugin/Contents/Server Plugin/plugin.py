#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# Tesla Control plugin for indigo
# Based on sample code that is:
# Copyright (c) 2014, Perceptive Automation, LLC. All rights reserved.
# http://www.indigodomo.com

import indigo
import teslajson

## TODO
# 1. Exception handling
# 2. Method to set temperature (with menu for F/C)
# 3. Events and refreshing

################################################################################
class Plugin(indigo.PluginBase):
	########################################
	def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
		indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
		self.vehicles = []
		self.debug = True

	########################################
	def startup(self):
		self.debugLog("Username: %s" % self.pluginPrefs['username'])

	def getVehicles(self):
		if not self.vehicles:
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
			vehicle.wake_up()
			return
		data = action.props
		vehicle.command(commandName, data)
