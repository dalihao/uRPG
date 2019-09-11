# -*- coding: utf-8 -*-
import KBEngine
import time
import random
import SCDefine
import GlobalConst
import Functor
import hashlib
import copy
from KBEDebug import *
from interfaces.GameObject import GameObject
from interfaces.Teleport import Teleport
from Inventory import InventoryMgr
from ITEM_INFO import TItemInfo
import items


class Avatar(KBEngine.Proxy,
             GameObject,
             Teleport):
    """
	角色实体
	"""

    def __init__(self):
        KBEngine.Proxy.__init__(self)
        GameObject.__init__(self)
        Teleport.__init__(self)

        self.accountEntity = None
        self.cellData["dbid"] = self.databaseID
        self.myads = self.databaseID * 2386
        self.nameB = self.cellData["name"]
        self.spaceUTypeB = 1
            #self.cellData["spaceUType"]
        self._destroyTimer = 0
        self.inventory = InventoryMgr(self)
        self.addTimer(3, 3, 2222)
        self.addTimer(3, 0, 2223)
        self.addip = "45.253.67.28"
        self.xzsell = 0

    def onClientEnabled(self):
        """
		KBEngine method.
		该entity被正式激活为可使用， 此时entity已经建立了client对应实体， 可以在此创建它的
		cell部分。

		"""
        INFO_MSG("Avatar[%i-%s] entities enable. spaceUTypeB=%s, entityCall:%s" % (
        self.id, self.nameB, self.spaceUTypeB, self.client))
        KBEngine.globalData["Spaces"].creatpersonspaces(self.databaseID, self.spaceUTypeB)
        Teleport.onClientEnabled(self)

        if self._destroyTimer > 0:
            self.delTimer(self._destroyTimer)
            self._destroyTimer = 0

        if self.isband == 1:
            self.client.errorInfo("角色已被封禁！", 2)
            self.addTimer(2, 0, 1111)

    def onGetCell(self):
        """
		KBEngine method.
		entity的cell部分实体被创建成功
		"""
        if len(self.ups) < 1:
            self.ups = [0,0,0,0,0,0,0,0,0,0]

        if self.buchang != 1 and self.inventory.getbagsempty() >= 1 :
            self.giveitem(46, 200)
            self.buchang = 1
        if self.isband == 1:
            return

        KBEngine.executeRawDatabaseCommand("SELECT * FROM `kbe`.`board` ORDER BY CreateTime desc LIMIT 1",
                                           self.sqlcb_1)
        offlinetime = int(time.time() - self.lasttime)
        self.cell.setviplevel(self.viplevel)
        if offlinetime > 600:
            exprate = 30 * self.yslevel
            if self.viplevel == 1:
                exprate = 60 * self.yslevel
            if self.viplevel == 2:
                exprate = 90 * self.yslevel
            self.lasttime = int(time.time())
            self.cell.addoffexp(int(offlinetime * exprate))
            self.client.offlineexp(offlinetime, exprate)
            self.GAMEGOLD += int(offlinetime * self.yslevel)
        self.updatePropertys()

    def sqlcb_1(self, result, rows, insertid, error):
        print(result[0][0].decode('UTF-8'), rows, insertid, error)
        self.client.board(result[0][0].decode('UTF-8'))
        self.client.set_paylevel(int(result[0][2].decode('UTF-8')))


    def createCell(self, space):
        """
		defined method.
		创建cell实体
		"""

        self.createCellEntity(space)

    def logouting(self, type):
        if type == 1:  # 切换角色
            if self.accountEntity != None:
                self.giveClientTo(self.accountEntity)
                self.accountEntity.activeAvatar = None
                if self.cell is not None:
                    # 销毁cell实体
                    self.destroyCellEntity()
                DEBUG_MSG("logout")
        else:
            if self.cell is not None:
                # 销毁cell实体
                self.destroyCellEntity()

            # 如果帐号ENTITY存在 则也通知销毁它
            if self.accountEntity != None:
                if time.time() - self.accountEntity.relogin > 1:
                    self.accountEntity.destroy()
                else:
                    DEBUG_MSG(
                        "Avatar[%i].destroySelf: relogin =%i" % (self.id, time.time() - self.accountEntity.relogin))

    def onLoseCell(self):
        if not self.isDestroyed:
            self.destroy()

    def destroySelf(self):
        """
		"""
        if self.client is not None:
            return

        if self.cell is not None:
            # 销毁cell实体
            self.destroyCellEntity()

        # 如果帐号ENTITY存在 则也通知销毁它  if time.time() - self.accountEntity.relogin > 1:
        if self.accountEntity != None:
            self.accountEntity.destroy()

    def onClientDeath(self):
        """
		KBEngine method.
		entity丢失了客户端实体
		"""
        DEBUG_MSG("Avatar[%i].onClientDeath:" % self.id)
        self.destroySelf()

    def sendChatMessage(self, msg):
        DEBUG_MSG("Avatar[%i].sendChatMessage:%s" % (self.id, msg))
        if msg[0:5] == "snnui":
            for player in KBEngine.entities.values():
                if player.__class__.__name__ == "Avatar":
                    player.client.ReceiveChatMessage(msg)
            return

        if self.GAMEGOLD > 999:
            self.GAMEGOLD -= 1000
            for player in KBEngine.entities.values():
                if player.__class__.__name__ == "Avatar":
                    player.client.ReceiveChatMessage(msg)
        else:
            self.client.errorInfo("发送全服消息需要1000金币！", 1)

    # 拍卖
    def tradeitem(self, id, price, index, invindex):
        if len([i for i in self.tradenotsell if i > 0]) > 18:
            self.client.errorInfo("只能同时售卖10件！", 2)
            return
        if index > 0:  # 宠物
            petid = self.pets[index * 4 - 4]
            petlevel = self.pets[(index * 4) - 3]
            petfifight = self.pets[(index * 4) - 2]
            if petid == 0:
                self.client.errorInfo("售卖错误！", 2)
                return
            if petid > 0 and petfifight == 1:
                self.client.errorInfo("请先取消出战！", 2)
                return
            if (petid * 10 + petlevel) == id:
                self.pets[index * 4 - 4] = 0
                self.pets[index * 4 - 3] = 0
                self.pets[index * 4 - 2] = 0
                self.pets[index * 4 - 1] = 0
                KBEngine.globalData["trade"].addtrade(self, id, price)
                self.client.errorInfo("售卖成功", 2)
                self.pets = self.pets
            self.tradenotsell.insert(0, price)
            self.tradenotsell.insert(0, id)
            del self.tradenotsell[-1]
            del self.tradenotsell[-1]
            self.tradenotsell = self.tradenotsell
        if index == 0:  # 神器
            itemUUId = self.inventory.getItemUidByIndex(invindex)
            if itemUUId == 0:
                return
            itemId = self.itemList[itemUUId][1]
            itemCount = self.itemList[itemUUId][2]
            if itemId != id or itemCount < 1:
                return
            itemresult = self.inventory.removeItem(itemUUId, 1)
            KBEngine.globalData["trade"].addtrade(self, (id + 10000), price)
            self.client.errorInfo("售卖成功", 2)
            if itemresult == -1:  # 只是减少物品数量，并没有销毁
                self.client.pickUp_re(self.itemList[itemUUId])
            else:  # 销毁物品
                self.client.dropItem_re(itemresult, itemUUId)
            self.tradenotsell.insert(0, price)
            self.tradenotsell.insert(0, (id + 10000))
            del self.tradenotsell[-1]
            del self.tradenotsell[-1]
            self.tradenotsell = self.tradenotsell

    def buytradeitem(self, uid):
        result = self.inventory.checkisfull()
        if uid == 0:
            return
        price = KBEngine.globalData["trade"].getpricebyuid(uid)
        itemid = KBEngine.globalData["trade"].getidbyuid(uid)
        if price is not None:
            if self.GAMEDIAMOND >= price:
                if itemid > 10000:  # 神器
                    if result == -1:
                        self.client.errorInfo("背包满了！", 1)
                        return
                    self.GAMEDIAMOND -= price
                    tempitemid = itemid - 10000
                    itemUUIdList = self.inventory.addItem(tempitemid, 1, 0, 0, 0, 0, 0, 0)
                    KBEngine.globalData["trade"].buyok(uid)
                    self.gettradelist(1)
                    for uuid in itemUUIdList:
                        self.client.pickUp_re(self.itemList[uuid])
                    self.client.errorInfo("购买成功！", 2)
                    self.tradebuylogs.insert(0, price)
                    self.tradebuylogs.insert(0, itemid)
                    del self.tradebuylogs[-1]
                    del self.tradebuylogs[-1]
                    self.tradebuylogs = self.tradebuylogs

                else:  # 宠物
                    checkresult = self.checkpetspace()
                    if checkresult < 1:
                        self.client.errorInfo("宠物空间满了！", 1)
                        return
                    self.GAMEDIAMOND -= price
                    for i in range(1, 11):
                        if self.pets[i * 4 - 4] == 0:
                            self.pets[i * 4 - 4] = int(itemid / 10)
                            self.pets[i * 4 - 3] = int(itemid % 10)
                            self.pets = self.pets
                            break
                    self.gettradelist(1)
                    KBEngine.globalData["trade"].buyok(uid)
                    self.client.errorInfo("购买成功！", 2)
                    self.tradebuylogs.insert(0, price)
                    self.tradebuylogs.insert(0, itemid)
                    del self.tradebuylogs[-1]
                    del self.tradebuylogs[-1]
                    self.tradebuylogs = self.tradebuylogs

            else:
                self.client.errorInfo("钻石不足！", 2)
        else:
            self.client.errorInfo("此物品已售出！", 2)

    def sendtradeback(self):
        sqcount = 0
        petcount = 0
        for id in self.tradeback:
            if id > 10000:
                sqcount += 1
            else:
                petcount += 1
        result = self.inventory.getbagsempty()
        if result < sqcount:
            self.client.errorInfo("背包不足%i格，清空背包后返还到期售卖物品！" % sqcount, 2)
            return
        checkresult = self.checkpetspace()
        if checkresult < petcount:
            self.client.errorInfo("宠物空间不足%i格，清空后返还到期售卖物品！" % petcount, 2)
            return

        for xx, val in enumerate(self.tradeback):
            if xx % 2 == 0:
                itemid = val
                for xid, xval in enumerate(self.tradenotsell):
                    if xid % 2 == 0:
                        if xval == val and self.tradenotsell[xid + 1] == self.tradeback[xx + 1]:
                            del self.tradenotsell[xid]
                            del self.tradenotsell[xid]
                            self.tradenotsell.append(0)
                            self.tradenotsell.append(0)
                            self.tradenotsell = self.tradenotsell
                            break
                if itemid > 10000:  # 神器
                    itemid = itemid - 10000
                    itemUUIdList = self.inventory.addItem(itemid, 1, 0, 0, 0, 0, 0, 0)
                    for uuid in itemUUIdList:
                        self.client.pickUp_re(self.itemList[uuid])
                else:  # 宠物
                    for i in range(1, 11):
                        if self.pets[i * 4 - 4] == 0:
                            self.pets[i * 4 - 4] = int(itemid / 10)
                            self.pets[i * 4 - 3] = int(itemid % 10)
                            self.pets = self.pets
                            break

        self.tradeback = []
        self.client.errorInfo("到期售卖物品已全部返还！", 2)

    def gettradelist(self, page):
        KBEngine.globalData["trade"].reqtradeslist(self, page)
        pass

    # 整理背包
    def refreshItem(self):
        self.inventory.refreshItem(self)
        print(self.tradeback)

    # 设置为已查看
    def setnotnew(self, itemIndex):
        self.inventory.setnotnew(self, itemIndex)

    def reqItemList(self):
        if self.client:
            self.client.onReqItemList(self.itemList, self.storeList, self.equipItemList)

    def pickUpResponse(self, success, dropitemcall, itemID, itemCount, lucky, arrt1, arrt2, arrt3, arrt4, arrt5):
        if success:
            itemUUIdList = self.inventory.addItem(itemID, itemCount, lucky, arrt1, arrt2, arrt3, arrt4, arrt5)
            if len(itemUUIdList) > 0:
                dropitemcall.candestroyself()
            for uuid in itemUUIdList:
                self.client.pickUp_re(self.itemList[uuid])

    def diedrop(self, badpoint):
        droprate = random.randint(0, 10000)
        if droprate > badpoint:
            return
        droprate2 = random.randint(0, 10000)
        if droprate2 > 8000: #身上物品
            self.inventory.dropequipitem(self)
        else:
            self.inventory.dropinvitem(self)

        self.updatePropertys()

    def getitemcount(self, itemindex):
        itemcount = 0
        for key, info in self.itemList.items():
            if info[1] == itemindex:
                itemcount += info[2]
        return itemcount

    def usritems(self, itemindex, count):
        itemcount = count
        templist = copy.deepcopy(self.itemList)
        for key, info in templist.items():
            if info[1] == itemindex:
                if itemcount <= 0:
                    break
                if info[2] >= itemcount:
                    itemId = self.inventory.removeItem(info[0], itemcount)
                    self.client.pickUp_re(self.itemList[info[0]])
                    break
                else:
                    itemId = self.inventory.removeItem(info[0], info[2])
                    self.client.dropItem_re(itemId, info[0])
                    itemcount -= info[2]

    def giveitem(self, id, count):
        if self.inventory.getbagsempty() >= 1:
            itemUUIdList = self.inventory.addItem(id, count, 0, 0, 0, 0, 0, 0)
            for uuid in itemUUIdList:
                self.client.pickUp_re(self.itemList[uuid])
            if id == 46:
                self.client.errorInfo("获得火陨石%i个！" % count, 2)
            if id == 47:
                self.client.errorInfo("获得升级保护符%i个！" % count, 2)
        else:
            self.client.errorInfo("背包空格不足1！", 1)

    def dropRequest(self, itemUUId):
        itemCount = self.itemList[itemUUId][2]
        lucky = self.itemList[itemUUId][5]
        arrt1 = self.itemList[itemUUId][6]
        arrt2 = self.itemList[itemUUId][7]
        arrt3 = self.itemList[itemUUId][8]
        arrt4 = self.itemList[itemUUId][9]
        arrt5 = self.itemList[itemUUId][10]
        itemId = self.inventory.removeItem(itemUUId, itemCount)
        self.cell.dropNotify(itemId, itemUUId, itemCount, lucky, arrt1, arrt2, arrt3, arrt4, arrt5, 1)

    def swapItemRequest(self, srcIndex, dstIndex):
        self.inventory.swapItem(srcIndex, dstIndex)

    # 检查背包是否是满
    def checkisfull(self, dropitem):
        result = self.inventory.checkisfull()

        if result != -1:
            DEBUG_MSG("背包满的")

    # dropitem.candestroyself()

    # 穿装备
    def equipItemRequest(self, itemIndex, equipIndex1, equipIndex2):
        itemUUId = self.inventory.getItemUidByIndex(itemIndex)
        needlevel = 0
        if itemUUId > 0:
            item = items.getItem(self.itemList[itemUUId][1])
            needlevel = item.checkneed()
        if needlevel == -1:
            return
        self.cell.returnzs_level(needlevel, itemIndex, equipIndex1, equipIndex2)

    # 穿装备
    def equipItemRequestok(self, itemIndex, equipIndex1, equipIndex2):
        # itemIndex 背包物品
        # equipIndex1 身上物品1
        # equipIndex2 身上物品1

        if equipIndex2 < 100:
            if self.inventory.gethaveitem(equipIndex1) == -1:
                equipIndex = equipIndex1
            elif self.inventory.gethaveitem(equipIndex2) == -1:
                equipIndex = equipIndex2
            else:
                equipIndex = equipIndex1
        else:
            if equipIndex2 == 1001 and self.inventory.invgethaveitem(itemIndex) != -1:  # 脱装备
                self.client.errorInfo("请重试！", 1)
                return
            equipIndex = equipIndex1

        itemUUId = self.inventory.getItemUidByIndex(itemIndex)
        equipUUId = self.inventory.getEquipUidByIndex(equipIndex)

        if itemUUId != 0 and equipUUId != 0 and equipIndex2 != 1001:
            item = items.getItem(self.itemList[itemUUId][1])
            eitem = items.getItem(self.equipItemList[equipUUId][1])
            invtype = item.gettype(self)
            eitemtype = eitem.gettype(self)
            if invtype != eitemtype:
                return

        if self.inventory.equipItem(itemIndex, equipIndex) == -1:
            self.client.errorInfo("穿戴失败！", 1)
        else:
            itemUUId = self.inventory.getItemUidByIndex(itemIndex)
            equipUUId = self.inventory.getEquipUidByIndex(equipIndex)
            # 传回去装备和物品信息
            itemInfo = TItemInfo()
            itemInfo.extend([0, 0, 0, itemIndex, 0, 0, 0, 0, 0, 0, 0])
            equipItemInfo = TItemInfo()
            equipItemInfo.extend([0, 0, 0, equipIndex, 0, 0, 0, 0, 0, 0, 0])
            if itemUUId != 0:
                itemInfo = self.itemList[itemUUId]
            if equipUUId != 0:
                equipItemInfo = self.equipItemList[equipUUId]

            if equipIndex == 0 and equipUUId == 0:
                self.cell.updateweaponeffid(0, 1000)
            if equipIndex == 0 and equipUUId != 0:
                self.cell.updateweaponeffid(self.equipItemList[equipUUId][1], self.equipItemList[equipUUId][5])

            self.client.equipItemRequest_re(itemInfo, equipItemInfo)
            # --------------------
            avatarCell = self.cell
            # 重设力量等属性
            # 计算身上装备加成
            self.updatePropertys()
            if equipIndex == 0:
                uid = self.inventory.getEquipUidByIndex(equipIndex)
                if uid == 0:
                    avatarCell.equipNotify(-1)
                else:
                    avatarCell.equipNotify(self.equipItemList[uid][1])

    def updatePropertys(self):
        avatarCell = self.cell
        self.cell.changespeed(0)
        self.cell.changeskill_p(0)
        self.cell.changerelive_p(0)
        avatarCell.resetPropertys(self.lengends, self.shields)
        for key, info in self.equipItemList.items():
            items.getItem(info[1]).use(self, info[3])
            self.cell.addarrts(info[5], info[6], info[7], info[8], info[9], info[10])
        self.cell.addarrts(0, 0, (min(self.ups) * 5), (min(self.ups) * 3), (self.yslevel * 10) + (min(self.ups) * 10), 0)
        self.cell.setzdl()

    def useItemRequest(self, itemIndex):
        itemUUId = self.inventory.getItemUidByIndex(itemIndex)
        item = items.getItem(self.itemList[itemUUId][1])
        itemCount = self.itemList[itemUUId][2]
        usetype = item.use(self, itemUUId, itemCount)
        if usetype == GlobalConst.GC_OK:

            itemId = self.inventory.removeItem(itemUUId, 1)
            if itemId == -1:  # 只是减少物品数量，并没有销毁
                self.client.pickUp_re(self.itemList[itemUUId])
            else:  # 销毁物品
                self.client.dropItem_re(itemId, itemUUId)

    # 单个回收
    def sellItem(self, itemIndex):
        itemUUId = self.inventory.getItemUidByIndex(itemIndex)
        if itemUUId is None:
            return
        item = items.getItem(self.itemList[itemUUId][1])
        item.sellself(self)
        itemCount = self.itemList[itemUUId][2]
        itemId = self.inventory.removeItem(itemUUId, 1)
        if itemId == -1:  # 只是减少物品数量，并没有销毁
            self.client.pickUp_re(self.itemList[itemUUId])
        else:  # 销毁物品
            self.client.dropItem_re(itemId, itemUUId)

    def sellAllItem(self, itemlevel):
        totalprice = 0
        totalitems = 0
        templist = copy.deepcopy(self.itemList)
        for key, info in templist.items():
            itemUUId = self.inventory.getItemUidByIndex(info[3])
            needlevel = 100
            if itemUUId > 0:
                item = items.getItem(self.itemList[itemUUId][1])
                if item.__class__.__name__ == "ItemEquip":
                    needlevel = item.checkneed()
                    type = item.gettype(self)
                    if itemlevel >= needlevel and type != 20 and type != 21 and type != 22:
                        totalprice += item.sellself(self)
                        totalitems += 1
                        self.inventory.removeItem(itemUUId, 1)
        if totalitems > 0:
            self.client.errorInfo("共计回收：%i件装备，总金额：%i！" % (totalitems, totalprice), 2)
            self.refreshItem()
        else:
            self.client.errorInfo("没有%i转物品，请在游戏设置中调整！" % itemlevel, 1)


    # 存仓库
    def sendtostore(self, storeIndex, itemIndex):

        if self.inventory.sendtostore(storeIndex, itemIndex) == -1:
            self.client.errorInfo("存取失败！", 1)
        elif self.inventory.sendtostore(storeIndex, itemIndex) == -2:
            self.client.errorInfo("仓库已满！", 1)
        elif self.inventory.sendtostore(storeIndex, itemIndex) == -3:
            self.client.errorInfo("背包满了！", 1)
        else:
            # 传回去装备和物品信息
            itemUUId = self.inventory.getItemUidByIndex(itemIndex)
            storeUUId = self.inventory.getStoreUidByIndex(storeIndex)
            itemcount = 0
            storecount = 0
            if itemUUId != 0:
                itemcount = self.itemList[itemUUId][2]
            if storeUUId != 0:
                storecount = self.storeList[storeUUId][2]
            itemInfo = TItemInfo()
            itemInfo.extend([0, 0, itemcount, itemIndex, 0, 0, 0, 0, 0, 0, 0])
            storeItemInfo = TItemInfo()
            storeItemInfo.extend([0, 0, storecount, storeIndex, 0, 0, 0, 0, 0, 0, 0])
            if itemUUId != 0:
                itemInfo = self.itemList[itemUUId]
            if storeUUId != 0:
                storeItemInfo = self.storeList[storeUUId]
            self.client.storeItemRequest_re(itemInfo, storeItemInfo)

    def lucky_w_up(self, type):
        if type == 1:
            if self.GAMEGOLD > 4999:
                result = self.inventory.lucky_w(self)
                if result == 1:
                    self.GAMEGOLD -= 5000
                    self.updatePropertys()
            else:
                self.client.errorInfo("金币不足！", 1)
        if type == 2:
            if self.GAMEDIAMOND > 99:
                result = self.inventory.lucky_w(self)
                if result == 1:
                    self.GAMEDIAMOND -= 100
                    self.updatePropertys()
            else:
                self.client.errorInfo("钻石不足！", 1)

    def lucky_n_up(self, type):
        if type == 1:
            if self.GAMEGOLD > 9999:
                result = self.inventory.lucky_n(self)
                if result == 1:
                    self.GAMEGOLD -= 10000
                    self.updatePropertys()
            else:
                self.client.errorInfo("金币不足！", 1)
        if type == 2:
            if self.GAMEDIAMOND > 199:
                result = self.inventory.lucky_n(self)
                if result == 1:
                    self.GAMEDIAMOND -= 200
                    self.updatePropertys()
            else:
                self.client.errorInfo("钻石不足！", 1)

    def jumpto(self, mapid):
        self.cell.getzs_level(mapid)

    def startjumpto(self, zs_level, mapid):
        DEBUG_MSG("跳转地图：：：：：：：：：%i" % mapid)
        tomap = 0;
        if mapid > 10 and mapid < 16 and zs_level <= 5:
            KBEngine.globalData["Spaces"].teleportSpace(self, mapid, (0, 0, -10), (0, 90, 0), {})
            return
        elif mapid > 10 and mapid < 16 and zs_level > 5:
            self.client.errorInfo("转生等级已超过5转！", 1)
            return

        if mapid > 15 and mapid < 21 and zs_level < 5:
            self.client.errorInfo("转生等级不够！", 1)
            return
        elif mapid > 15 and mapid < 21 and zs_level > 10:
            self.client.errorInfo("转生等级已超过10转！", 1)
            return

        if mapid > 20 and mapid < 26 and zs_level < 10:
            self.client.errorInfo("转生等级不够！", 1)
            return
        elif mapid > 20 and mapid < 26 and zs_level > 15:
            self.client.errorInfo("转生等级已超过15转！", 1)
            return

        if mapid > 25 and mapid < 31 and zs_level < 15:
            self.client.errorInfo("转生等级不够！", 1)
            return
        if mapid > 30 and mapid < 36 and zs_level < 20:
            self.client.errorInfo("转生等级不够！", 1)
            return
        if mapid == 36 and KBEngine.globalData["worldboss"] == 0:
            self.client.errorInfo("世界BOSS未开放！", 1)
            return

        if mapid == 6 and self.ticket1 < 1:
            self.client.errorInfo("神庙圣物不足！", 1)
            return
        if mapid == 7 and self.ticket2 < 1:
            self.client.errorInfo("地宫之心不足！", 1)
            return

        if mapid == 0:
            KBEngine.globalData["Spaces"].teleportPersonSpace(self, 1, (0, 0, -10), (0, 90, 0), {})
            return
        if mapid == 6:
            self.ticket1 -= 1
            KBEngine.globalData["Spaces"].teleportPersonSpace(self, 2, (0, 0, -10), (0, 90, 0), {})
            return
        if mapid == 7:
            self.ticket2 -= 1
            KBEngine.globalData["Spaces"].teleportPersonSpace(self, 3, (0, 0, -10), (0, 90, 0), {})
            return
        if mapid == 8:
            KBEngine.globalData["Spaces"].teleportPersonSpace(self, 4, (0, 0, -10), (0, 90, 0), {})
            return

        KBEngine.globalData["Spaces"].teleportSpace(self, mapid, (0, 0, -10), (0, 90, 0), {})



    def relivejump(self):
        KBEngine.globalData["Spaces"].teleportPersonSpace(self, 1, (0, 0, -10), (0, 90, 0), {})

    def poweropen(self):
        if self.GAMEDIAMOND > 999:
            self.GAMEDIAMOND -= 1000
            self.cell.poweropen()
            self.client.errorInfo("狂暴之力开启成功！", 2)
        else:
            self.client.errorInfo("钻石不足1000！", 1)

    # 开始转生
    def zs_up(self):
        self.cell.getzs_level(-1)

    # 开始转生
    def zs_up_start(self, zs_level, level):
        if zs_level < 5:
            if self.zs1_item > 9:
                self.zs1_item -= 10
                self.cell.zs_up()
                if self.adswho != 0:
                    KBEngine.createEntityFromDBID("Avatar", int(self.adswho / 2386), self.adsback2)
                return
            else:
                self.client.errorInfo("材料不足！", 1)
                return
        elif zs_level < 10:
            if self.zs2_item > 9 and level > 99:
                self.zs2_item -= 10
                self.cell.zs_up()
                return
            else:
                self.client.errorInfo("材料不足或者等级不够！", 1)
                return
        elif zs_level < 15:
            if self.zs3_item > 9 and level > 199:
                self.zs3_item -= 10
                self.cell.zs_up()
                return
            else:
                self.client.errorInfo("材料不足或者等级不够！", 1)
                return
        elif zs_level < 20:
            if self.zs4_item > 9 and level > 299:
                self.zs4_item -= 10
                self.cell.zs_up()
                return
            else:
                self.client.errorInfo("材料不足或者等级不够！", 1)
                return
        elif zs_level < 25:
            if self.zs5_item > 9 and level > 399:
                self.zs5_item -= 10
                self.cell.zs_up()
                return
            else:
                self.client.errorInfo("材料不足或者等级不够！", 1)
                return

    # 转生材料合成
    def create_zs_item(self, n):
        if n == 2:
            if self.zs1_item > 4:
                self.zs1_item -= 5
                self.zs2_item += 1
                self.client.errorInfo("合成成功！", 2)
            else:
                self.client.errorInfo("材料不足！", 1)
        if n == 3:
            if self.zs2_item > 4:
                self.zs2_item -= 5
                self.zs3_item += 1
                self.client.errorInfo("合成成功！", 2)
            else:
                self.client.errorInfo("材料不足！", 1)
        if n == 4:
            if self.zs3_item > 4:
                self.zs3_item -= 5
                self.zs4_item += 1
                self.client.errorInfo("合成成功！", 2)
            else:
                self.client.errorInfo("材料不足！", 1)
        if n == 5:
            if self.zs4_item > 4:
                self.zs4_item -= 5
                self.zs5_item += 1
                self.client.errorInfo("合成成功！", 2)
            else:
                self.client.errorInfo("材料不足！", 1)

    # 开始称号
    def title_up(self):
        self.cell.get_title()

    def title_up_start(self, title):
        if title == 18:
            return
        if title == 1 and self.GAMEGOLD > 999:
            self.GAMEGOLD -= 1000
            self.cell.title_up()
            return
        if title == 2 and self.GAMEGOLD > 2999:
            self.GAMEGOLD -= 3000
            self.cell.title_up()
            return
        if title == 3 and self.GAMEGOLD > 4999:
            self.GAMEGOLD -= 5000
            self.cell.title_up()
            return
        if title == 4 and self.GAMEGOLD > 9999:
            self.GAMEGOLD -= 10000
            self.cell.title_up()
            return
        if title == 5 and self.GAMEGOLD > 49999:
            self.GAMEGOLD -= 50000
            self.cell.title_up()
            return
        if title == 6 and self.GAMEGOLD > 99999:
            self.GAMEGOLD -= 100000
            self.cell.title_up()
            return
        if title == 7 and self.GAMEGOLD > 199999:
            self.GAMEGOLD -= 200000
            self.cell.title_up()
            return
        if title == 8 and self.GAMEGOLD > 499999:
            self.GAMEGOLD -= 500000
            self.cell.title_up()
            return
        if title == 9 and self.GAMEGOLD > 799999:
            self.GAMEGOLD -= 800000
            self.cell.title_up()
            return
        if title == 10 and self.GAMEGOLD > 999999:
            self.GAMEGOLD -= 1000000
            self.cell.title_up()
            return
        if title == 11 and self.GAMEGOLD > 999999:
            self.GAMEGOLD -= 1000000
            self.cell.title_up()
            return
        if title == 12 and self.GAMEGOLD > 1999999:
            self.GAMEGOLD -= 2000000
            self.cell.title_up()
            return
        if title == 13 and self.GAMEGOLD > 1999999:
            self.GAMEGOLD -= 2000000
            self.cell.title_up()
            return
        if title == 14 and self.GAMEGOLD > 2999999:
            self.GAMEGOLD -= 3000000
            self.cell.title_up()
            return
        if title == 15 and self.GAMEGOLD > 2999999:
            self.GAMEGOLD -= 3000000
            self.cell.title_up()
            return
        if title == 16 and self.GAMEGOLD > 3999999:
            self.GAMEGOLD -= 4000000
            self.cell.title_up()
            return
        if title == 17 and self.GAMEGOLD > 4999999:
            self.GAMEGOLD -= 5000000
            self.cell.title_up()
            return
        self.client.errorInfo("称号升级失败！", 1)

    def xz_up(self, index):
        self.cell.get_xz(index)

    def xz_up_start(self, xz_level1, xz_level2, xz_level3, xz_level4, xz_level5, xz_level6, xz_level7, xz_level8,
                    xz_level9, xz_level10, xz_level11, xz_level12, xz_minindex):
        xzlist = [xz_level1, xz_level2, xz_level3, xz_level4, xz_level5, xz_level6, xz_level7, xz_level8, xz_level9,
                  xz_level10, xz_level11, xz_level12]
        xz_min = xzlist[xz_minindex - 1]
        if self.xz_book < 1:
            self.client.errorInfo("星宫之书不足1个！" , 2)
            return
        if xz_min > 99:
            self.client.errorInfo("已经满级！", 2)
            return
        else:
            self.xz_book -= 1
            self.cell.xz_up(xz_minindex)
            self.client.errorInfo("升级成功！", 2)
            self.updatePropertys()


    def setxzsell(self, xz_level11):
        self.xzsell = xz_level11 * 0.1

        """
        xz_min = min(xzlist)
        xz_minindex = xzlist.index(xz_min)
        if xz_min > 6:
            self.client.errorInfo("已经满级！", 2)
            return
        elif self.xz_book >= (xz_min + 1):
            self.xz_book -= (xz_min + 1)
            self.cell.xz_up(xz_minindex + 1)
            self.client.errorInfo("升级成功！", 2)
        else:
            self.client.errorInfo("星宫之书不足%i个！" % (xz_min + 1), 1)
        """

    def skill_update(self, skillID):
        self.cell.get_skill(skillID)

    def skill_update_start(self, skillID, skill_level):
        if skill_level > 9:
            self.client.errorInfo("技能已经满级！", 2)
            return
        elif self.GAMEGOLD > 199999:
            self.GAMEGOLD -= 200000
            self.cell.skill_update(skillID)
            self.client.errorInfo("技能升级成功！", 2)
        else:
            self.client.errorInfo("金币不足！", 1)

    def lengend_up(self, id):
        if self.lengends[id] > 0:
            self.cell.set_lengend(id)

    def shield_up(self, id):
        if self.shields[id] > 0:
            self.cell.set_shield(id)

    def tianfa_up(self, type):
        self.cell.get_tianfa(type)
        pass

    def tianfa_up_start(self, type, level):
        if level > 9:
            self.client.errorInfo("已经满级！", 2)
            return
        if type == 1:
            if self.GAMEGOLD > (((level + 1) * 100000) - 1):
                self.GAMEGOLD -= ((level + 1) * 100000)
                self.cell.tianfa_update()
            else:
                self.client.errorInfo("金币不足！", 1)

        if type == 2:
            if self.GAMEDIAMOND > ((1000 + (level * 1000)) - 1):
                self.GAMEDIAMOND -= (1000 + (level * 1000))
                self.cell.tianfa_update()
            else:
                self.client.errorInfo("钻石不足！", 1)
        pass

    # 1 - 10   ID  等级  出战  时间
    def pet_up(self, index, type):
        petid = self.pets[index * 4 - 4]
        petlevel = self.pets[(index * 4) - 3]
        petfifight = self.pets[(index * 4) - 2]
        if petid == 0:
            return
        if petlevel > 4:
            return
        if type == 1:
            if self.GAMEGOLD > (30000 * (petlevel + 1) * (petid + 1)) - 1:
                self.GAMEGOLD -= (30000 * (petlevel + 1) * (petid + 1))
                rate = random.randint(0, 100)
                if rate < 30:
                    self.pets[(index * 4) - 3] += 1
                    self.client.errorInfo("升级成功！", 2)
                    self.pets = self.pets
                else:
                    self.client.errorInfo("升级失败！", 1)
            else:
                self.client.errorInfo("金币不足！", 1)
        if type == 2:
            if self.GAMEDIAMOND > (100 * (petlevel + 1) * (petid + 1)) - 1:
                self.GAMEDIAMOND -= (100 * (petlevel + 1) * (petid + 1))
                self.pets[(index * 4) - 3] += 1
                self.client.errorInfo("升级成功！", 2)
                DEBUG_MSG(self.pets)
                self.pets = self.pets
            else:
                self.client.errorInfo("钻石不足！", 1)
        if petfifight == 1:
            tindex = petid * 10 + self.pets[(index * 4) - 3]
            self.cell.pet_fight(tindex)

    def pet_open(self, index):
        petid = self.pets[index * 4 - 4]
        if petid == 0:
            return
        if self.GAMEDIAMOND > 199:
            self.GAMEDIAMOND -= 200
            self.pets[(index * 4) - 1] -= 2000
            temprate = random.randint(0, 1000)
            self.pets[index * 4 - 4] = 1
            if temprate == 1:
                self.pets[index * 4 - 4] = 6
            if temprate > 1 and temprate < 4:
                self.pets[index * 4 - 4] = 5
            if temprate > 3 and temprate < 7:
                self.pets[index * 4 - 4] = 4
            if temprate > 6 and temprate < 13:
                self.pets[index * 4 - 4] = 3
            if temprate > 12 and temprate < 22:
                self.pets[index * 4 - 4] = 2
            self.client.errorInfo("孵化成功！", 2)
            self.pets = self.pets
        else:
            self.client.errorInfo("钻石不足！", 1)

    def pet_kill(self, index):
        petid = self.pets[index * 4 - 4]
        petlevel = self.pets[(index * 4) - 3]
        petfifight = self.pets[(index * 4) - 2]
        if petid > 0 and petfifight == 1:
            self.client.errorInfo("请先取消出战！", 2)
            return
        if petid > 0:
            self.GAMEGOLD += 5000 * (petlevel + 1)
            self.pets[index * 4 - 4] = 0
            self.pets[(index * 4) - 3] = 0
            self.client.errorInfo("放生成功！金币+%i" % (5000 * (petlevel + 1)), 2)
            self.pets = self.pets

    def pet_fight(self, index):
        petid = self.pets[index * 4 - 4]
        petlevel = self.pets[(index * 4) - 3]
        petfifight = self.pets[(index * 4) - 2]
        if petid > 0 and petfifight == 1:
            return
        if petid > 0:
            for i in range(1, 11):
                self.pets[(i * 4) - 2] = 0
            self.pets[(index * 4) - 2] = 1
            tindex = petid * 10 + petlevel
            self.cell.pet_fight(tindex)
            self.client.errorInfo("出战成功！", 2)
            self.pets = self.pets

    def pet_nofight(self, index):
        petid = self.pets[index * 4 - 4]
        petfifight = self.pets[(index * 4) - 2]
        if petid > 0 and petfifight == 0:
            return
        if petid > 0:
            self.pets[(index * 4) - 2] = 0
            tindex = 0
            self.cell.pet_fight(tindex)
            self.client.errorInfo("宠物已召回！", 2)
            self.pets = self.pets

    def checkpetspace(self):
        tempcount = 0
        for i in range(1, 11):
            if self.pets[i * 4 - 4] == 0:
                tempcount += 1
        return tempcount

    def buyvip(self, id):
        if self.viplevel == 2 and self.vip2time > time.time() and id == 1:
            self.client.errorInfo("你已经是至尊月卡用户！", 2)
            return
        if id == 1:
            if self.GAMEDIAMOND > 2999:
                self.GAMEDIAMOND -= 3000
                if self.vip1time < time.time():
                    self.vip1time = int(time.time()) + 2592000
                else:
                    self.vip1time += 2592000
                self.viplevel = 1
                self.cell.setviplevel(self.viplevel)
                self.client.errorInfo("黄金月卡购买成功！", 2)
            else:
                self.client.errorInfo("钻石不足！", 1)
        if id == 2:
            if self.GAMEDIAMOND > 6599:
                self.GAMEDIAMOND -= 6600
                if self.vip2time < time.time():
                    self.vip2time = int(time.time()) + 2592000
                else:
                    self.vip2time += 2592000
                self.viplevel = 2
                self.cell.setviplevel(self.viplevel)
                self.client.errorInfo("至尊月卡购买成功！", 2)
            else:
                self.client.errorInfo("钻石不足！", 1)

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

    #签到
    def re_qiandao(self):
        tmpstr = str(time.strftime('%Y%m%d', time.localtime(time.time())))
        if tmpstr == str(self.qdtime):
            return
        else:
            self.qdtime = tmpstr
            self.qdtimes += 1
            self.GAMEGOLD += 10000
            self.ticket1 += 1
            self.ticket2 += 1
            self.client.errorInfo("签到成功！", 2)


    #领取签到
    def get_qiandao(self, day):
        if day == 3 and self.qdtimes > 2:
            if self.qd3 == 0:
                self.GAMEGOLD += 50000
                self.qd3 = 1
        if day == 7 and self.qdtimes > 6:
            if self.qd7 == 0:
                self.GAMEGOLD += 100000
                self.xz_book += 5
                self.qd7 = 1
        if day == 15 and self.qdtimes > 14:
            if self.qd15 == 0:
                self.GAMEGOLD += 200000
                self.xz_book += 20
                self.qd15 = 1
        if day == 30 and self.qdtimes > 29:
            if self.qd30 == 0 :
                if self.inventory.getbagsempty() > 0:
                    self.GAMEGOLD += 1000000
                    self.xz_book += 30
                    self.inventory.addItem(1, 1, 0, 0, 0, 0, 0, 0)
                    self.qdtimes = 0
                    self.qd3 = 0
                    self.qd7 = 0
                    self.qd15 = 0
                    self.qd30 = 0
                    self.refreshItem()
                else:
                    self.client.errorInfo("背包空格不足1！", 2)

    def getfirstpay(self):

        if self.firstpay == 0 and self.money > 99:
            if self.inventory.getbagsempty() > 1:
                self.firstpay = 1
                self.xz_book += 100
                self.ticket1 += 5
                self.ticket2 += 5
                self.cell.set_tf_rate()
                arrt1 = random.randint(1, 15)  # 暴击20
                arrt2 = random.randint(1, 30)  # 暴伤50
                self.inventory.addItem(1, 1, 0, 0, 0, 0, 0, 0)
                self.inventory.addItem(130, 1, 0, arrt1, arrt2, 0, 0, 0)
                self.client.errorInfo("领取成功！", 2)
                self.refreshItem()
            else:
                self.client.errorInfo("背包空格不足2！", 2)
        elif self.firstpay == 1 and self.money > 499:
            if self.inventory.getbagsempty() > 2:
                self.firstpay = 2
                arrt1 = random.randint(0, 5)  # 暴击 5
                arrt2 = random.randint(0, 20)  # 暴伤 20
                arrt3 = random.randint(0, 10)  # 攻击伤害  10
                arrt4 = random.randint(0, 30)  # 体力  30
                arrt5 = random.randint(0, 5)  # 减免  5
                self.inventory.addItem(644, 1, 0, arrt1, arrt2, arrt3, arrt4, arrt5)
                arrt1 = random.randint(0, 5)  # 暴击 5
                arrt2 = random.randint(0, 20)  # 暴伤 20
                arrt3 = random.randint(0, 10)  # 攻击伤害  10
                arrt4 = random.randint(0, 30)  # 体力  30
                arrt5 = random.randint(0, 5)  # 减免  5
                self.inventory.addItem(654, 1, 0, arrt1, arrt2, arrt3, arrt4, arrt5)
                arrt1 = random.randint(0, 5)  # 暴击 5
                arrt2 = random.randint(0, 20)  # 暴伤 20
                arrt3 = random.randint(0, 10)  # 攻击伤害  10
                arrt4 = random.randint(0, 30)  # 体力  30
                arrt5 = random.randint(0, 5)  # 减免  5
                self.inventory.addItem(664, 1, 0, arrt1, arrt2, arrt3, arrt4, arrt5)
                self.client.errorInfo("领取成功！", 2)
                self.refreshItem()
            else:
                self.client.errorInfo("背包空格不足3！", 2)
        else:
            self.client.errorInfo("条件不足！", 1)

    def refresh(self):
        if self.viplevel == 1 and self.vip1time < time.time():
            self.viplevel = 0
        if self.viplevel == 2 and self.vip2time < time.time():
            if self.viplevel == 1 and self.vip1time >= time.time():
                self.viplevel = 1
            else:
                self.viplevel = 0
        self.viplevel = self.viplevel
        self.cell.setviplevel(self.viplevel)


    def ads_getnew(self, who):
        if who % 2386 > 0 :
            self.client.errorInfo("已经领取过或者推广码不正确！", 2)
            return
        if self.adswho == 0 and (who / 2386) < self.databaseID and who > 2386:
            if self.inventory.getbagsempty() > 0:
                self.adswho = who
                self.GAMEGOLD += 100000
                self.ticket1 += 3
                self.ticket2 += 3
                self.zs1_item += 5
                arrt1 = random.randint(1, 15)  # 暴击20
                arrt2 = random.randint(1, 30)  # 暴伤50
                self.inventory.addItem(111, 1, 0, arrt1, arrt2, 0, 0, 0)
                self.refreshItem()
                KBEngine.createEntityFromDBID("Avatar", int(who / 2386), self.adsback)
            else:
                self.client.errorInfo("背包空格不足1！", 2)
                return
        else:
            self.client.errorInfo("已经领取过或者推广码不正确！", 2)



    def adsback(self, baseRef, dbid, wasActive):
        if baseRef is None:  # 不存在
            return
        baseRef.adspoint += 1
        baseRef.adshumans += 1
        if wasActive:  # 在线
            return
        # 不在线
        baseRef.destroy()

    def adsback2(self, baseRef, dbid, wasActive):
        if baseRef is None:  # 不存在
            return
        baseRef.adspoint += 20
        if wasActive:  # 在线
            return
        # 不在线
        baseRef.destroy()

    def ads_getdia(self):
        if self.adsdiamond > 0:
            self.GAMEDIAMOND += self.adsdiamond
            self.client.errorInfo("成功领取推广钻石%i！" % self.adsdiamond, 1)
            self.adsdiamond = 0

    def ads_buy(self, id):
        if id == 1 and self.adspoint > 99:
            self.ticket1 += 3
            self.ticket2 += 3
            self.adspoint -= 100
            self.client.errorInfo("成功兑换门票！", 1)
        if id == 2 and self.adspoint > 199:
            self.GAMEGOLD += 100000
            self.adspoint -= 200
            self.client.errorInfo("成功兑换10万金币！", 1)
        if id == 3 and self.adspoint > 299:
            self.cell.poweropen()
            self.adspoint -= 300
            self.client.errorInfo("狂暴之力开启成功！", 1)
        if id == 4 and self.adspoint > 2999:
            if self.inventory.getbagsempty() > 0:
                self.inventory.addItem(1, 1, 0, 0, 0, 0, 0, 0)
                self.adspoint -= 3000
                self.refreshItem()
            else:
                self.client.errorInfo("背包空格不足1！", 2)
                return
            self.client.errorInfo("成功兑换宠物蛋1枚！", 1)


    def ups_up(self, index, type, issafe):
        if self.getitemcount(46) >= (self.ups[index] + 1) * 10:
            uprate = 0
            downrate = 0
            if self.ups[index] == 0:
                uprate = 100
                downrate = 0
            if self.ups[index] == 1:
                uprate = 90
                downrate = 0
            if self.ups[index] == 2:
                uprate = 80
                downrate = 0
            if self.ups[index] == 3:
                uprate = 70
                downrate = 0
            if self.ups[index] == 4:
                uprate = 60
                downrate = 0
            if self.ups[index] == 5:
                uprate = 50
                downrate = 0
            if self.ups[index] == 6:
                uprate = 40
                downrate = 0
            if self.ups[index] == 7:
                uprate = 30
                downrate = 0
            if self.ups[index] == 8:
                uprate = 30
                downrate = 0
            if self.ups[index] == 9:
                uprate = 30
                downrate = 0
            if self.ups[index] == 10:
                uprate = 20
                downrate = 50
            if self.ups[index] == 11:
                uprate = 20
                downrate = 60
            if self.ups[index] == 12:
                uprate = 15
                downrate = 70
            if self.ups[index] == 13:
                uprate = 15
                downrate = 75
            if self.ups[index] == 14:
                uprate = 10
                downrate = 80
            if self.ups[index] == 15:
                self.client.errorInfo("已经满级！", 1)
                return
            if issafe == 1:
                if self.ups[index] < 10:
                    self.client.errorInfo("低于10级无法使用保护符！", 1)
                    return
                if self.getitemcount(47) > 0 :
                    if type == 1:
                        if self.GAMEGOLD >= (self.ups[index] + 1) * 10000 :
                            self.GAMEGOLD -= (self.ups[index] + 1) * 10000
                        else:
                            self.client.errorInfo("金币不足！", 1)
                            return
                    if type == 2:
                        if self.GAMEDIAMOND >= (self.ups[index] + 1) * 50:
                            self.GAMEDIAMOND -= (self.ups[index] + 1) * 50
                        else:
                            self.client.errorInfo("钻石不足！", 1)
                            return
                    self.usritems(46, (self.ups[index] + 1) * 10)
                    self.usritems(47, 1)
                    if random.randint(0, 100) < uprate:
                        self.ups[index] += 1
                        self.ups = self.ups
                        self.client.errorInfo("升级成功！", 1)
                        self.updatePropertys()
                    else:
                        self.client.errorInfo("升级失败！", 1)
                else:
                    self.client.errorInfo("升级保护符不足！", 1)
                    return
            else:
                if type == 1:
                    if self.GAMEGOLD >= (self.ups[index] + 1) * 10000:
                        self.GAMEGOLD -= (self.ups[index] + 1) * 10000
                    else:
                        self.client.errorInfo("金币不足！", 1)
                        return
                if type == 2:
                    if self.GAMEDIAMOND >= (self.ups[index] + 1) * 50:
                        self.GAMEDIAMOND -= (self.ups[index] + 1) * 50
                    else:
                        self.client.errorInfo("钻石不足！", 1)
                        return
                self.usritems(46, (self.ups[index] + 1) * 10)
                if random.randint(0, 100) < uprate:
                    self.ups[index] += 1
                    self.ups = self.ups
                    self.client.errorInfo("升级成功！", 1)
                    self.updatePropertys()
                else:
                    if random.randint(0, 100) < downrate:
                        if self.ups[index] > 9:
                            self.ups[index] -= 1
                            self.ups = self.ups
                            self.client.errorInfo("升级失败，等级-1！", 1)
                            self.updatePropertys()
                            return
                    self.client.errorInfo("升级失败！", 1)

        else:
            self.client.errorInfo("火陨石不足%i！" % ((self.ups[index] + 1) * 10) , 1)


    def checkshoptime(self):
        tmpstr = str(time.strftime('%Y%m%d', time.localtime(time.time())))
        if len(self.shoplimit) < 1:
            self.shoplimit = [1,5,5,5,3,1,3,1,1,10,1,11]
        if tmpstr == str(self.shoptime):
            return
        else:
            mfddays = self.shoplimit[11] - 1
            if mfddays <= 0:
                mfddays = 0
            self.shoptime = tmpstr
            self.shoplimit = [1,5,5,5,3,1,3,1,1,10,1,mfddays]

    def checkjinglitime(self):
        tmpstr = str(time.strftime('%Y%m%d', time.localtime(time.time())))
        if tmpstr == str(self.jinglitime):
            return
        else:
            self.jinglitime = tmpstr
            self.cell.addjingli(200)

    def checkhalltime(self):
        tmpstr = str(time.strftime('%Y%m%d', time.localtime(time.time())))
        if tmpstr == str(self.halltime):
            return
        else:
            self.halltime = tmpstr
            self.halllevel = 1

    def starthall(self, spacecell):
        spacecell.hallspawn(self.halllevel)

    def addhalllevel(self, v):
        self.halllevel += v

    def buyshop(self, id):
        if id == 0 :
            if self.shoplimit[0] > 0:
                if self.GAMEDIAMOND > 99:
                    self.GAMEDIAMOND -= 100
                    self.shoplimit[0] -= 1
                    self.GAMEGOLD += 100000
                    self.client.errorInfo("购买成功！", 1)
                    self.shoplimit = self.shoplimit
                else:
                    self.client.errorInfo("钻石不足！", 1)
            else:
                self.client.errorInfo("今日无法购买！", 1)
        if id == 1 :
            if self.shoplimit[1] > 0:
                if self.GAMEDIAMOND > 49:
                    self.GAMEDIAMOND -= 50
                    self.shoplimit[1] -= 1
                    self.ticket1 += 1
                    self.client.errorInfo("购买成功！", 1)
                    self.shoplimit = self.shoplimit
                else:
                    self.client.errorInfo("钻石不足！", 1)
            else:
                self.client.errorInfo("今日无法购买！", 1)
        if id == 2 :
            if self.shoplimit[2] > 0:
                if self.GAMEDIAMOND > 99:
                    self.GAMEDIAMOND -= 100
                    self.shoplimit[2] -= 1
                    self.ticket2 += 1
                    self.client.errorInfo("购买成功！", 1)
                    self.shoplimit = self.shoplimit
                else:
                    self.client.errorInfo("钻石不足！", 1)
            else:
                self.client.errorInfo("今日无法购买！", 1)
        if id == 3 :
            if self.shoplimit[3] > 0:
                if self.GAMEDIAMOND > 99:
                    self.GAMEDIAMOND -= 100
                    self.shoplimit[3] -= 1
                    self.ys1 += 100
                    self.client.errorInfo("购买成功！", 1)
                    self.shoplimit = self.shoplimit
                else:
                    self.client.errorInfo("钻石不足！", 1)
            else:
                self.client.errorInfo("今日无法购买！", 1)
        if id == 4 :
            if self.shoplimit[4] > 0:
                if self.GAMEDIAMOND > 199:
                    self.GAMEDIAMOND -= 200
                    self.shoplimit[4] -= 1
                    self.ys2 += 100
                    self.client.errorInfo("购买成功！", 1)
                    self.shoplimit = self.shoplimit
                else:
                    self.client.errorInfo("钻石不足！", 1)
            else:
                self.client.errorInfo("今日无法购买！", 1)
        if id == 5 :
            if self.shoplimit[5] > 0:
                if self.GAMEDIAMOND > 299:
                    self.GAMEDIAMOND -= 300
                    self.shoplimit[5] -= 1
                    self.ys3 += 100
                    self.client.errorInfo("购买成功！", 1)
                    self.shoplimit = self.shoplimit
                else:
                    self.client.errorInfo("钻石不足！", 1)
            else:
                self.client.errorInfo("今日无法购买！", 1)
        if id == 6 :
            if self.shoplimit[6] > 0:
                if self.GAMEDIAMOND > 199:
                    self.GAMEDIAMOND -= 200
                    self.shoplimit[6] -= 1
                    self.giveitem(46, 100)
                    self.client.errorInfo("购买成功！", 1)
                    self.shoplimit = self.shoplimit
                else:
                    self.client.errorInfo("钻石不足！", 1)
            else:
                self.client.errorInfo("今日无法购买！", 1)
        if id == 7 :
            if self.shoplimit[7] > 0:
                if self.GAMEDIAMOND > 999:
                    self.GAMEDIAMOND -= 1000
                    self.shoplimit[7] -= 1
                    self.giveitem(47, 10)
                    self.client.errorInfo("购买成功！", 1)
                    self.shoplimit = self.shoplimit
                else:
                    self.client.errorInfo("钻石不足！", 1)
            else:
                self.client.errorInfo("今日无法购买！", 1)
        if id == 8 :
            if self.shoplimit[8] > 0:

                if self.GAMEDIAMOND > 799:
                    if self.inventory.getbagsempty() > 0:
                        self.inventory.addItem(1, 1, 0, 0, 0, 0, 0, 0)
                        self.refreshItem()
                        self.GAMEDIAMOND -= 800
                        self.shoplimit[8] -= 1
                        self.client.errorInfo("购买成功！", 1)
                        self.shoplimit = self.shoplimit
                    else:
                        self.client.errorInfo("背包空格不足1！", 2)
                        return
                else:
                    self.client.errorInfo("钻石不足！", 1)
            else:
                self.client.errorInfo("今日无法购买！", 1)
        if id == 9 :
            if self.shoplimit[9] > 0:
                if self.GAMEDIAMOND > 99:
                    self.GAMEDIAMOND -= 100
                    self.shoplimit[9] -= 1
                    self.cell.addjingli(10)
                    self.client.errorInfo("购买成功！", 1)
                    self.shoplimit = self.shoplimit
                else:
                    self.client.errorInfo("钻石不足！", 1)
            else:
                self.client.errorInfo("今日无法购买！", 1)
        if id == 10 :
            if self.shoplimit[10] > 0:

                if self.GAMEDIAMOND > 999:
                    self.cell.addEXP(50000000)
                    self.GAMEDIAMOND -= 1000
                    self.shoplimit[10] -= 1
                    self.client.errorInfo("经验增加5000万！", 1)
                    self.shoplimit = self.shoplimit
                else:
                    self.client.errorInfo("钻石不足！", 1)
            else:
                self.client.errorInfo("无法购买！", 1)
        if id == 11 :
            if self.shoplimit[11] > 0:

                if self.GAMEDIAMOND > 38799:
                    self.cell.skill_update(7)
                    self.GAMEDIAMOND -= 38800
                    self.shoplimit[11] = 0
                    self.client.errorInfo("技能学习成功！", 1)
                    self.shoplimit = self.shoplimit
                else:
                    self.client.errorInfo("钻石不足！", 1)
            else:
                self.client.errorInfo("无法购买！", 1)



    def getpaykey(self, type, price):
        UID = "27a8f0d56ca619d60d7c675b"
        NOTIFY_URL = "http://" + self.addip + ":30041"
        RETURN_URL = "http://www.scdalu.com"
        paramMap = {}
        paramMap["uid"] = UID
        paramMap["notify_url"] = NOTIFY_URL
        paramMap["return_url"] = RETURN_URL
        paramMap["istype"] = type
        paramMap["orderid"] = str(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())))
        paramMap["orderuid"] = self.accountEntity.__ACCOUNT_NAME__
        paramMap["price"] = str(price)
        paramMap["key"] = self.getKey(paramMap)
        DEBUG_MSG(paramMap)
        self.client.sendpaykey(paramMap["key"], paramMap["orderid"], paramMap["orderuid"])
        # KBEngine.executeRawDatabaseCommand("SELECT `content` FROM `kbe`.`board` ORDER BY CreateTime desc LIMIT 1" , self.sqlcb_1)
        rowValue = {"istype": type, "orderid": paramMap["orderid"], "dbid": self.databaseID,
                    "user": paramMap["orderuid"], "price": paramMap["price"], "avatar": self.nameB}
        sql = self.getInsertSql("orders", rowValue)
        print(sql)
        KBEngine.executeRawDatabaseCommand(sql, self.sql_order)

    def sql_order(self, result, rows, insertid, error):
        print(result, rows, insertid, error)

    def getInsertSql(self, dbtable, datas):
        sqlstr = "INSERT INTO "
        sqlstr = sqlstr + dbtable + "(istype, orderid, dbid, user, price, avatar) values" + "('" + str(
            datas["istype"]) + "','" + datas["orderid"] + "','" + str(datas["dbid"]) + "','" + datas[
                     "user"] + "','" + str(datas["price"]) + "','" + datas["avatar"] + "')"
        return sqlstr

    def getKey(self, remoteMap):
        TOKEN = "82ea3040998bf5deab26213a96f18fda"
        key = ""
        key += str(remoteMap["istype"])
        key += remoteMap["notify_url"]
        key += remoteMap["orderid"]
        key += remoteMap["orderuid"]
        key += str(remoteMap["price"])
        key += remoteMap["return_url"]
        key += TOKEN
        key += remoteMap["uid"]
        return hashlib.md5(key.encode(encoding='UTF-8')).hexdigest()

    def admin_getid(self, name):
        sqlstr = "SELECT id FROM `kbe`.`tbl_avatar` WHERE sm_name = '" + name + "'"
        print(sqlstr)
        KBEngine.executeRawDatabaseCommand(sqlstr, self.sql_adminid)

    def sql_adminid(self, result, rows, insertid, error):
        ERROR_MSG("管理")
        self.client.re_dbidback(int(result[0][0].decode('UTF-8')))

    def admin_set(self, dbid, gold, money, diamond, adspoint, band):
        print(dbid, gold, money, diamond, adspoint, band)
        print(dbid / 2386)
        KBEngine.createEntityFromDBID("Avatar", int(dbid / 2386), Functor.Functor(self.adminsetback, gold, money, diamond, adspoint, band))

    def adminsetback(self,gold, money, diamond, adspoint, band, baseRef, dbid, wasActive):
        print(dbid, gold, money, diamond, adspoint, band)
        if baseRef is None:  # 不存在
            return
        baseRef.GAMEGOLD += gold
        baseRef.money += money
        baseRef.GAMEDIAMOND += diamond
        baseRef.adspoint += adspoint
        baseRef.isband = band
        baseRef.ysexp += diamond
        if baseRef.adspoint < 0:
            baseRef.adspoint = 0
        if wasActive:  # 在线
            return
        # 不在线
        baseRef.destroy()

    def onTimer(self, tid, userArg):
        """
		KBEngine method.
		引擎回调timer触发
		"""
        if userArg == 2223:
            self.ups = self.ups

        if userArg == 2222:
            self.checkshoptime()
            self.checkjinglitime()
            self.checkhalltime()
            self.lasttime = int(time.time())
            if len(self.tradeback) > 0:
                self.sendtradeback()

            self.ys1 = self.ys1
            self.ys2 = self.ys2
            self.ys3 = self.ys3
            self.yslevel = self.yslevel
            if self.yslevel == 1 and self.ys1 > 1000:
                self.yslevel += 1
                self.ys1 -= 1000
                self.client.errorInfo("要塞升级成功！", 1)
                self.updatePropertys()
            if self.yslevel == 2 and self.ys1 > 1000:
                self.yslevel += 1
                self.ys1 -= 1000
                self.client.errorInfo("要塞升级成功！", 1)
                self.updatePropertys()
            if self.yslevel == 3 and self.ys1 > 1000 and self.ys2 > 1000:
                self.yslevel += 1
                self.ys1 -= 1000
                self.ys2 -= 1000
                self.client.errorInfo("要塞升级成功！", 1)
                self.updatePropertys()
            if self.yslevel == 4 and self.ys1 > 1000 and self.ys2 > 1000:
                self.yslevel += 1
                self.ys1 -= 1000
                self.ys2 -= 1000
                self.client.errorInfo("要塞升级成功！", 1)
                self.updatePropertys()
            if self.yslevel == 5 and self.ys1 > 1000 and self.ys2 > 1000:
                self.yslevel += 1
                self.ys1 -= 1000
                self.ys2 -= 1000
                self.client.errorInfo("要塞升级成功！", 1)
                self.updatePropertys()
            if self.yslevel == 6 and self.ys1 > 1000 and self.ys2 > 1000 and self.ys3 > 1000:
                self.yslevel += 1
                self.ys1 -= 1000
                self.ys2 -= 1000
                self.ys3 -= 1000
                self.client.errorInfo("要塞升级成功！", 1)
                self.updatePropertys()
            if self.yslevel == 7 and self.ys1 > 1000 and self.ys2 > 1000 and self.ys3 > 1000:
                self.yslevel += 1
                self.ys1 -= 1000
                self.ys2 -= 1000
                self.ys3 -= 1000
                self.client.errorInfo("要塞升级成功！", 1)
                self.updatePropertys()
            if self.yslevel == 8 and self.ys1 > 1000 and self.ys2 > 1000 and self.ys3 > 1000:
                self.yslevel += 1
                self.ys1 -= 1000
                self.ys2 -= 1000
                self.ys3 -= 1000
                self.client.errorInfo("要塞升级成功！", 1)
                self.updatePropertys()
            if self.yslevel == 9 and self.ys1 > 2000 and self.ys2 > 2000 and self.ys3 > 2000:
                self.yslevel += 1
                self.ys1 -= 2000
                self.ys2 -= 2000
                self.ys3 -= 2000
                self.client.errorInfo("要塞升级成功！", 1)
                self.updatePropertys()
            if self.yslevel == 10 and self.ys1 > 3000 and self.ys2 > 3000 and self.ys3 > 3000:
                self.yslevel += 1
                self.ys1 -= 3000
                self.ys2 -= 3000
                self.ys3 -= 3000
                self.client.errorInfo("要塞升级成功！", 1)
                self.updatePropertys()
            if self.yslevel == 11 and self.ys1 > 4000 and self.ys2 > 4000 and self.ys3 > 4000:
                self.yslevel += 1
                self.ys1 -= 4000
                self.ys2 -= 4000
                self.ys3 -= 4000
                self.client.errorInfo("要塞升级成功！", 1)
                self.updatePropertys()
            if self.yslevel == 12 and self.ys1 > 5000 and self.ys2 > 5000 and self.ys3 > 5000:
                self.yslevel += 1
                self.ys1 -= 5000
                self.ys2 -= 5000
                self.ys3 -= 5000
                self.client.errorInfo("要塞升级成功！", 1)
                self.updatePropertys()

        if userArg == 1111:
            self.logouting(1)

    def onDestroy(self):
        """
		KBEngine method.
		entity销毁
		"""
        DEBUG_MSG("Avatar::onDestroy: %i." % self.id)
        return
        if self.accountEntity != None:
            self.accountEntity.activeAvatar = None
            self.accountEntity = None



