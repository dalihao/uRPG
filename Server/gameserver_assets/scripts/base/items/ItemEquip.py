# -*- coding: utf-8 -*-
import KBEngine
import GlobalConst
from KBEDebug import *
from items.base.ItemBase import ItemBase


class ItemEquip(ItemBase):
    def __init__(self):
        ItemBase.__init__(self)

    def loadFromDict(self, dictDatas):
        """
		virtual method.
		从字典中创建这个对象
		"""
        ItemBase.loadFromDict(self, dictDatas)

        self.defence = dictDatas.get('defence', 0)
        self.attack_Max = dictDatas.get("attack_Max", 0)
        self.attack_Min = dictDatas.get("attack_Min", 0)
        self.need = dictDatas.get("need", 0)
        self.HP = dictDatas.get("HP", 0)
        # sellprice
        self.type = dictDatas.get("type", 0)
        self.price = dictDatas.get("price", 0)
        self.attspeed_p = dictDatas.get("attspeed_p", 0)
        self.skill_p = dictDatas.get("skill_p", 0)
        self.relive_p = dictDatas.get("relive_p", 0)

    def canUse(self, user):
        return GlobalConst.GC_OK

    def getrate(self, index):
        if index == 0:
            return 1
        if index == 1:
            return 1.1
        if index == 2:
            return 1.2
        if index == 3:
            return 1.3
        if index == 4:
            return 1.4
        if index == 5:
            return 1.5
        if index == 6:
            return 1.7
        if index == 7:
            return 1.9
        if index == 8:
            return 2.1
        if index == 9:
            return 2.3
        if index == 10:
            return 2.5
        if index == 11:
            return 2.8
        if index == 12:
            return 3.2
        if index == 13:
            return 3.7
        if index == 14:
            return 4.3
        if index == 15:
            return 5.1

    # 计算装备信息 4左5右 6 左 7 右
    def use(self, user, index):
        if self.defence > 0:
            xdef = self.defence
            if self.type == 10:
                xdef = self.getrate(user.ups[0]) * self.defence
            if self.type == 11:
                xdef = self.getrate(user.ups[1]) * self.defence
            if self.type == 12:
                xdef = self.getrate(user.ups[2]) * self.defence
            if self.type == 13:
                xdef = self.getrate(user.ups[3]) * self.defence
            if self.type == 17:
                xdef = self.getrate(user.ups[4]) * self.defence
            if self.type == 16:
                xdef = self.getrate(user.ups[5]) * self.defence
            if self.type == 14 and index == 4:
                xdef = self.getrate(user.ups[6]) * self.defence
            if self.type == 14 and index == 5:
                xdef = self.getrate(user.ups[7]) * self.defence
            if self.type == 15 and index == 6:
                xdef = self.getrate(user.ups[8]) * self.defence
            if self.type == 15 and index == 7:
                xdef = self.getrate(user.ups[9]) * self.defence
            user.cell.addDefence(int(xdef))

        if self.HP > 0:
            xhp = self.HP
            if self.type == 10:
                xhp = self.getrate(user.ups[0]) * self.HP
            if self.type == 11:
                xhp = self.getrate(user.ups[1]) * self.HP
            if self.type == 12:
                xhp = self.getrate(user.ups[2]) * self.HP
            if self.type == 13:
                xhp = self.getrate(user.ups[3]) * self.HP
            if self.type == 17:
                xhp = self.getrate(user.ups[4]) * self.HP
            if self.type == 16:
                xhp = self.getrate(user.ups[5]) * self.HP
            if self.type == 14 and index == 4:
                xhp = self.getrate(user.ups[6]) * self.HP
            if self.type == 14 and index == 5:
                xhp = self.getrate(user.ups[7]) * self.HP
            if self.type == 15 and index == 6:
                xhp = self.getrate(user.ups[8]) * self.HP
            if self.type == 15 and index == 7:
                xhp = self.getrate(user.ups[9]) * self.HP
            user.cell.addHPmax(int(xhp))

        if self.attack_Max > 0:
            xattack_Max = self.attack_Max
            if self.type == 10:
                xattack_Max = self.getrate(user.ups[0]) * self.attack_Max
            if self.type == 11:
                xattack_Max = self.getrate(user.ups[1]) * self.attack_Max
            if self.type == 12:
                xattack_Max = self.getrate(user.ups[2]) * self.attack_Max
            if self.type == 13:
                xattack_Max = self.getrate(user.ups[3]) * self.attack_Max
            if self.type == 17:
                xattack_Max = self.getrate(user.ups[4]) * self.attack_Max
            if self.type == 16:
                xattack_Max = self.getrate(user.ups[5]) * self.attack_Max
            if self.type == 14 and index == 4:
                xattack_Max = self.getrate(user.ups[6]) * self.attack_Max
            if self.type == 14 and index == 5:
                xattack_Max = self.getrate(user.ups[7]) * self.attack_Max
            if self.type == 15 and index == 6:
                xattack_Max = self.getrate(user.ups[8]) * self.attack_Max
            if self.type == 15 and index == 7:
                xattack_Max = self.getrate(user.ups[9]) * self.attack_Max
            user.cell.addAttack_Max(int(xattack_Max))
        if self.attack_Min > 0:
            user.cell.addAttack_Min(self.attack_Min)

        if self.type == 20:
            user.cell.changespeed(self.attspeed_p)
        if self.type == 22:
            user.cell.changeskill_p(self.skill_p)
        if self.type == 21:
            user.cell.changerelive_p(self.relive_p)
        return GlobalConst.GC_OK

    def sellself(self, user):
        price = int(self.price * (1  + (user.xzsell / 100 )))
        if user.viplevel > 0:
            price = int(price * (1 + (0.1 * user.viplevel)))
        user.GAMEGOLD += price
        return price

    def gettype(self, user):
        return self.type

    def checkneed(self):
        return self.need

