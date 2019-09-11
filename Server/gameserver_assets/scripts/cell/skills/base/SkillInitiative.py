# -*- coding: utf-8 -*-
import KBEngine
import random
import GlobalConst
import GlobalDefine
import time
from KBEDebug import * 
from skillbases.SObject import SObject
from skillbases.SCObject import SCObject

class SkillInitiative(SObject):
	def __init__(self):
		SObject.__init__(self)
		
	def loadFromDict(self, dictDatas):
		"""
		virtual method.
		从字典中创建这个对象
		"""
		SObject.loadFromDict(self, dictDatas)
		
		# 法术速度
		self.speed = dictDatas.get('speed', 0)
		
		# 吟唱时间
		self.intonateTime = dictDatas.get("intonateTime", 0.0)
		
		# 最小最大施放范围
		self.rangeMin = dictDatas.get('rangeMin', 0)
		self.rangeMax = dictDatas.get('rangeMax', 2)
		self.__castMaxRange = dictDatas.get("rangeMaxAdd", 10.0)
		
		# 施法转向
		self.__isRotate	= dictDatas.get("isRotate", True)
		
		# 最大受术个数
		self.maxReceiveCount = dictDatas.get("maxReceiverCount", 999)
		
		# cd
		self.limitCDs = dictDatas.get("limitCDs", [1])
		self.springCDs = dictDatas.get("springCDs", [])
		
	def getRangeMin(self, caster):
		"""
		virtual method.
		"""
		return self.rangeMin

	def getRangeMax(self, caster):
		"""
		virtual method.
		"""
		return self.rangeMax
		
	def getIntonateTime(self, caster):
		"""
		virtual method.
		"""
		return self.intonateTime
		
	def getCastMaxRange(self, caster):
		return self.getRangeMax(caster) + self.__castMaxRange

	def getSpeed(self):
		return self.speed

	def isRotate(self):
		return self.__isRotate

	def getMaxReceiverCount(self):
		return self.maxReceiverCount

	def canUse(self, caster, scObject):
		"""
		virtual method.
		可否使用 
		@param caster: 使用技能者
		@param receiver: 受技能影响者
		"""
		skillID = self.getID()
		skillCD = self.getCD()

		if scObject.getObject().state == GlobalDefine.ENTITY_STATE_DEAD:
			return GlobalConst.GC_SKILL_ENTITY_DEAD

		if caster.state == GlobalDefine.ENTITY_STATE_REST:
			return GlobalConst.GC_SKILL_ENTITY_REST

		if skillID == 4:  #普通攻击 int(round(time.time() * 1000))
			nowtime = int(round(time.time() * 1000))
			if caster.isPlayer():
				if (nowtime - caster.skill_time) < caster.DC_SPEED * 10:
					#DEBUG_MSG("超速：相差时间")
					#DEBUG_MSG(nowtime - caster.skill_time)
					return
				#DEBUG_MSG("相差时间%i(%i:%i),攻速%f" % (nowtime - caster.skill_time, nowtime, caster.skill_time, caster.DC_SPEED * 10))
				caster.skill_time = nowtime
			return GlobalConst.GC_OK
		elif skillID == 5:
			if caster.isPlayer():
				if (time.time() - caster.skill5_time) < skillCD:
					#DEBUG_MSG("超速：相差时间")
					#DEBUG_MSG(time.time() - caster.skill5_time)
					return
				#DEBUG_MSG("技能6相差时间%i(%i:%i),攻速cd%i" % (time.time() - caster.skill5_time, time.time(), caster.skill5_time, skillCD))
				if caster.MP >= 20:
					caster.skill5_time = time.time()
					caster.addMP(-20)
				else:
					caster.client.errorInfo("魔法值不足20！", 1)
					return
			return GlobalConst.GC_OK
		elif skillID == 6:
			if caster.isPlayer():
				if (time.time() - caster.skill6_time) < skillCD:
					#DEBUG_MSG("超速：相差时间")
					#DEBUG_MSG(time.time() - caster.skill6_time)
					return
				#DEBUG_MSG("技能6相差时间%i(%i:%i),攻速cd%i" % (time.time() - caster.skill6_time, time.time(), caster.skill6_time, skillCD))
				if caster.MP >= 30:
					caster.skill6_time = time.time()
					caster.addMP(-30)
				else:
					caster.client.errorInfo("魔法值不足30！", 1)
					return
			return GlobalConst.GC_OK
		
	def use(self, caster, scObject):
		"""
		virtual method.
		使用技能
		@param caster: 使用技能者
		@param receiver: 受技能影响者
		"""
		self.cast(caster, scObject)
		return GlobalConst.GC_OK
		
	def cast(self, caster, scObject):
		"""
		virtual method.
		施放技能
		"""
		delay = self.distToDelay(caster, scObject)
		#INFO_MSG("%i cast skill[%i] delay=%s." % (caster.id, self.id, delay))
		if delay <= 0.1:
			self.onArrived(caster, scObject)
		else:
			#INFO_MSG("%i add castSkill:%i. delay=%s." % (caster.id, self.id, delay))
			caster.addCastSkill(self, scObject, delay)

		self.onSkillCastOver_(caster, scObject)
		
	def distToDelay(self, caster, scObject):
		"""
		"""
		return scObject.distToDelay(self.getSpeed(), caster.position)
		
	def onArrived(self, caster, scObject):
		"""
		virtual method.
		到达了目标
		"""
		self.receive(caster, scObject.getObject())
		
	def receive_snnui(self, caster, receiver):
		"""
		virtual method.
		可以对受术者做一些事情了
		"""
		pass

	def onSkillCastOver_(self, caster, scObject):
		"""
		virtual method.
		法术施放完毕通知
		"""
		pass
