# -*- coding: utf-8 -*-
import KBEngine
import GlobalDefine
import random
import time
from KBEDebug import * 
from interfaces.CombatPropertys import CombatPropertys
import d_avatar_inittab

class Combat(CombatPropertys):
	"""
	关于战斗的一些功能
	"""
	def __init__(self):
		CombatPropertys.__init__(self)

	def weight_choice(self, weight):
		"""
		:param weight: list对应的权重序列
		:return:选取的值在原列表里的索引
		"""
		t = random.randint(0, sum(weight) - 1)
		for i, val in enumerate(weight):
			t -= val
			if t < 0:
				return i

	def canUpgrade(self):
		"""
		virtual method.
		"""
		return True
		
	def upgrade(self):
		"""
		for real
		"""
		if self.canUpgrade():
			self.addLevel(1)
			
	def addLevel(self, lv):
		"""
		for real
		"""
		self.level += lv
		self.onLevelChanged(lv)
		
	def isDead(self):
		"""
		"""
		return self.state == GlobalDefine.ENTITY_STATE_DEAD

	def isMa(self):
		"""
		"""
		return self.state == GlobalDefine.ENTITY_STATE_REST


	def canrelive_cd(self):
		if time.time() - self.relivetime < 60:
			return False
		else:
			return True

	def relivesuccess(self):
		self.client.relive_re(1)
		self.HP = self.HP_Max
		self.relivetime = time.time()

	def relivefaile(self):
		self.client.relive_re(2)
		self.relivetime = time.time()

	def relivefaile_cd(self):
		self.client.relive_re(3)

	def die(self, killerID):
		"""
		"""
		if self.isDestroyed or self.isDead():
			return
		
		if killerID == self.id:
			killerID = 0
			
		INFO_MSG("%s::die: %i i die. killerID:%i." % (self.getScriptName(), self.id, killerID))
		killer = KBEngine.entities.get(killerID)
		if killer:
			killer.onKiller(self.id)
		if self.isPlayer() and self.relive_p > 0:
			if self.canrelive_cd():
				if random.randint(0, 100) <= self.relive_p:
					self.relivesuccess()
					return
				else:
					self.relivefaile()
			else:
				self.relivefaile_cd()
		self.onBeforeDie(killerID)
		self.onDie(killerID)
		self.changeState(GlobalDefine.ENTITY_STATE_DEAD)
		self.onAfterDie(killerID)
		if self.isPlayer():
			if self.badpoint > 0:
				self.base.diedrop(self.badpoint)
			if killer.isMonster():
				self.base.sendChatMessage("snnui【"+self.name+"】在地图【" + self.getCurrSpace().name + "】被怪物轻松干掉了")
			if killer.isPlayer():
				self.base.sendChatMessage("snnui【"+ killer.name + "】在地图【" + self.getCurrSpace().name + "】将【"+ self.name+"】轻松干掉了")
				if self.badpoint == 0:
					killer.badpoint += 100
				self.power = 0
				self.adddamage_p(-20)
				self.base.updatePropertys()
		if self.isMonster():
			if killer.badpoint > 0:
				killer.badpoint -= 1
			if killer.badpoint < 0:
				killer.badpoint = 0
			if self.utype == 5:
				killer.base.addhalllevel(1)
				if self.mexp > 89:
					self.dropNotify(43, 30 , 0, 0, 0, 0, 0, 0, killerID)
					self.dropNotify(44, 25 , 0, 0, 0, 0, 0, 0, killerID)
					self.dropNotify(45, 20, 0, 0, 0, 0, 0, 0, killerID)
					self.dropNotify(46, 20, 0, 0, 0, 0, 0, 0, killerID)
					self.dropNotify(47, 2, 0, 0, 0, 0, 0, 0, killerID)
				elif self.mexp > 59:
					self.dropNotify(43, 20 , 0, 0, 0, 0, 0, 0, killerID)
					self.dropNotify(44, 15 , 0, 0, 0, 0, 0, 0, killerID)
					self.dropNotify(45, 10, 0, 0, 0, 0, 0, 0, killerID)
					self.dropNotify(46, 10, 0, 0, 0, 0, 0, 0, killerID)
					self.dropNotify(47, 1, 0, 0, 0, 0, 0, 0, killerID)
				elif self.mexp > 39:
					self.dropNotify(43, 15, 0, 0, 0, 0, 0, 0, killerID)
					self.dropNotify(44, 10 , 0, 0, 0, 0, 0, 0, killerID)
					self.dropNotify(45, 5, 0, 0, 0, 0, 0, 0, killerID)
					self.dropNotify(46, 5, 0, 0, 0, 0, 0, 0, killerID)
					self.dropNotify(47, 1, 0, 0, 0, 0, 0, 0, killerID)
				elif self.mexp > 9:
					self.dropNotify(43, 8, 0, 0, 0, 0, 0, 0, killerID)
					self.dropNotify(44, 5, 0, 0, 0, 0, 0, 0, killerID)
					self.dropNotify(46, 3, 0, 0, 0, 0, 0, 0, killerID)
				else:
					self.dropNotify(43, 5, 0, 0, 0, 0, 0, 0, killerID)
					self.dropNotify(46, 2, 0, 0, 0, 0, 0, 0, killerID)
			if self.utype == 4:
				self.worldbossdead()
				KBEngine.globalData["worldboss"] = 0
				killer.base.sendChatMessage("snnui【世界BOSS被击杀！】")
			if killer.isPlayer() :
				if self.utype == 1 and killer.jingli <= 0:
					killer.client.errorInfo("精力不足，无任何奖励！", 1)
					return
				if self.utype == 1 and killer.jingli > 0:
					killer.client.errorInfo("精力-1", 1)
					killer.addjingli(-1)
				if self.utype != 1 :
					killer.client.errorInfo("精力+3", 1)
					killer.addjingli(3)
			self.getdropitem(killer, killerID)
			mexp = self.getMonsterExp() * (1 + (killer.xzexe / 100))
			if mexp is None:
				return
			if killer.viplevel > 0:
				mexp = int(mexp * (1 + (killer.viplevel * 0.5)))
			killer.addEXP(mexp)
			killer.client.errorInfo("经验增加%i" % mexp, 1)

	def worldbossdead(self):
		for i in range(len(KBEngine.globalData["worldbosslist2"])):
			KBEngine.globalData["worldbosslist"][KBEngine.globalData["worldbosslist2"][i]][0].giveitem(46, ((15 - i) * (15 - i)))
			KBEngine.globalData["worldbosslist"][KBEngine.globalData["worldbosslist2"][i]][0].giveitem(47, (11 - i))
			del KBEngine.globalData["worldbosslist"][KBEngine.globalData["worldbosslist2"][i]]
		KBEngine.globalData["worldbosslist2"] = []
		KBEngine.globalData["worldbosslist3"] = []
		for key,value in KBEngine.globalData["worldbosslist"].items():
			value[0].giveitem(46, 10)
		KBEngine.globalData["worldbosslist"] = {}
	
	def canDie(self, attackerID, skillID, damageType, damage):
		"""
		virtual method.
		是否可死亡
		"""
		return True
		
	def recvDamage(self, attackerID, skillID, damageType, damage, tfdamage, petdamage, speed):
		"""
		defined.
		"""
		damageall = int(damage) + int(tfdamage) + int(petdamage)

		if self.isDestroyed or self.isDead():
			return
		
		self.addEnemy(attackerID, damageall)

		#DEBUG_MSG("%s::recvDamage: %i attackerID=%i, skillID=%i, damageType=%i, damage=%i" % \	(self.getScriptName(), self.id, attackerID, skillID, damageType, damage))
			
		if self.HP <= damageall:
			if self.canDie(attackerID, skillID, damageType, damageall):
				self.die(attackerID)
		else:
			self.setHP(self.HP - damageall)

		self.allClients.recvDamage(attackerID, skillID, damageType, damage, tfdamage, petdamage, speed)
		
	def addEnemy(self, entityID, enmity):
		"""
		defined.
		添加敌人
		"""
		if entityID in self.enemyLog:
			return

		DEBUG_MSG("%s::addEnemy: %i entity=%i, enmity=%i" % \
						(self.getScriptName(), self.id, entityID, enmity))
		
		self.enemyLog.append(entityID)
		self.onAddEnemy(entityID)
		
	def removeEnemy(self, entityID):
		"""
		defined.
		删除敌人
		"""
		DEBUG_MSG("%s::removeEnemy: %i entity=%i" % \
						(self.getScriptName(), self.id, entityID))
		
		self.enemyLog.remove(entityID)
		self.onRemoveEnemy(entityID)
	
		if len(self.enemyLog) == 0:
			self.onEnemyEmpty()

	def checkInTerritory(self):
		"""
		virtual method.
		检查自己是否在可活动领地中
		"""
		return True

	def checkEnemyDist(self, entity):
		"""
		virtual method.
		检查敌人距离
		"""
		#dist = entity.position.distTo(self.position)
		dist = abs(entity.position.x - self.position.x)
		if dist > 10.0:
			INFO_MSG("%s::checkEnemyDist: %i id=%i, dist=%f." % (self.getScriptName(), self.id, entity.id, dist))
			return False
		
		return True
		
	def checkEnemys(self):
		"""
		检查敌人列表
		"""
		for idx in range(len(self.enemyLog) - 1, -1, -1):
			entity = KBEngine.entities.get(self.enemyLog[idx])
			if entity is None or entity.isDestroyed or entity.isDead() or \
				not self.checkInTerritory() or not self.checkEnemyDist(entity):
				self.removeEnemy(self.enemyLog[idx])

	#--------------------------------------------------------------------------------------------
	#                              Callbacks
	#--------------------------------------------------------------------------------------------
	def onLevelChanged(self, addlv):
		"""
		virtual method.
		self.strength = d_avatar_inittab.datas[self.roleTypeCell]["strength"] + 1*self.level
		"""
		props = self.getLvPops()
		if props is None:
			return

		self.exp_max = props.get("exp", 10000000000)
		self.HP = self.HP_Max
		self.MP = 100
		self.MP_Max = 100
		self.base.updatePropertys()
		pass
		
	def onDie(self, killerID):
		"""
		virtual method.
				if self.isPlayer() and self.level > 1:
			self.level -= 1
			self.onLevelChanged(self.level)
		"""
		self.setHP(0)
		self.setMP(0)

	def onBeforeDie(self, killerID):
		"""
		virtual method.
		"""
		pass

	def onAfterDie(self, killerID):
		"""
		virtual method.
		"""
		pass
	
	def onKiller(self, entityID):
		"""
		defined.
		我击杀了entity
		"""
		pass
		
	def onDestroy(self):
		"""
		entity销毁
		"""
		pass
		
	def onAddEnemy(self, entityID):
		"""
		virtual method.
		有敌人进入列表
		"""
		pass

	def onRemoveEnemy(self, entityID):
		"""
		virtual method.
		删除敌人
		"""
		pass

	def onEnemyEmpty(self):
		"""
		virtual method.
		敌人列表空了
		"""
		pass
	