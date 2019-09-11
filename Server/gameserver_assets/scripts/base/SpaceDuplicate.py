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


class SpaceDuplicate(KBEngine.Entity, GameObject):
	"""
	BOSS空间
	公共空间
	"""

	def __init__(self):
		KBEngine.Entity.__init__(self)
		GameObject.__init__(self)
		self.createCellEntityInNewSpace(None)

		self.spaceUTypeB = self.cellData["spaceUType"]
		self.name = self.cellData["name"]

		self.spaceResName = d_spaces.datas.get(self.spaceUTypeB)['resPath']
		self.eno = 0
		# 这个地图上创建的entity总数
		self.tmpCreateEntityDatas = copy.deepcopy(d_spaces_spawns.datas.get(self.spaceUTypeB, []))
		#self.tmpCreateEntityDatas = []

		self.avatars = {}
		self.createSpawnPointDatas()

	def getspaceKey(self, cellcall):
		cellcall.getspaceKey(self.spaceKey)

	def createSpawnPointDatas(self):
		"""
		"""
		res = r"scripts\data\spawnpoints\%s_spawnpoints.xml" % (self.spaceResName.replace("\\", "/").split("/")[-1])
		if (len(self.spaceResName) == 0 or not KBEngine.hasRes(res)):
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
			direction = [float(directionNode[0].text) / 360 * (math.pi * 2),
			             float(directionNode[1].text) / 360 * (math.pi * 2),
			             float(directionNode[2].text) / 360 * (math.pi * 2)]

			if direction[0] - math.pi > 0.0:
				direction[0] -= math.pi * 2
			if direction[1] - math.pi > 0.0:
				direction[1] -= math.pi * 2
			if direction[2] - math.pi > 0.0:
				direction[2] -= math.pi * 2

			self.eno = int(child.attrib['name'])
			if self.spaceResName == "spaces/worldboss":
				self.eno = 5030
			if self.spaceResName == "spaces/boss1":
				self.eno = random.choice([1022,1023,1024,1025,1026])
			if self.spaceResName == "spaces/boss2":
				self.eno = random.choice([2022,2023,2024,2025,2026])
			if self.spaceResName == "spaces/boss3":
				self.eno = random.choice([3022,3023,3024,3025,3026])
			if self.spaceResName == "spaces/boss4":
				self.eno = random.choice([4022,4023,4024,4025,4026])
			if self.spaceResName == "spaces/boss5":
				self.eno = random.choice([5022,5023,5024,5025,5026])

			self.tmpCreateEntityDatas.append([self.eno, \
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
		                              {"spawnEntityNO": datas[0], \
		                               "position"		: datas[1], \
		                               "direction"			: datas[2], \
		                               "modelScale"		: datas[3], \
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
		entityCall.cell.onTeleportSpaceCB(self.cell, self.spaceUTypeB, position, direction)


	def daojishi3(self, tid):
		if len(self.avatars) > 0:
			for key, info in self.avatars.items():
				if self.avatars[key].isDestroyed:
					return
				self.avatars[key].timetick -= 1
				if self.avatars[key].timetick <= 0:
					KBEngine.globalData["Spaces"].teleportPersonSpace(self.avatars[key], 1, (0, 0, -10), (0, 90, 0), {})



	def onTimer(self, tid, userArg):
		"""
		KBEngine method.
		引擎回调timer触发
		"""
		# DEBUG_MSG("%s::onTimer: %i, tid:%i, arg:%i" % (self.getScriptName(), self.id, tid, userArg))
		if SCDefine.TIMER_TYPE_SPACE_SPAWN_TICK == userArg:
			self.spawnOnTimer(tid)
		if SCDefine.TIMER_TYPE_DAOJISHI3 == userArg:
			self.daojishi3(tid)

		GameObject.onTimer(self, tid, userArg)

	def onEnter(self, entityCall):
		"""
		defined method.
		进入场景
		"""

		DEBUG_MSG("进入公共地图%i" % self.spaceUTypeB)
		self.avatars[entityCall.id] = entityCall

		entityCall.nowmapname = self.name
		if self.cell is not None:
			self.cell.onEnter(entityCall)
		if self.spaceUTypeB > 35:
			entityCall.timetick = 3600


	def onLeave(self, entityID):
		"""
		defined method.
		离开场景
		"""
		DEBUG_MSG("离开公共地图%i" % self.spaceUTypeB)
		if entityID in self.avatars:
			self.avatars[entityID].timetick = 0
			del self.avatars[entityID]

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
		self.addTimer(1, 1, SCDefine.TIMER_TYPE_SPACE_SPAWN_TICK)
		if self.spaceUTypeB > 35:
			self.addTimer(1, 1, SCDefine.TIMER_TYPE_DAOJISHI3)
		KBEngine.globalData["Spaces"].onSpaceGetCell(self.spaceUTypeB, self, self.spaceKey)
		GameObject.onGetCell(self)



