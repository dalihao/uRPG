# -*- coding: utf-8 -*-
import KBEngine
import random
import SCDefine
import copy
import math
from KBEDebug import *
from interfaces.GameObject import GameObject
import d_entities
import d_spaces
import d_spaces_person
import d_spaces_spawns
import xml.etree.ElementTree as etree

class Space(KBEngine.Entity, GameObject):
	"""
	私人地图
	"""
	def __init__(self):
		KBEngine.Entity.__init__(self)
		GameObject.__init__(self)
		self.createCellEntityInNewSpace(None)

		self.spaceUTypeB = self.cellData["spaceUType"] % 10
		self.spaceUTypeC = self.cellData["spaceUType"]
		self.name = self.cellData["name"]

		self.spaceResName = d_spaces_person.datas.get(self.spaceUTypeB)['resPath']

		# 这个地图上创建的entity总数

		DEBUG_MSG("此空间的ID：：：：：%i：：：" % (self.spaceKey))


		#KBEngine.globalData["space_%i" % self.spaceKey] = self

		self.tmpCreateEntityDatas = []
		self.avatars = {}
		self.createSpawnPointDatas()
		self.timetid = -1

	def getspaceKey(self, cellcall):
		cellcall.getspaceKey(self.spaceUTypeC)

	def createSpawnPointDatas(self):
		"""
		"""
		res = r"scripts\data\spawnpoints\%s_spawnpoints.xml" % (self.spaceResName.replace("\\", "/").split("/")[-1])
		if(len(self.spaceResName) == 0 or not KBEngine.hasRes(res)):
			return

		res = KBEngine.getResFullPath(res)

		tree = etree.parse(res)
		root = tree.getroot()

		for child in root:
			positionNode = child[0][0]
			directionNode = child[0][1]
			scaleNode = child[0][2]

			scale = int(((float(scaleNode[0].text) + float(scaleNode[1].text) + float(scaleNode[2].text)) / 3.0) * 10)
			position = (float(positionNode[0].text), float(positionNode[1].text), float(positionNode[2].text))
			direction = [float(directionNode[0].text) / 360 * (math.pi * 2), float(directionNode[1].text) / 360 * (math.pi * 2), float(directionNode[2].text) / 360 * (math.pi * 2)]

			if direction[0] - math.pi > 0.0:
				direction[0] -= math.pi * 2
			if direction[1] - math.pi > 0.0:
				direction[1] -= math.pi * 2
			if direction[2] - math.pi > 0.0:
				direction[2] -= math.pi * 2

			self.tmpCreateEntityDatas.append([int(child.attrib['name']), \
			position, \
			direction, \
			scale, \
			])

	def spawnOnTimer(self, tid):
		"""
		出生怪物
		"""
		if len(self.tmpCreateEntityDatas) <= 0:
			self.delTimer(tid)
			return

		datas = self.tmpCreateEntityDatas.pop(0)

		if datas is None:
			ERROR_MSG("Space::onTimer: spawn %i is error!" % datas[0])

		KBEngine.createEntityAnywhere("SpawnPoint",
									{"spawnEntityNO"	: datas[0], 	\
									"position"			: datas[1], 	\
									"direction"			: datas[2],		\
									"modelScale"		: datas[3],		\
									"createToCell"		: self.cell})

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
		entityCall.cell.onTeleportSpaceCB(self.cell, self.spaceUTypeC, position, direction)

	def daojishi1(self, tid):
		if len(self.avatars) > 0:
			self.timetid = tid
			for key, info in self.avatars.items():
				if self.avatars[key].isDestroyed:
					return
				self.avatars[key].timetick -= 1
				if self.avatars[key].timetick <= 0:
					if self.avatars[key].ticket1 > 0 and self.spaceUTypeB == 2:
						self.avatars[key].ticket1 -= 1
						self.avatars[key].timetick = 600
						self.avatars[key].client.errorInfo("自动使用门票1张！", 1)
					elif self.avatars[key].ticket2 > 0 and self.spaceUTypeB == 3:
						self.avatars[key].ticket2 -= 1
						self.avatars[key].timetick = 1800
						self.avatars[key].client.errorInfo("自动使用门票1张！", 1)
					else:
						KBEngine.globalData["Spaces"].teleportPersonSpace(self.avatars[key], 1, (0, 0, -10), (0, 90, 0), {})
		else:
			self.delTimer(tid)

	def onTimer(self, tid, userArg):
		"""
		KBEngine method.
		引擎回调timer触发
		"""
		#DEBUG_MSG("%s::onTimer: %i, tid:%i, arg:%i" % (self.getScriptName(), self.id, tid, userArg))
		if SCDefine.TIMER_TYPE_SPACE_SPAWN_TICK == userArg:
			self.spawnOnTimer(tid)
		if SCDefine.TIMER_TYPE_DAOJISHI1 == userArg:
			self.daojishi1(tid)
		if SCDefine.TIMER_TYPE_DAOJISHI2 == userArg:
			self.daojishi1(tid)
		GameObject.onTimer(self, tid, userArg)

	def onEnter(self, entityCall):
		"""
		defined method.
		进入场景
		"""
		DEBUG_MSG("进入私人地图%i" % self.spaceUTypeC)
		entityCall.nowmap = self.spaceKey
		entityCall.nowmapname = self.name
		self.avatars[entityCall.id] = entityCall

		if self.cell is not None:
			self.cell.onEnter(entityCall)
		if (self.spaceUTypeC % 10) == 2:
			entityCall.timetick = 600
			self.addTimer(1, 1, SCDefine.TIMER_TYPE_DAOJISHI1)
		if (self.spaceUTypeC % 10) == 3:
			entityCall.timetick = 1800
			self.addTimer(1, 1, SCDefine.TIMER_TYPE_DAOJISHI2)

	def onLeave(self, entityID):
		"""
		defined method.
		离开场景
		"""
		DEBUG_MSG("离开私人地图%i" % self.spaceUTypeC)
		if entityID in self.avatars:
			self.avatars[entityID].timetick = 0
			del self.avatars[entityID]
			self.delTimer(self.timetid)

		if self.cell is not None:
			self.cell.onLeave(entityID)

	def onLoseCell(self):
		"""
		KBEngine method.
		entity的cell部分实体丢失
		"""
		KBEngine.globalData["Spaces"].onSpaceLoseCell(self.spaceUTypeB, self.spaceKey)
		GameObject.onLoseCell(self)

	def onGetCell(self):
		"""
		KBEngine method.
		entity的cell部分实体被创建成功
		"""
		self.addTimer(1,1, SCDefine.TIMER_TYPE_SPACE_SPAWN_TICK)
		self.addTimer(10, 20, SCDefine.TIMER_TYPE_CREATE_SPACESPERSON)
		KBEngine.globalData["Spaces"].onSpaceGetCell(self.spaceUTypeB, self, self.spaceKey)
		GameObject.onGetCell(self)


