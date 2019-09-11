# -*- coding: utf-8 -*-
import KBEngine
import random
import time
import GlobalDefine
from KBEDebug import * 
from skills.base.SkillInitiative import SkillInitiative

class SkillAttack(SkillInitiative):
	def __init__(self):
		SkillInitiative.__init__(self)

	def canUse(self, caster, scObject):
		"""
		virtual method.
		可否使用 
		@param caster: 使用技能者
		@param receiver: 受技能影响者
		"""
		return SkillInitiative.canUse(self, caster, scObject)
		
	def use(self, caster, scObject):
		"""
		virtual method.
		使用技能
		@param caster: 使用技能者
		@param receiver: 受技能影响者
		"""
		return SkillInitiative.use(self, caster, scObject)
		
	def receive(self, caster, receiver):
		"""
		virtual method.
		可以对受术者做一些事情了
		"""
		speed = 100;
		if caster.isPlayer() and receiver.isPlayer():
			nowh = int(time.strftime('%H', time.localtime(time.time())))
			if nowh < 8 or nowh > 22:
				return
		if caster.isPlayer():
			speed = caster.DC_SPEED
		if caster.isMonster():
			speed = caster.attspeed
		petdamage = 0
		petma = 0
		if caster.isPlayer() and caster.pet > 0 and receiver.isMonster() :
			petdamage = caster.get_petatt()
			petma = caster.get_petma()
			if random.randint(0, 100) <= petma and receiver.utype != 5:
				receiver.changeState(GlobalDefine.ENTITY_STATE_REST)

		attack = random.randint(caster.attack_Min, caster.attack_Max)
		if caster.isPlayer() and caster.LUCK > 8:
			attack = caster.attack_Max
		defence = receiver.defence
		tfdamage = 0
		skill5_crit = 0
		if self.getID() == 1:
			damage = attack - defence + 10
		elif self.getID() == 2:
			damage = attack - defence + 30
		elif self.getID() == 4:
			damage = attack - defence
		elif self.getID() == 5:
			damage =int((attack - defence) * (100 + (20 * caster.skill5_level) + caster.skill_power) / 100)
			skill5_crit = 20
		elif self.getID() == 6:
			damage = int(attack * (80 + (20 * caster.skill6_level) + caster.skill_power) / 100)

		if damage < 0:
			damage = 0

		damagetype = 0

		#世界BOSS
		if receiver.utype == 4:
			damage = 1

		#暴击
		if caster.isPlayer():
			if random.randint(0, 100) <= (caster.CRIT + skill5_crit) :
				damage = int(damage * (caster.CRITDAMAGE + 100) / 100)
				damagetype = 1
				if damage == 1:
					damage = 2

		#伤害减免
		if receiver.isPlayer():
			damage = int(damage * (100 - receiver.DAMAGE_DEC)/100)

		#天罚
		if damage > 0 and caster.isPlayer() :
			if receiver.isPlayer() is not True:
				if caster.tianfa_rate > 0:
					if random.randint(0, 100) <= caster.tianfa_rate:  # 概率是10caster.tianfa_rate
						tfdamage = caster.tianfa_power * caster.ZDL
		if receiver.utype == 5:
			tfdamage = 0
			petdamage = 0
		#世界BOSS
		if receiver.utype == 4:
			tfdamage = caster.tianfa_power
			petdamage = caster.get_petattworld()
			if caster.name in KBEngine.globalData["worldbosslist"].keys():
				KBEngine.globalData["worldbosslist"][caster.name] = [caster.base,caster.name,(KBEngine.globalData["worldbosslist"][caster.name][2] + tfdamage + petdamage + damage)]
			else:
				KBEngine.globalData["worldbosslist"][caster.name] = [caster.base, caster.name, (tfdamage + petdamage + damage)]


			KBEngine.globalData["worldbosslist2"] = []
			KBEngine.globalData["worldbosslist3"] = []
			templist = sorted(KBEngine.globalData["worldbosslist"].items(),key=lambda x:x[1][2], reverse=True)
			for i in range(len(templist)):
				if i > 9:
					break
				KBEngine.globalData["worldbosslist2"].append(templist[i][0])
				KBEngine.globalData["worldbosslist3"].append(templist[i][1][2])
			caster.client.set_worldlist(KBEngine.globalData["worldbosslist2"], KBEngine.globalData["worldbosslist3"])

		if receiver.HP % 100 == 0 and receiver.utype == 4:
			caster.base.sendChatMessage("snnui【世界BOSS正在被攻击！】")

		receiver.recvDamage(caster.id, self.getID(), damagetype, damage, tfdamage, petdamage, speed)
		if caster.isPlayer() and caster.attback > 0 and caster.HP < caster.HP_Max: #吸血，给自己加血
			caster.recvDamage(caster.id, self.getID(), 0, -int(caster.attback * caster.HP_Max / 20000), 0, 0, speed)