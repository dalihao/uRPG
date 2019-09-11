# -*- coding: utf-8 -*-
import KBEngine
import SpaceContext
from KBEDebug import * 

class Teleport:
	def __init__(self):

		pass
		
	def teleportSpace(self, spaceUType, position, direction, context):
		"""
		defined.
		传送到某场景
		"""
		assert self.base != None
		self.lastSpaceUType = self.spaceUType
		
		inputContext = SpaceContext.createContext(self, spaceUType)
		if type(context) == dict:
			inputContext.update(context)

		self.getSpaces().teleportSpace(self.base, spaceUType, position, direction, inputContext)

	def getspaceKey(self, spaceUType):
		DEBUG_MSG("得到spacekey%i" % spaceUType)
		#self.spaceUType = self.getCurrSpace().spaceUType
		DEBUG_MSG("得到111111spacekey%i" % self.spaceUType)
	#--------------------------------------------------------------------------------------------
	#                              Callbacks
	#if spaceKey > 10000000:
	#	self.spaceUType = 0
	#	return
	#--------------------------------------------------------------------------------------------
	def onTeleportSpaceCB(self, spaceCellEntityCall, spaceUType, position, direction):
		"""
		defined.
		baseapp返回teleportSpace的回调
		"""
		DEBUG_MSG("Teleport::onTeleportSpaceCB: %i spaceID=%s, spaceUType=%i, nowspaceUType=%i" % \
					(self.id, spaceCellEntityCall.id, spaceUType, self.spaceUType))

		#self.getCurrSpaceBase().onLeave(self.id)
		KBEngine.globalData["space_%i" % self.spaceUType].onLeave(self.id)
		self.spaceUType = spaceUType
		self.teleport(spaceCellEntityCall, (0, 0, -10), direction)
		if spaceUType > 200:
			self.client.teleporting(spaceUType % 10)
		else:
			self.client.teleporting(spaceUType)

		self.pet = self.pet

	def onTeleportSuccess(self, nearbyEntity):
		"""
		KBEngine method.
		"""
		#self.getCurrSpaceBase().getspaceKey(self)
		DEBUG_MSG("Teleport::onTeleportSuccessspaceUType: %i-=-------" % (self.spaceUType))
		#self.getCurrSpaceBase().onEnter(self.base)
		KBEngine.globalData["space_%i" % self.spaceUType].onEnter(self.base)

		
	def onDestroy(self):
		"""
		entity销毁
		"""
		self.getCurrSpaceBase().logoutSpace(self.id)
