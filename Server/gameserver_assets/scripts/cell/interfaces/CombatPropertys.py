# -*- coding: utf-8 -*-
import KBEngine
import GlobalDefine
from KBEDebug import * 

class CombatPropertys:
    """
    所有关于战斗的属性
    完善的话可以根据策划excel表来直接生成这个模块
    """
    def __init__(self):
        #self.HP_Max = 100
        #self.MP_Max = 100

        # 非死亡状态才需要补满
        if not self.isState(GlobalDefine.ENTITY_STATE_DEAD) and self.HP == 0 and self.HP_Max != 0:
            self.fullPower()

    def fullPower(self):
        """
        """
        self.setHP(self.HP_Max)
        self.setMP(self.MP_Max)

    def autohp(self):
        """
        defined.自动回复HP
        """
        if self.isState(GlobalDefine.ENTITY_STATE_DEAD):
            return
        rate = 0.3
        if self.viplevel > 0:
            rate = rate + (0.1 * self.viplevel)
        self.client.autohp_re(int(rate * 100))
        v = self.HP + int(self.HP_Max * rate)
        if v < 0:
            v = 0
        if v > self.HP_Max:
            v = self.HP_Max

        if self.HP != v:
            self.HP = v

        vm = self.MP + 50
        if vm < 0:
            vm = 0
        if vm > self.MP_Max:
            vm = self.MP_Max
        if self.MP == vm:
            return
        self.MP = vm

    def addHP(self, val):
        """
        defined.
        """
        v = self.HP + int(val)
        if v < 0:
            v = 0
        if v > self.HP_Max:
            v = self.HP_Max

        if self.HP == v:
            return

        self.HP = v

    def addMP(self, val):
        """
        defined.
        """
        v = self.MP + int(val)
        if v < 0:
            v = 0
        if v > self.MP_Max:
            v = self.MP_Max

        if self.MP == v:
            return

        self.MP = v

    def addEXP(self, val):
        """
        defined.
                    if killer.exp > killer.level*5+20:
                killer.upgrade()
        """
        v = self.exp + int(val)
        if v < 0:
            v = 0

        upper_exp = self.getUpperExp()
        if upper_exp is None:
            return

        list_exp = list(upper_exp.values())
        lv_max = list(upper_exp.keys())[-1]

        lv = self.level
        #DEBUG_MSG("CombatPropertys::addEXP: lv:%i,lv_max:%i,list_exp:%s" % (lv, lv_max, str(list_exp)))

        for exp in list_exp:
            if v - int(exp) >= 0:
                if lv >= lv_max:
                    lv = lv_max
                    v = int(exp)
                else:
                    lv += 1
                    v -= int(exp)

        if lv > self.level:
            self.addLevel(lv - self.level)

        self.exp = v

        DEBUG_MSG("CombatPropertys::addEXP: EXP:%i,level:%i" % (self.exp, self.level))

    def addDefence(self, val):
        v = self.defence + int(val)
        if v < 0:
            v = 0

        if self.defence == v:
            return
        self.defence = v

    def addHPmax(self, val):
        v = self.HP_Max + int(val)
        if v < 0:
            v = 0

        if self.HP_Max == v:
            return
        self.HP_Max = v

    def addAttack_Max(self, val):
        v = self.attack_Max + int(val)
        if v < 0:
            v = 0

        if self.attack_Max == v:
            return
        self.attack_Max = v

    def addAttack_Min(self, val):
        v = self.attack_Min + int(val)
        if v < 0:
            v = 0

        if self.attack_Min == v:
            return
        self.attack_Min = v

    def adddamage_p(self, val):
        v = self.DAMAGE_P + int(val)
        if v < 0:
            v = 0

        if self.DAMAGE_P == v:
            return
        self.DAMAGE_P = v

    def addarrts(self, lucky, arrt1, arrt2, arrt3, arrt4, arrt5):
        v1 = self.LUCK + int(lucky)
        v2 = self.CRIT + int(arrt1)
        v3 = self.CRITDAMAGE + int(arrt2)
        v4 = self.DAMAGE_P + int(arrt3)
        v5 = self.HP_P + int(arrt4)
        v6 = self.DAMAGE_DEC + int(arrt5)
        if v1 < 0:
            v1 = 0
        if v2 < 0:
            v2 = 0
        if v3 < 0:
            v3 = 0
        if v4 < 0:
            v4 = 0
        if v5 < 0:
            v5 = 0
        if v6 < 0:
            v6 = 0
        if self.LUCK != v1:
            self.LUCK = v1
        if self.LUCK > 12:
            self.LUCK = 12
        if self.CRIT != v2:
            self.CRIT = v2
        if self.CRITDAMAGE != v3:
            self.CRITDAMAGE = v3
        if self.DAMAGE_P != v4:
            self.DAMAGE_P = v4
        if self.HP_P != v5:
            self.HP_P = v5
        if self.DAMAGE_DEC != v6:
            self.DAMAGE_DEC = v6

    def changespeed(self, val):
        v = 100 - int(val)
        v -=  round(self.xz_level5 * 0.1)
        if v > 100:
            v = 100
        if v < 50:
            v = 50
        if self.DC_SPEED == v:
            return
        self.DC_SPEED = v

    def changeskill_p(self, val):
        v = int(val)
        if v < 0:
            v = 0
        if self.skill_power == v:
            return
        self.skill_power = v

    def changerelive_p(self, val):
        v = int(val)
        if v > 100:
            v = 100
        if self.relive_p == v:
            return
        self.relive_p = v

    def setzdl(self):
        power_zdl = 0
        if self.power == 1:
            power_zdl = 20000
        if self.LUCK > 7:
            self.CRIT += (self.LUCK - 7)
        self.ZDL = int(((self.attack_Max + self.attack_Min + self.defence) / 3) * ((100 + self.LUCK + self.CRIT + self.CRITDAMAGE + self.DAMAGE_P + self.HP_P + self.DAMAGE_DEC)/100)) + (self.level * 300) + (self.attback * 100) + power_zdl
        self.attack_Min = int((self.DAMAGE_P + 100) / 100 * self.attack_Min)
        self.attack_Max = int((self.DAMAGE_P + 100) / 100 * self.attack_Max)
        self.HP = self.HP
        self.HP_Max = int(self.HP_Max * (100 + self.HP_P) / 100) + self.HP_ADD
        # 非死亡状态才需要补满
        if not self.isState(GlobalDefine.ENTITY_STATE_DEAD) and self.HP == 0 and self.HP_Max != 0:
            self.fullPower()


    def setHP(self, hp):
        """
        defined
        """
        hp = int(hp)
        if hp < 0:
            hp = 0
        if hp > self.HP_Max:
            hp = self.HP_Max

        if self.HP == hp:
            return

        self.HP = hp

    def setMP(self, mp):
        """
        defined
        """
        hp = int(mp)
        if mp < 0:
            mp = 0
        if mp > self.MP_Max:
            mp = self.MP_Max
        if self.MP == mp:
            return

        self.MP = mp

    def setHPMax(self, hpmax):
        """
        defined
        """
        hpmax = int(hpmax)
        self.HP_Max = hpmax

    def setMPMax(self, mpmax):
        """
        defined
        """
        mpmax = int(mpmax)
        self.MP_Max = mpmax


