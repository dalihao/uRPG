# -*- coding: utf-8 -*-
import KBEngine
import Functor
import d_spaces
import d_spaces_person
import SCDefine
import Watcher
from KBEDebug import *
from SpaceAlloc import *
from SpaceAllocDuplicate import *
from interfaces.GameObject import GameObject

class Spaces(KBEngine.Entity, GameObject):
	"""
	这是一个脚本层封装的空间管理器
	KBEngine的space是一个抽象空间的概念，一个空间可以被脚本层视为游戏场景、游戏房间、甚至是一个宇宙。
	"""
	def __init__(self):
		KBEngine.Entity.__init__(self)
		GameObject.__init__(self)

		# 初始化空间分配器
		self.initAlloc()
		
		# 向全局共享数据中注册这个管理器的entityCall以便在所有逻辑进程中可以方便的访问
		KBEngine.globalData["Spaces"] = self

	def initAlloc(self):
		# 注册一个定时器，在这个定时器中我们每个周期都创建出一些NPC，直到创建完所有
		self._spaceAllocs = {}

		# 私人空间列表
		self._spaceperson = {}
		self._tmpDatasperson = list(d_spaces_person.datas.keys())

		self.addTimer(3, 0.1, SCDefine.TIMER_TYPE_CREATE_SPACES)

		self._tmpDatas = list(d_spaces.datas.keys())
		for utype in self._tmpDatas:
			self._spaceAllocs[utype] = SpaceAlloc(utype)

	def getSpaceAllocs(self):
		return self._spaceAllocs


	def creatpersonspaces(self, dbid, utypeB):
		"""
		创建所有私人space
		"""
		for utype in self._tmpDatasperson:
			if (str(str(dbid) + str(utype)) not in self._spaceperson):
				self._spaceperson[str(str(dbid) + str(utype))] = SpaceAllocDuplicate(utype)
				self._spaceperson[str(str(dbid) + str(utype))].init(str(str(dbid) + str(utype)))


	def creatpersonspace(self, dbid, utypeB):
		"""
		检查私人space
		"""
		for utype in self._tmpDatasperson:
			for key in self._spaceperson.keys():
				if key == str(str(dbid) + str(utypeB)):
					return

		self._spaceperson[str(str(dbid) + str(utypeB))] = SpaceAllocDuplicate(utypeB)
		self._spaceperson[str(str(dbid) + str(utypeB))].init(str(str(dbid) + str(utypeB)))
		self.addTimer(3, 0, 20)



	def createSpaceOnTimer(self, tid):
		"""
		创建space
		"""
		if len(self._tmpDatas) > 0:
			spaceUType = self._tmpDatas.pop(0)
			self._spaceAllocs[spaceUType].init()
			
		if len(self._tmpDatas) <= 0:
			del self._tmpDatas
			self.delTimer(tid)
			
	def loginToSpace(self, avatarEntity, spaceUType, context):
		"""
		defined method.
		某个玩家请求登陆到某个space中
		"""
		self._spaceAllocs[spaceUType].loginToSpace(avatarEntity, context)

	def loginToPersonSpace(self, avatarEntity, spaceUType, context):
		"""
		defined method.
		某个玩家请求登陆到某个私人space中
		"""
		temkey = str(avatarEntity.databaseID) + str(spaceUType)
		self._spaceperson[temkey].loginToSpace(avatarEntity, spaceUType, context)

	def teleportSpace(self, entityCall, spaceUType, position, direction, context):
		"""
		defined method.
		请求进入某个space中
		"""
		#DEBUG_MSG(self._spaceAllocs[spaceUType])
		self._spaceAllocs[spaceUType].teleportSpace(entityCall, position, direction, context)

	def teleportPersonSpace(self, entityCall, spaceUType, position, direction, context):
		"""
		defined method.
		请求进入某个私人space中
		"""
		self.creatpersonspace(entityCall.databaseID, spaceUType)
		#DEBUG_MSG(self._spaceperson[str(entityCall.databaseID) + str(spaceUType)])
		self._spaceperson[str(entityCall.databaseID) + str(spaceUType)].teleportSpace(entityCall, position, direction, {"spaceKey" : int(str(entityCall.databaseID) + str(spaceUType))})



	def logoutSpace(self, avatarID, spaceKey):
		"""
		defined method.
		某个玩家请求登出这个space
		"""
		for spaceAlloc in self._spaceAllocs.values():
			space = spaceAlloc.getSpaces().get(spaceKey)
			if space:
				space.logoutSpace(avatarID)

		for spaceAlloc in self._spaceperson.values():
			space = spaceAlloc.getSpaces().get(spaceKey)
			if space:
				space.logoutSpace(avatarID)



	#--------------------------------------------------------------------------------------------
	#                              Callbacks
	#--------------------------------------------------------------------------------------------

	def onTimer(self, tid, userArg):
		"""
		KBEngine method.
		引擎回调timer触发
		"""
		#DEBUG_MSG("%s::onTimer: %i, tid:%i, arg:%i" % (self.getScriptName(), self.id, tid, userArg))
		if SCDefine.TIMER_TYPE_CREATE_SPACES == userArg:
			self.createSpaceOnTimer(tid)

		GameObject.onTimer(self, tid, userArg)
		
	def onSpaceLoseCell(self, spaceUType, spaceKey):
		"""
		defined method.
		space的cell创建好了
		"""
		if (spaceKey > 10000000):
			self._spaceAllocs[spaceUType].onSpaceLoseCell(spaceKey)
		else:
			self._spaceperson[str(spaceKey)].onSpaceLoseCell(spaceKey)
			del self._spaceperson[str(spaceKey)]
		
	def onSpaceGetCell(self, spaceUType, spaceEntityCall, spaceKey):
		"""
		defined method.
		space的cell创建好了
		"""
		if (spaceKey > 10000000):
			self._spaceAllocs[spaceUType].onSpaceGetCell(spaceEntityCall, spaceKey)
		else:
			self._spaceperson[str(spaceKey)].onSpaceGetCell(spaceEntityCall, spaceKey)

