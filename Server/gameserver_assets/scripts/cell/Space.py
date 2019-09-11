# -*- coding: utf-8 -*-
import KBEngine
import random
from KBEDebug import *
from SpaceDuplicate import SpaceDuplicate
import d_entities
import d_spaces
import SCDefine

class Space(SpaceDuplicate):
	def __init__(self):
		SpaceDuplicate.__init__(self)

		self.avatars = {}
		self.checktimerId = self.addTimer(1800, 0, SCDefine.TIMER_TYPE_HEARDBEAT)
		#self.base.getspaceKey()

	def loginToSpace(self, avatarEntityCall, context):
		"""
		defined method.
		某个玩家请求登陆到这个space中
		"""
		avatarEntityCall.createCell(self.cell)
		self.onEnter(avatarEntityCall)

	def logoutSpace(self, entityID):
		"""
		defined method.
		某个玩家请求登出这个space
		"""
		self.onLeave(entityID)

	def teleportSpace(self, entityCall, position, direction, context):
		"""
		defined method.
		请求进入某个space中
		"""
		entityCall.cell.onTeleportSpaceCB(self.cell, self.spaceUTypeB, position, direction)

	def getspaceKey(self, spaceKey):
		self.spaceKey = spaceKey
	#--------------------------------------------------------------------------------------------
	#                              Callbacks
	#--------------------------------------------------------------------------------------------
	def onTimer(self, tid, userArg):
		"""
		KBEngine method.
		引擎回调timer触发TIMER_TYPE_DESTROY
		"""
		if SCDefine.TIMER_TYPE_HEARDBEAT == userArg:
			self.onCheckDestroyTimer()
		SpaceDuplicate.onTimer(self, tid, userArg)


	def destoryself(self):
		DEBUG_MSG("此空间被销毁: %i" % (self.id))
		self.destroy()

	def onCheckDestroyTimer(self):
		if len(self.avatars) > 0:
			self.delTimer(self.checktimerId)
			self.checktimerId = 0
			self.checktimerId = self.addTimer(1800, 0, SCDefine.TIMER_TYPE_HEARDBEAT)
			return
		else:
			# 没人了则销毁
			self.destoryself()

	def hallspawn(self, halllevel):
		datas = d_entities.datas.get(6000)

		if datas is None:
			ERROR_MSG("SpawnPoint::spawn:%i not found." % 6000)
			return
		self.etype = datas["etype"]

		params = {
			"spawnID": 6000,
			"spawnPos": (0,0,0),
			"uid": datas["id"],
			"attspeed": datas.get("attspeed", 100),
			"utype": datas["etype"],
			"modelID": datas["modelID"],
			"modelScale": self.modelScale,
			"dialogID": datas["dialogID"],
			"name": datas["name"] + str(halllevel) + "级",
			"descr": datas.get("descr", ''),
			"itemId": 2,
			"attack_Max": 1500 * halllevel* halllevel,
			"attack_Min": 800 * halllevel* halllevel,
			"defence": 500 * halllevel * halllevel,
			"HP": 20000 * halllevel * halllevel,
			"HP_Max": 20000 * halllevel * halllevel,
			"mexp": halllevel,
		}
		print(params)
		KBEngine.globalData["hall_%i" % self.spaceUType] = KBEngine.createEntity(datas["entityType"], self.spaceID, (0,0,0), tuple([0.0,0.0,0.0]),
		                          params)

	def onEnter(self, entityCall):
		"""
		defined method.
		进入场景
		"""
		DEBUG_MSG("进入私人地图cell")

		self.avatars[entityCall.id] = entityCall
		SpaceDuplicate.onEnter(self, entityCall)
		if self.spaceUType % 10 == 4:
			if "hall_%i" % self.spaceUType in KBEngine.globalData.keys() and not KBEngine.globalData["hall_%i" % self.spaceUType].isDestroyed:
				KBEngine.globalData["hall_%i" % self.spaceUType].destroy()
			entityCall.starthall(self)
		
	def onLeave(self, entityID):
		"""
		defined method.
		离开场景
		"""
		DEBUG_MSG("离开私人地图cell")
		if entityID in self.avatars:
			del self.avatars[entityID]
		
		SpaceDuplicate.onLeave(self, entityID)

