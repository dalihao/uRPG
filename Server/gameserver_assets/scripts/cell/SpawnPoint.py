# -*- coding: utf-8 -*-
import KBEngine
import SCDefine
import random
import time
from KBEDebug import *
from interfaces.GameObject import GameObject
import d_entities

class SpawnPoint(KBEngine.Entity, GameObject):
	def __init__(self):
		KBEngine.Entity.__init__(self)
		self.etype = 0
		self.bosstime = 0
		self.bossnum = 0
		self.addTimer(1, 0, SCDefine.TIMER_TYPE_SPAWN)
		self.addTimer(10, 10, SCDefine.TIMER_TYPE_SPAWNWORLD5)
		
	def spawnTimer(self):
		datas = d_entities.datas.get(self.spawnEntityNO)
		nowh = int(time.strftime('%H', time.localtime(time.time())))
		self.bosstime = nowh

		if datas is None:
			ERROR_MSG("SpawnPoint::spawn:%i not found." % self.spawnEntityNO)
			return
		self.etype = datas["etype"]

		if self.etype > 9: #传送门375
			self.position.x = random.randint(10, 375)
		if self.etype == 4:  # 世界BOSS
			self.bossnum = 1
			KBEngine.globalData["worldboss"] = 1
			KBEngine.globalData["worldbosslist"] = {}
			KBEngine.globalData["worldbosslist2"] = []
			KBEngine.globalData["worldbosslist3"] = []
			self.base.sendChatMessage("snnui【世界BOSS】已刷新！")

		params = {
			"spawnID"	: self.id,
			"spawnPos" : tuple(self.position),
			"uid" : datas["id"],
			"attspeed" : datas.get("attspeed",100),
			"utype" : datas["etype"],
			"modelID" : datas["modelID"],
			"modelScale" : self.modelScale,
			"dialogID" : datas["dialogID"],
			"name" : datas["name"],
			"descr" : datas.get("descr", ''),
			"itemId" : 2,
			"attack_Max" : datas.get("attack_Max",10),
			"attack_Min" : datas.get("attack_Min",0),
			"defence" : datas.get("defence",10),
			"HP" : datas.get("HP_Max",200),
			"HP_Max" : datas.get("HP_Max",200),
			"mexp" : datas.get("mexp",0),
			}

		if self.etype == 5:  #地狱塔
			return

		
		e = KBEngine.createEntity(datas["entityType"], self.spaceID, tuple(self.position), tuple(self.direction), params)

	#--------------------------------------------------------------------------------------------
	#                              Callbacks
	#--------------------------------------------------------------------------------------------
	def onTimer(self, tid, userArg):
		"""
		KBEngine method.
		引擎回调timer触发
		"""
		#DEBUG_MSG("%s::onTimer: %i, tid:%i, arg:%i" % (self.getScriptName(), self.id, tid, userArg))
		if SCDefine.TIMER_TYPE_SPAWN == userArg:
			self.spawnTimer()
		if SCDefine.TIMER_TYPE_SPAWNWORLD5 == userArg:
			if self.etype == 4:  # 世界BOSS
				nowh = int(time.strftime('%H', time.localtime(time.time())))
				if nowh == 9 and self.bosstime != 9 and self.bossnum == 0:
					self.spawnTimer()
					return
				if nowh == 12 and self.bosstime != 12 and self.bossnum == 0:
					self.spawnTimer()
					return
				if nowh == 18 and self.bosstime != 18 and self.bossnum == 0:
					self.spawnTimer()
					return
				if nowh == 21 and self.bosstime != 21 and self.bossnum == 0:
					self.spawnTimer()
					return
				if nowh == 23 and self.bosstime != 23 and self.bossnum == 0:
					self.spawnTimer()
					return
		GameObject.onTimer(self, tid, userArg)

	def onRestore(self):
		"""
		KBEngine method.
		entity的cell部分实体被恢复成功
		"""
		GameObject.onRestore(self)
		self.addTimer(1, 0, SCDefine.TIMER_TYPE_SPAWN)
		
	def onDestroy(self):
		"""
		KBEngine method.
		当前entity马上将要被引擎销毁
		可以在此做一些销毁前的工作
		"""
		#DEBUG_MSG("onDestroy(%i)" % self.id)
	
	def onEntityDestroyed(self, entityNO):
		"""
		defined.
		出生的entity销毁了 需要重建?
		"""
		reboretime = 3

		if self.etype == 2:
			reboretime = 30

		elif self.etype == 6:
			reboretime = 30

		elif self.etype == 4: #世界BOSS
			self.bossnum = 0
			return

		elif self.etype > 9: #传送门
			reboretime = 10
		else:
			reboretime = 3
		self.addTimer(reboretime, 0, SCDefine.TIMER_TYPE_SPAWN)
		
