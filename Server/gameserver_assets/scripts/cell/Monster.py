# -*- coding: utf-8 -*-
import random
import math
import time
import KBEngine
import copy
import SCDefine
import d_entities
import d_drops
from KBEDebug import *
from interfaces.Combat import Combat
from interfaces.Spell import Spell
from interfaces.Motion import Motion
from interfaces.State import State
from interfaces.AI import AI
from interfaces.NPCObject import NPCObject

class Monster(KBEngine.Entity,
			NPCObject, 
			State,
			Motion, 
			Combat, 
			Spell, 
			AI):
	def __init__(self):
		KBEngine.Entity.__init__(self)
		NPCObject.__init__(self)
		State.__init__(self) 
		Motion.__init__(self) 
		Combat.__init__(self) 
		Spell.__init__(self) 
		AI.__init__(self) 
		
		# entity所在的层，可以设置多个不同的navmesh层来寻路, 这里20002001是warring-demo中在天上的飞龙，
		# 第0层是地面，第1层是忽略建筑物的寻路层
		if self.modelID == 20002001:
			self.layer = 1
		self.mabitimeid = 0

	def initEntity(self):
		"""
		virtual method.
		"""
		pass

	def checkInTerritory(self):
		"""
		virtual method.
		检查自己是否在可活动领地中
		"""
		return AI.checkInTerritory(self)

	def isMonster(self):
		"""
		virtual method.
		"""
		return True

	def getdropitem(self, killer, killerID):
		datas = d_drops.drops.get(self.uid)
		if datas is None:
			return
		for i in range(len(datas["drop"])):
			dropdata = d_drops.drop.get(datas["drop"][i])
			list = dropdata["items"]
			ratelist = copy.deepcopy(dropdata["rate"])
			ratelist[0] = int(ratelist[0] * (1 - (0.1 * killer.viplevel))  * 1) #测试暴率
			dropid = list[self.weight_choice(ratelist)]
			arrt1 = 0  #暴击 60
			arrt2 = 0  #暴伤 200
			arrt3 = 0  #攻击伤害  80
			arrt4 = 0  #体力  320
			arrt5 = 0  #减免  40
			if dropid > 0:
				if dropid == 1:
					killer.base.sendChatMessage("snnui【"+ killer.name + "】在地图【" + killer.getCurrSpace().name + "】获得【宠物蛋】")
				if dropid == 42:
					killer.base.sendChatMessage("snnui【"+ killer.name + "】在地图【" + killer.getCurrSpace().name + "】获得【魔法盾】")
				if dropid < 100:
					arrt1 = 0
					arrt2 = 0
					arrt3 = 0
					arrt4 = 0
					arrt5 = 0
				elif self.utype == 1:
					if dropid > 99 and dropid < 153: #武器
						arrt1 = random.randint(1, 15)  #暴击20
						arrt2 = random.randint(1, 30)  #暴伤50

					if dropid > 152 and dropid < 208: #衣服
						arrt5 = random.randint(1, 10)  # 减免15
						arrt4 = random.randint(1, 50)  # 体力80

					if dropid > 207 and dropid < 263: #头盔
						arrt3 = random.randint(1, 20)  #攻击伤害30

					if dropid > 262 and dropid < 318: #项链
						arrt1 = random.randint(1, 10)  #暴击15


					if dropid > 317 and dropid < 424: #手镯
						arrt5 = random.randint(1, 5)  # 减免20


					if dropid > 423 and dropid < 530: #戒指
						arrt2 = random.randint(1, 30)  #暴伤80


					if dropid > 529 and dropid < 585: #鞋子
						arrt4 = random.randint(1, 50)  # 体力80


					if dropid > 584 and dropid < 640: #腰带
						arrt4 = random.randint(1, 50)  # 体力80


					if dropid > 637 and dropid < 650: #攻速
						arrt1 = random.randint(0, 5)  # 暴击 5
						arrt2 = random.randint(0, 20)  # 暴伤 20
						arrt3 = random.randint(0, 10)  # 攻击伤害  10
						arrt4 = random.randint(0, 30)  # 体力  30
						arrt5 = random.randint(0, 5)  # 减免  5


					if dropid > 649 and dropid < 660: #复活
						arrt1 = random.randint(0, 5)  # 暴击 5
						arrt2 = random.randint(0, 20)  # 暴伤 20
						arrt3 = random.randint(0, 10)  # 攻击伤害  10
						arrt4 = random.randint(0, 30)  # 体力  30
						arrt5 = random.randint(0, 5)  # 减免  5


					if dropid > 659 and dropid < 678: #翅膀
						arrt1 = random.randint(0, 5)  # 暴击 5
						arrt2 = random.randint(0, 20)  # 暴伤 20
						arrt3 = random.randint(0, 10)  # 攻击伤害  10
						arrt4 = random.randint(0, 30)  # 体力  30
						arrt5 = random.randint(0, 5)  # 减免  5

				else:
					if dropid > 99 and dropid < 153: #武器
						arrt1 = random.randint(10, 20)  #暴击20
						arrt2 = random.randint(20, 50)  #暴伤50

					if dropid > 152 and dropid < 208: #衣服
						arrt5 = random.randint(5, 15)  # 减免15
						arrt4 = random.randint(30, 80)  # 体力80

					if dropid > 207 and dropid < 263: #头盔
						arrt3 = random.randint(10, 30)  #攻击伤害30

					if dropid > 262 and dropid < 318: #项链
						arrt1 = random.randint(5, 15)  #暴击15


					if dropid > 317 and dropid < 424: #手镯
						arrt5 = random.randint(5, 10)  # 减免20


					if dropid > 423 and dropid < 530: #戒指
						arrt2 = random.randint(10, 40)  #暴伤80


					if dropid > 529 and dropid < 585: #鞋子
						arrt4 = random.randint(30, 80)  # 体力80


					if dropid > 584 and dropid < 640: #腰带
						arrt4 = random.randint(30, 80)  # 体力80


					if dropid > 637 and dropid < 650: #攻速
						arrt1 = random.randint(0, 5)  # 暴击 5
						arrt2 = random.randint(0, 20)  # 暴伤 20
						arrt3 = random.randint(0, 10)  # 攻击伤害  10
						arrt4 = random.randint(0, 30)  # 体力  30
						arrt5 = random.randint(0, 5)  # 减免  5


					if dropid > 649 and dropid < 660: #复活
						arrt1 = random.randint(0, 5)  # 暴击 5
						arrt2 = random.randint(0, 20)  # 暴伤 20
						arrt3 = random.randint(0, 10)  # 攻击伤害  10
						arrt4 = random.randint(0, 30)  # 体力  30
						arrt5 = random.randint(0, 5)  # 减免  5


					if dropid > 659 and dropid < 678: #翅膀
						arrt1 = random.randint(0, 5)  # 暴击 5
						arrt2 = random.randint(0, 20)  # 暴伤 20
						arrt3 = random.randint(0, 10)  # 攻击伤害  10
						arrt4 = random.randint(0, 30)  # 体力  30
						arrt5 = random.randint(0, 5)  # 减免  5
				if dropid == 130:
					dropid = 131
				self.dropNotify(dropid, 1, 0, arrt1, arrt2, arrt3, arrt4, arrt5, killerID)


	def dropNotify(self, itemId, itemCount, lucky, arrt1, arrt2, arrt3, arrt4, arrt5, killerID):
		datas = d_entities.datas.get(40001003)
		if datas is None:
			ERROR_MSG("SpawnPoint::spawn:%i not found." % 40001003)
			return
		#itemQ  0 - 5    1: 普通武器   2：材料、门票  3：高级物品   4：终极装备   5：特殊物品
		itemQ = 0
		if itemId < 32: #宠物和神器
			itemQ = 5
		if 31 < itemId < 100: #材料、门票
			itemQ = 2
		if 117 < itemId < 130 :
			itemQ = 1
		if 141 < itemId < 153 :
			itemQ = 4
		if 129 < itemId < 142 :
			itemQ = 3
		if 187 < itemId < 208 :
			itemQ = 4
		if 178 < itemId < 188 :
			itemQ = 3
		if 251 < itemId < 263 :
			itemQ = 4
		if 233 < itemId < 252 :
			itemQ = 3
		if 306 < itemId < 318 :
			itemQ = 4
		if 288 < itemId < 307 :
			itemQ = 3
		if 361 < itemId < 373 :
			itemQ = 4
		if 343 < itemId < 362 :
			itemQ = 3
		if 412 < itemId < 424 :
			itemQ = 4
		if 398 < itemId < 413 :
			itemQ = 3
		if 467 < itemId < 479 :
			itemQ = 4
		if 449 < itemId < 468 :
			itemQ = 3
		if 520 < itemId < 530 :
			itemQ = 4
		if 504 < itemId < 521 :
			itemQ = 3
		if 573 < itemId < 585 :
			itemQ = 4
		if 559 < itemId < 574 :
			itemQ = 3
		if 637 < itemId < 640 :
			itemQ = 4
		if 614 < itemId < 638 :
			itemQ = 3
		if 639 < itemId:
			itemQ = 5


		params = {
			"uid" : datas["id"],
			"utype" : datas["etype"],
			"modelID" : datas["modelID"],
			"dialogID" : datas["dialogID"],
			"name" : datas["name"],
			"descr" : datas.get("descr", ''),
			"itemId" : itemId,
			"itemCount" : itemCount,
			"lucky" : 0,
			"arrt1" : arrt1,
			"arrt2" : arrt2,
			"arrt3" : arrt3,
			"arrt4" : arrt4,
			"arrt5" : arrt5,
			"belong" : killerID,
			"itemQ" : itemQ,
		}
		tempposition = copy.deepcopy(self.position)
		tempposition.x += random.randint(-3, 3)
		e = KBEngine.createEntity("DroppedItem", self.spaceID, tuple(tempposition), tuple(self.direction), params)
		
	#--------------------------------------------------------------------------------------------
	#                              Callbacks
	#--------------------------------------------------------------------------------------------
	def onTimer(self, tid, userArg):
		"""
		KBEngine method.
		引擎回调timer触发
		"""
		#DEBUG_MSG("%s::onTimer: %i, tid:%i, arg:%i" % (self.getScriptName(), self.id, tid, userArg))
		NPCObject.onTimer(self, tid, userArg)
		Spell.onTimer(self, tid, userArg)
		AI.onTimer(self, tid, userArg)


	def onWitnessed(self, isWitnessed):
		"""
		KBEngine method.
		此实体是否被观察者(player)观察到, 此接口主要是提供给服务器做一些性能方面的优化工作，
		在通常情况下，一些entity不被任何客户端所观察到的时候， 他们不需要做任何工作， 利用此接口
		可以在适当的时候激活或者停止这个entity的任意行为。
		@param isWitnessed	: 为false时， entity脱离了任何观察者的观察
		"""
		AI.onWitnessed(self, isWitnessed)
		
	def onForbidChanged_(self, forbid, isInc):
		"""
		virtual method.
		entity禁止 条件改变
		@param isInc		:	是否是增加
		"""
		State.onForbidChanged_(self, forbid, isInc)
		AI.onForbidChanged_(self, forbid, isInc)
		
	def onStateChanged_(self, oldstate, newstate):
		"""
		virtual method.
		entity状态改变了
		"""
		State.onStateChanged_(self, oldstate, newstate)
		AI.onStateChanged_(self, oldstate, newstate)
		NPCObject.onStateChanged_(self, oldstate, newstate)
		
	def onSubStateChanged_(self, oldSubState, newSubState):
		"""
		virtual method.
		子状态改变了
		"""
		State.onSubStateChanged_(self, oldSubState, newSubState)
		AI.onSubStateChanged_(self, oldSubState, newSubState)

	def onFlagsChanged_(self, flags, isInc):
		"""
		virtual method.
		"""
		Flags.onFlagsChanged_(self, flags, isInc)
		AI.onFlagsChanged_(self, flags, isInc)

	def onEnterTrap(self, entity, range_xz, range_y, controllerID, userarg):
		"""
		KBEngine method.
		引擎回调进入陷阱触发
		"""
		AI.onEnterTrap(self, entity, range_xz, range_y, controllerID, userarg)

	def onLeaveTrap(self, entity, range_xz, range_y, controllerID, userarg):
		"""
		KBEngine method.
		引擎回调离开陷阱触发
		"""
		AI.onLeaveTrap(self, entity, range_xz, range_y, controllerID, userarg)

	def onAddEnemy(self, entityID):
		"""
		virtual method.
		有敌人进入列表
		"""
		AI.onAddEnemy(self, entityID)
		Combat.onAddEnemy(self, entityID)

	def onRemoveEnemy(self, entityID):
		"""
		virtual method.
		删除敌人
		"""
		AI.onRemoveEnemy(self, entityID)
		Combat.onRemoveEnemy(self, entityID)

	def onEnemyEmpty(self):
		"""
		virtual method.
		敌人列表空了
		"""
		AI.onEnemyEmpty(self)
		Combat.onEnemyEmpty(self)

	def onDestroy(self):
		"""
		entity销毁
		"""
		NPCObject.onDestroy(self)
		Combat.onDestroy(self)

