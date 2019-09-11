# -*- coding: utf-8 -*-
import KBEngine
import math
import Math
import time
import random
import d_spaces
import d_spaces_person
from KBEDebug import * 

class Motion:
	"""
	移动相关的封装
	"""
	def __init__(self):
		self.position.y = -5
		self.nextMoveTime = int(time.time() + random.randint(5, 15))
	
	def stopMotion(self):
		"""
		停止移动
		"""
		if self.isMoving:
			#INFO_MSG("%i stop motion." % self.id)
			self.cancelController("Movement")
			self.isMoving = False

	def randomWalk(self, basePos):
		"""
		随机移动entity
		"""

		if self.isMoving:
			return False
			
		if time.time() < self.nextMoveTime:
			return False
		
		while True:
			if abs(self.position.x - self.spawnPos.x) > 5:
				self.nextMoveTime = int(time.time() + random.randint(5, 30))
				self.backSpawnPos()
				return
			destPos = basePos
			destPos.x = basePos.x + random.randint(-5, 5)
			destPos.z = -10

			if abs(self.position.x - destPos.x) < 2.0:
				continue

			self.gotoPosition(destPos)
			self.isMoving = True
			self.nextMoveTime = int(time.time() + random.randint(5, 30))
			break

		return True

	def resetSpeed(self):
		walkSpeed = self.getDatas()["moveSpeed"]
		if walkSpeed != self.moveSpeed:
			self.moveSpeed = walkSpeed
				
	def backSpawnPos(self):
		"""
		virtual method.
		"""
		#INFO_MSG("%s::backSpawnPos: %i, pos=%s, speed=%f." % (self.getScriptName(), self.id, self.spawnPos, self.moveSpeed * 0.1))
		
		self.resetSpeed()
		self.gotoPosition(self.spawnPos)
	
	def gotoEntity(self, targetID, dist = 0.0):
		"""
		virtual method.
		移动到entity位置
		"""
		if self.isMoving:
			self.stopMotion()
		
		entity = KBEngine.entities.get(targetID)
		if entity is None:
			DEBUG_MSG("%s::gotoEntity: not found targetID=%i" % (targetID))
			return
			
		#if entity.position.distTo(self.position) <= dist:
		if abs(entity.position.x - self.position.x) <= dist:
			return

		self.isMoving = True
		self.moveToEntity(targetID, self.moveSpeed * 0.1, dist, None, True, False)
		
	def gotoPosition(self, position, dist = 0.0):
		"""
		virtual method.
		移动到位置
		"""
		if self.isMoving:
			self.stopMotion()

		if abs(self.position.x - Math.Vector3(position).x) <= 0.05:
			return

		self.isMoving = True
		speed = self.moveSpeed * 0.1
		
		if self.canNavigate():
			self.navigate(Math.Vector3(position), speed, dist, speed, 512.0, 1, 0, None)
		else:
			if dist > 0.0:
				destPos = Math.Vector3(position) - self.position
				destPos.normalise()
				destPos *= dist
				destPos = position - destPos
			else:
				destPos = Math.Vector3(position)
			
			self.moveToPoint(destPos, speed, 0, None, 1, False)

	def getStopPoint(self, yaw = None, rayLength = 100.0):
		"""
		"""
		if yaw is None:yaw = self.yaw
		yaw = (yaw / 2);
		vv = Math.Vector3(math.sin(yaw), 0, math.cos(yaw))
		vv.normalise()
		vv *= rayLength
		
		lastPos = self.position + vv;
		
		pos = KBEngine.raycast(self.spaceID, self.layer, self.position, vv)
		if pos == None:
			pos = lastPos
			
		return pos
		
	#--------------------------------------------------------------------------------------------
	#                              Callbacks
	#--------------------------------------------------------------------------------------------
	def onMove(self, controllerId, userarg):
		"""
		KBEngine method.
		使用引擎的任何移动相关接口， 在entity一次移动完成时均会调用此接口
		"""
		#DEBUG_MSG("%s::onMove: %i controllerId =%i, userarg=%s" % \
		#				(self.getScriptName(), self.id, controllerId, userarg))
		self.isMoving = True
		
	def onMoveFailure(self, controllerId, userarg):
		"""
		KBEngine method.
		使用引擎的任何移动相关接口， 在entity一次移动完成时均会调用此接口
		"""
		#DEBUG_MSG("%s::onMoveFailure: %i controllerId =%i, userarg=%s" %  (self.getScriptName(), self.id, controllerId, userarg))
		
		self.isMoving = False
		
	def onMoveOver(self, controllerId, userarg):
		"""
		KBEngine method.
		使用引擎的任何移动相关接口， 在entity移动结束时均会调用此接口
		"""	
		self.isMoving = False
