# -*- coding: utf-8 -*-
import KBEngine
import random
import time
import GlobalConst
from KBEDebug import * 
from items.base.ItemBase import ItemBase

class ItemConsume(ItemBase):
	def __init__(self):
		ItemBase.__init__(self)

	def loadFromDict(self, dictDatas):
		"""
		virtual method.
		从字典中创建这个对象
		"""
		ItemBase.loadFromDict(self, dictDatas)
		
		# 加血
		self.hp = dictDatas.get('hp', 0)
		
		# 加魔法
		self.mp = dictDatas.get("mp", 0)

		self.type = dictDatas.get("type", 0)
		self.id = dictDatas.get("id", 0)
		
		# cd
		self.limitCD = dictDatas.get("limitCD", 1)

		# sellprice
		self.price = dictDatas.get("price", 1)
		
	def getHp(self):
		return self.hp

	def getMp(self):
		return self.mp

	def canUse(self, user):
		return GlobalConst.GC_OK

	def checkneed(self):
		return -1

	def use(self, user, itemUUId, itemCount):
		#药品
		if self.type == 2:
			if self.hp > 0:
				user.cell.addHP(self.hp)
			if self.mp > 0:
				user.cell.addMP(self.mp)
			return GlobalConst.GC_OK

		#宠物
		if self.type == 3:
			for i in range(1, 11) :
				if user.pets[i * 4 - 4] == 0:
					temprate = random.randint(0, 1000)
					user.pets[i * 4 - 4] = 1
					if temprate == 1:
						user.pets[i * 4 - 4] = 6
					if temprate > 1 and temprate < 4:
						user.pets[i * 4 - 4] = 5
					if temprate > 3 and temprate < 7:
						user.pets[i * 4 - 4] = 4
					if temprate > 6 and temprate < 13:
						user.pets[i * 4 - 4] = 3
					if temprate > 12 and temprate < 22:
						user.pets[i * 4 - 4] = 2
					user.pets[i * 4 - 1] = int(time.time())
					user.pets = user.pets
					return GlobalConst.GC_OK
			user.client.errorInfo("宠物空间不足！", 1)

		#门票
		if self.type == 4:
			if self.id == 33:  #神庙圣物
				user.ticket1 += itemCount
			if self.id == 32:  #亚特兰蒂斯之心
				user.ticket2 += itemCount
			itemId = user.inventory.removeItem(itemUUId, itemCount)
			if itemId == -1:  # 只是减少物品数量，并没有销毁
				user.client.pickUp_re(user.itemList[itemUUId])
			else:  # 销毁物品
				user.client.dropItem_re(itemId, itemUUId)

		#材料
		if self.type == 6:
			if self.id == 34:  #星宫之书
				user.xz_book += itemCount
			#  35	1 - 5     36	6 - 10    37  11 - 15 	  38  16 - 20   39	  21 - 25
			if self.id == 35:
				user.zs1_item += itemCount
			if self.id == 36:
				user.zs2_item += itemCount
			if self.id == 37:
				user.zs3_item += itemCount
			if self.id == 38:
				user.zs4_item += itemCount
			if self.id == 39:
				user.zs5_item += itemCount
			itemId = user.inventory.removeItem(itemUUId, itemCount)
			if itemId == -1:  # 只是减少物品数量，并没有销毁
				user.client.pickUp_re(user.itemList[itemUUId])
			else:  # 销毁物品
				user.client.dropItem_re(itemId, itemUUId)

		#要塞
		if self.type == 8:
			if self.id == 43:  #茅草
				user.ys1 += itemCount
			if self.id == 44:  #木头
				user.ys2 += itemCount
			if self.id == 45:  #石块
				user.ys3 += itemCount
			itemId = user.inventory.removeItem(itemUUId, itemCount)
			if itemId == -1:  # 只是减少物品数量，并没有销毁
				user.client.pickUp_re(user.itemList[itemUUId])
			else:  # 销毁物品
				user.client.dropItem_re(itemId, itemUUId)

		#神器
		if self.type == 5:
			if self.id > 1 and self.id < 17:
				lid = self.id - 2
				if user.lengends[lid] == 0:
					user.lengends[lid] = 1
					user.lengends = user.lengends
					return GlobalConst.GC_OK
				user.client.errorInfo("已经拥有此神器！", 2)
			if self.id > 16 and self.id < 32:
				sid = self.id - 17
				if user.shields[sid] == 0:
					user.shields[sid] = 1
					user.shields = user.shields
					return GlobalConst.GC_OK
				user.client.errorInfo("已经拥有此神器！", 2)

		# 魔法盾
		if self.type == 7:
			if user.skill7b_level != 1:
				user.skill7b_level = 1
				user.cell.skill_update(7)
				return GlobalConst.GC_OK
			user.client.errorInfo("已经学习过此技能！", 2)



