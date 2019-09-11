# -*- coding: utf-8 -*-
import KBEngine
import GlobalDefine
import d_entities
import SCDefine
import d_spaces
import random
import time
import copy
from KBEDebug import *
from interfaces.GameObject import GameObject
from interfaces.Combat import Combat
from interfaces.Spell import Spell
from interfaces.Teleport import Teleport
from interfaces.Dialog import Dialog
from interfaces.State import State
from interfaces.Motion import Motion
from interfaces.SkillBox import SkillBox

class Avatar(KBEngine.Entity,
                GameObject,
                State,
                Motion,
                SkillBox,
                Combat,
                Spell,
                Teleport,
                Dialog):
    def __init__(self):
        KBEngine.Entity.__init__(self)
        GameObject.__init__(self)
        State.__init__(self)
        Motion.__init__(self)
        SkillBox.__init__(self)
        Spell.__init__(self)
        Teleport.__init__(self)
        Dialog.__init__(self)
        #self.resetPropertys()
        Combat.__init__(self)
        #self.base.updatePropertys()
        self.xzexe = 0
        self.viplevel = 0
        # 设置每秒允许的最快速度, 超速会被拉回去
        self.topSpeed = 0
        self.topSpeedY = 0
        self.skill_time = int(round(time.time() * 1000))
        self.skill5_time = time.time()
        self.skill6_time = time.time()
        self.relivetime = time.time()
        self.client.relive_re(4)
        self.client.autohp_re(0)
        self.addTimer(30, 30, SCDefine.TIMER_TYPE_ADDHP)
        self.gateingentity = None


    def setviplevel(self, level):
        self.viplevel = level

    def isPlayer(self):
        """
        virtual method.
        """
        return True

    def dropNotify(self, itemId, UUid, itemCount, lucky, arrt1, arrt2, arrt3, arrt4, arrt5, itemfrom):
        datas = d_entities.datas.get(40001003)

        if datas is None:
            ERROR_MSG("SpawnPoint::spawn:%i not found." % 40001003)
            return
        itemQ = 0
        if itemId < 32:  # 宠物和神器
            itemQ = 5
        if 31 < itemId < 100:  # 材料、门票
            itemQ = 2
        if 117 < itemId < 130:
            itemQ = 1
        if 141 < itemId < 153:
            itemQ = 4
        if 129 < itemId < 142:
            itemQ = 3
        if 187 < itemId < 208:
            itemQ = 4
        if 178 < itemId < 188:
            itemQ = 3
        if 251 < itemId < 263:
            itemQ = 4
        if 233 < itemId < 252:
            itemQ = 3
        if 306 < itemId < 318:
            itemQ = 4
        if 288 < itemId < 307:
            itemQ = 3
        if 361 < itemId < 373:
            itemQ = 4
        if 343 < itemId < 362:
            itemQ = 3
        if 412 < itemId < 424:
            itemQ = 4
        if 398 < itemId < 413:
            itemQ = 3
        if 467 < itemId < 479:
            itemQ = 4
        if 449 < itemId < 468:
            itemQ = 3
        if 520 < itemId < 530:
            itemQ = 4
        if 504 < itemId < 521:
            itemQ = 3
        if 573 < itemId < 585:
            itemQ = 4
        if 559 < itemId < 574:
            itemQ = 3
        if 637 < itemId < 640:
            itemQ = 4
        if 614 < itemId < 638:
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
            "lucky" : lucky,
            "arrt1" : arrt1,
            "arrt2" : arrt2,
            "arrt3" : arrt3,
            "arrt4" : arrt4,
            "arrt5" : arrt5,
            "belong" : 0,
            "itemQ" : itemQ,
        }
        tempposition = copy.deepcopy(self.position)
        tempposition.x += random.randint(-3, 3)
        e = KBEngine.createEntity("DroppedItem", self.spaceID, tuple(tempposition), tuple(self.direction), params)

        if itemfrom == 1:
            self.client.dropItem_re(itemId, UUid)
        if itemfrom == 0:
            self.client.dropeqItem_re(itemId, UUid)




    def returnzs_level(self, needlevel, itemIndex, equipIndex1, equipIndex2):
        if self.zs_level >= needlevel:
            self.base.equipItemRequestok(itemIndex, equipIndex1, equipIndex2)
        else:
            self.client.errorInfo("转生等级不够！", 1)

    def resetPropertys(self, lengends, shields):
        hp_MAX = 0
        a_MAX = 0
        CRIT = 0

        if self.TITLE == 1:
            a_Min = 100
            a_MAX = 200
            hp_MAX = 5000
        if self.TITLE == 2:
            a_Min = 200
            a_MAX = 500
            hp_MAX = 10000
        if self.TITLE == 3:
            a_Min = 250
            a_MAX = 700
            hp_MAX = 25000
        if self.TITLE == 4:
            a_Min = 300
            a_MAX = 1000
            hp_MAX = 40000
        if self.TITLE == 5:
            a_Min = 400
            a_MAX = 1500
            hp_MAX = 50000
        if self.TITLE == 6:
            a_Min = 500
            a_MAX = 2000
            hp_MAX = 80000
        if self.TITLE == 7:
            a_Min = 500
            a_MAX = 2500
            hp_MAX = 100000
        if self.TITLE == 8:
            a_Min = 500
            a_MAX = 3000
            hp_MAX = 120000
        if self.TITLE == 9:
            a_Min = 500
            a_MAX = 4000
            hp_MAX = 150000
        if self.TITLE == 10:
            a_Min = 800
            a_MAX = 6000
            hp_MAX = 250000
        if self.TITLE == 11:
            a_Min = 1000
            a_MAX = 10000
            hp_MAX = 300000
        if self.TITLE == 12:
            a_Min = 1000
            a_MAX = 12000
            hp_MAX = 400000
        if self.TITLE == 13:
            a_Min = 2000
            a_MAX = 15000
            hp_MAX = 500000
        if self.TITLE == 14:
            a_Min = 2000
            a_MAX = 25000
            hp_MAX = 600000
        if self.TITLE == 15:
            a_Min = 3000
            a_MAX = 35000
            hp_MAX = 700000
        if self.TITLE == 16:
            a_Min = 5000
            a_MAX = 50000
            hp_MAX = 800000
        if self.TITLE == 17:
            a_Min = 6000
            a_MAX = 80000
            hp_MAX = 1000000
        if self.TITLE == 18:
            a_Min = 10000
            a_MAX = 100000
            hp_MAX = 1500000

        self.attack_Min = 0 + a_Min
        a_MAX += 10
        defence = 0
        self.LUCK = 0
        CRITDAMAGE = 0
        DAMAGE_P = self.zs_level * 2
        if self.power == 1:
            DAMAGE_P  += 20
        DAMAGE_DEC = 0
        if self.skill7_level == 1:
            DAMAGE_DEC = 25
        HP_P = self.zs_level * 5
        hp_MAX  += self.level*1000
        #lengends, shields
        for i, val in enumerate(lengends):
            if val == 1:
                a_MAX += (i + 1) * 150
        for i, val in enumerate(shields):
            if val == 1:
                defence += (i + 1) * 100
                hp_MAX += (i + 1) * 2500

        a_MAX += (self.lengend + 1) * 3000
        defence += (self.shield + 1) * 2000
        hp_MAX += (self.shield + 1) * 50000


        if self.lengend == self.shield and self.lengend > -1:
            lengendlevel = self.lengend + 1
            DAMAGE_P += lengendlevel * 3
            CRIT += lengendlevel
            CRITDAMAGE += lengendlevel * 5
            HP_P += lengendlevel * 3
            DAMAGE_DEC += lengendlevel

        a_MAX += self.xz_level1 * 300
        hp_MAX += self.xz_level2 * 10000
        defence += self.xz_level3 * 200
        HP_P += round(self.xz_level4 * 0.5)

        CRIT += round(self.xz_level6 * 0.10)
        CRITDAMAGE += round(self.xz_level7)
        DAMAGE_P += round(self.xz_level8 * 0.3)
        self.xzexe = self.xz_level10 * 0.5
        self.skill_power += round(self.xz_level12 * 0.5)
        self.defence = defence
        self.attack_Max = a_MAX
        self.HP_Max = hp_MAX
        self.CRIT = CRIT
        self.DAMAGE_P = DAMAGE_P
        self.CRITDAMAGE = CRITDAMAGE
        self.DAMAGE_DEC = DAMAGE_DEC
        self.HP_P = HP_P
        self.base.setxzsell(self.xz_level11)

    def equipNotify(self, itemId):
        self.equipWeapon = itemId

    def addoffexp(self, exp):
        self.addEXP(exp)

    #开启狂暴之力
    def poweropen(self):
        self.power = 1
        self.adddamage_p(20)
        self.base.updatePropertys()

    #开始转生
    def zs_up(self):
        self.client.errorInfo("转生成功！", 2)
        self.zs_level += 1
        self.base.updatePropertys()

    def getzs_level(self, id):
        if id == -1:
            self.base.zs_up_start(self.zs_level, self.level)
        if id > -1:
            self.base.startjumpto(self.zs_level, id)

    def get_title(self):
        self.base.title_up_start(self.TITLE)

    def title_up(self):
        self.client.errorInfo("升级称号成功！", 2)
        self.TITLE += 1
        self.base.updatePropertys()

    def get_xz(self, index):
        self.base.xz_up_start(self.xz_level1, self.xz_level2, self.xz_level3, self.xz_level4, self.xz_level5, self.xz_level6, self.xz_level7, self.xz_level8, self.xz_level9, self.xz_level10, self.xz_level11, self.xz_level12, index)

    def xz_up(self, who):
        if who == 1:
            self.xz_level1 += 1
        if who == 2:
            self.xz_level2 += 1
        if who == 3:
            self.xz_level3 += 1
        if who == 4:
            self.xz_level4 += 1
        if who == 5:
            self.xz_level5 += 1
        if who == 6:
            self.xz_level6 += 1
        if who == 7:
            self.xz_level7 += 1
        if who == 8:
            self.xz_level8 += 1
        if who == 9:
            self.xz_level9 += 1
        if who == 10:
            self.xz_level10 += 1
        if who == 11:
            self.xz_level11 += 1
        if who == 12:
            self.xz_level12 += 1

        allnum = self.xz_level1 + self.xz_level2 + self.xz_level3 + self.xz_level4 + self.xz_level5 + self.xz_level6 + self.xz_level7 + self.xz_level8 + self.xz_level9 + self.xz_level10 + self.xz_level11 + self.xz_level12
        self.attback = allnum

    def get_skill(self, v):
        if v == 5:
            self.base.skill_update_start(5, self.skill5_level)
        if v == 6:
            self.base.skill_update_start(6, self.skill6_level)

    def skill_update(self, v):
        if v == 5:
            self.skill5_level += 1
        if v == 6:
            self.skill6_level += 1
        if v == 7:
            self.skill7_level = 1

    def addjingli(self, v):
        if v == 0:
            self.jingli = 200
            return
        else:
            if self.jingli + v < 0:
                self.jingli = 0
            elif self.jingli + v > 999:
                self.jingli = 1000
            else:
                self.jingli += v;



    def set_lengend(self, id):
        self.lengend = id
        self.base.updatePropertys()

    def set_shield(self, id):
        self.shield = id
        self.base.updatePropertys()

    def get_tianfa(self, type):
        self.base.tianfa_up_start(type, self.tianfa_power)
        pass

    def tianfa_update(self):
        self.tianfa_power += 1
        pass

    def pet_fight(self, index):
        self.pet = index
        pass

    #取宠物攻击
    def get_petatt(self):
        petid = int(list(str(self.pet))[0])
        petlevel = int(list(str(self.pet))[1])
        attr = 0
        if petid == 1:
            attr = 10000 + (petlevel * 10000)
        if petid == 2:
            attr = 100000 + (petlevel * 100000)
        if petid == 3:
            attr = 300000 + (petlevel * 300000)
        if petid == 4:
            attr = 500000 + (petlevel * 500000)
        if petid == 5:
            attr = 1000000 + (petlevel * 1000000)
        if petid == 6:
            attr = 1500000 + (petlevel * 1500000)
        return attr

    #取宠物攻击世界BOSS
    def get_petattworld(self):
        petid = int(list(str(self.pet))[0])
        return petid

    #取宠物麻痹机率
    def get_petma(self):
        petlevel = int(list(str(self.pet))[1])
        skillma = 20 + (petlevel * 15)
        return skillma

    #设置天罚几率
    def set_tf_rate(self):
        self.tianfa_rate = 50;

    def gateing(self):
        if self.gateingentity == None or self.gatestate == 0:
            return
        if self.spaceUType > 10 and self.spaceUType < 16:
            gotoSpaceUType = random.randint(41, 60)
        if self.spaceUType > 15 and self.spaceUType < 21:
            gotoSpaceUType = random.randint(61, 80)
        if self.spaceUType > 20 and self.spaceUType < 26:
            gotoSpaceUType = random.randint(81, 100)
        if self.spaceUType > 25 and self.spaceUType < 31:
            gotoSpaceUType = random.randint(101, 110)
        if self.spaceUType > 30 and self.spaceUType < 36:
            gotoSpaceUType = random.randint(111, 115)
        #gotoSpaceUType = 10
        spaceData = d_spaces.datas.get(gotoSpaceUType)
        INFO_MSG("传送的坐标：：：：：：：：：：%i" % gotoSpaceUType)
        self.teleportSpace(gotoSpaceUType, spaceData["spawnPos"], (0, 0, 0), {})
        self.gateingentity.destroy()
        pass

    def updateweaponeffid(self, itemid, lucky):
        self.weaponeffid = 0
        if lucky == 1000:
            return
        if lucky > 6:
            self.weaponeffid = 1
        if 143 > itemid > 140:
            self.weaponeffid = 2
            return
        if 145 > itemid > 142:
            self.weaponeffid = 3
            return
        if 147 > itemid > 144:
            self.weaponeffid = 4
            return
        if 149 > itemid > 146:
            self.weaponeffid = 5
            return
        if 151 > itemid > 148:
            self.weaponeffid = 6
            return
        if 153 > itemid > 150:
            self.weaponeffid = 7
            return


    #--------------------------------------------------------------------------------------------
    #                              Callbacks
    #--------------------------------------------------------------------------------------------
    def onTimer(self, tid, userArg):
        """
        KBEngine method.
        引擎回调timer触发
        """
        #DEBUG_MSG("%s::onTimer: %i, tid:%i, arg:%i" % (self.getScriptName(), self.id, tid, userArg))
        GameObject.onTimer(self, tid, userArg)
        Spell.onTimer(self, tid, userArg)


    def onGetWitness(self):
        """
        KBEngine method.
        绑定了一个观察者(客户端)
        """
        #DEBUG_MSG("Avatar::onGetWitness: %i." % self.id)

    def onLoseWitness(self):
        """
        KBEngine method.
        解绑定了一个观察者(客户端)
        """
        #DEBUG_MSG("Avatar::onLoseWitness: %i." % self.id)

    def onDestroy(self):
        """
        KBEngine method.
        entity销毁
        """
        DEBUG_MSG("Avatar::onDestroy: %i." % self.id)
        Teleport.onDestroy(self)
        Combat.onDestroy(self)

    def relive(self, exposed, type):
        """
        defined.
        复活
        """
        if exposed != self.id:
            return

        #DEBUG_MSG("Avatar::relive: %i, type=%i." % (self.id, type))

        # 回城复活
        if type == 0:
            pass

        self.fullPower()
        self.changeState(GlobalDefine.ENTITY_STATE_FREE)
        self.base.relivejump()



    def onAddEnemy(self, entityID):
        """
        virtual method.
        有敌人进入列表
        """
        if not self.isState(GlobalDefine.ENTITY_STATE_FIGHT):
            self.changeState(GlobalDefine.ENTITY_STATE_FIGHT)

    def onEnemyEmpty(self):
        """
        virtual method.
        敌人列表空了
        """
        self.changeState(GlobalDefine.ENTITY_STATE_FREE)
