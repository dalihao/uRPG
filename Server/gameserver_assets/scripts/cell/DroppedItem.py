# -*- coding: utf-8 -*-
import random
import math
import time
import SCDefine
import d_spaces
import KBEngine
from KBEDebug import *
from interfaces.GameObject import GameObject

class DroppedItem(KBEngine.Entity, GameObject):
	"""
	这是一个掉地物品实体，可以拾取
	"""
	
	def __init__(self):
		KBEngine.Entity.__init__(self)
		GameObject.__init__(self) 
		self.pickerID = 0
		self.whomID = 0
		self.DESTROY_TIMER = 1001
		self.CANPICK_TIMER = 1002
		self.addTimer(SCDefine.TIMER_DESTROY_ITEMSEC, 0 ,self.DESTROY_TIMER)
		self.addTimer(SCDefine.TIMER_CANPICK_ITEMSEC, 0 ,self.CANPICK_TIMER)

	def pickUpRequest(self, whomID):
		picker = KBEngine.entities[whomID]
		if self.belong != 0:
			if self.belong == whomID :
				if self.pickerID == 0:
					picker.base.pickUpResponse(True, self, self.itemId, self.itemCount, self.lucky, self.arrt1, self.arrt2, self.arrt3, self.arrt4, self.arrt5)
					self.whomID = whomID
			else:
				picker.client.errorInfo("无法拾取！", 1)
			return
		if self.pickerID == 0 and self.belong == 0:
			picker.base.pickUpResponse(True, self, self.itemId, self.itemCount, self.lucky, self.arrt1, self.arrt2,
			                           self.arrt3, self.arrt4, self.arrt5)
			self.whomID = whomID

	def candestroyself(self):
		self.pickerID = self.whomID
		self.addTimer(0.1, 0, self.DESTROY_TIMER)


	def onTimer( self, timerId, userId):
		if userId == self.DESTROY_TIMER:
			self.destroy()
		if userId == self.CANPICK_TIMER:
			self.belong = 0