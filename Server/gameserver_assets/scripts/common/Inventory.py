import weakref
import KBEngine
from KBEDebug import *
import copy
import d_items
import random
from ITEM_INFO import TItemInfo


class InventoryMgr:
    """docstring for InventoryMgr"""

    # NOITEM = -1
    def __init__(self, entity):
        self._entity = weakref.proxy(entity)
        # self._curItemIndex = NOITEM
        # 初始化背包索引index to Uid
        self.INVCOUNT = 76;
        self.invIndex2Uids = [0] * self.INVCOUNT
        for key, info in self._entity.itemList.items():
            self.invIndex2Uids[info[3]] = key

        # 初始化仓库索引index to Uid
        self.SINVCOUNT = 100;
        self.storeIndex2Uids = [0] * self.SINVCOUNT
        for key, info in self._entity.storeList.items():
            self.storeIndex2Uids[info[3]] = key

        # 初始化装备索引index to Uid
        self.EQUIPVCOUNT = 15;
        self.equipIndex2Uids = [0] * 15
        for key, info in self._entity.equipItemList.items():
            self.equipIndex2Uids[info[3]] = key

    def checkisfull(self):
        emptyIndex = -1
        for i in range(0, self.INVCOUNT):
            if self.invIndex2Uids[i] == 0:
                emptyIndex = i
                break
        return emptyIndex

    def getbagsempty(self):
        emptycount = 0
        for i in range(0, self.INVCOUNT):
            if self.invIndex2Uids[i] == 0:
                emptycount += 1
        return emptycount

    def getbagsempty(self):
        bagsnum = 0
        for i in range(0, self.INVCOUNT):
            if self.invIndex2Uids[i] == 0:
                bagsnum += 1
        return bagsnum

    def addItem(self, itemId, itemCount, lucky, arrt1, arrt2, arrt3, arrt4, arrt5):
        result = []
        emptyIndex = -1
        for i in range(0, self.INVCOUNT):
            if self.invIndex2Uids[i] == 0:
                emptyIndex = i
                break
        # 背包已经满了
        if emptyIndex == -1:
            INFO_MSG("背包满了！！")
            return result
        # 放置物品
        itemStack = d_items.datas[itemId]['itemStack']

        # 不可堆叠物品
        if itemStack == 1:
            itemUUID = KBEngine.genUUID64()
            iteminfo = TItemInfo()
            iteminfo.extend([itemUUID, itemId, 1, emptyIndex, 1, lucky, arrt1, arrt2, arrt3, arrt4, arrt5])
            self.invIndex2Uids[emptyIndex] = itemUUID
            self._entity.itemList[itemUUID] = iteminfo
            result.append(itemUUID)

        # 可堆叠物品
        else:
            for key, info in self._entity.itemList.items():
                if info[1] == itemId and info[2] < itemStack:
                    info[2] += itemCount
                    info[4] = 1
                    result.append(key)
                    if info[2] > itemStack:
                        itemCount = info[2] - itemStack
                        info[2] = itemStack
                    else:
                        itemCount = 0
                        break

            if itemCount > 0:
                itemUUID = KBEngine.genUUID64()
                iteminfo = TItemInfo()
                iteminfo.extend([itemUUID, itemId, itemCount, emptyIndex, 1, lucky, arrt1, arrt2, arrt3, arrt4, arrt5])
                self.invIndex2Uids[emptyIndex] = itemUUID
                self._entity.itemList[itemUUID] = iteminfo
                result.append(itemUUID)

        return result

    def removeItem(self, itemUUID, itemCount):
        itemId = self._entity.itemList[itemUUID][1]
        itemC = self._entity.itemList[itemUUID][2]
        itemIndex = self._entity.itemList[itemUUID][3]
        if itemCount < itemC:
            self._entity.itemList[itemUUID][2] = itemC - itemCount
            return -1
        else:
            self.invIndex2Uids[itemIndex] = 0
            del self._entity.itemList[itemUUID]
        return itemId

    def swapItem(self, srcIndex, dstIndex):
        srcUid = self.invIndex2Uids[srcIndex]
        dstUid = self.invIndex2Uids[dstIndex]
        self.invIndex2Uids[srcIndex] = dstUid
        if dstUid != 0:
            self._entity.itemList[dstUid][3] = srcIndex
        self.invIndex2Uids[dstIndex] = srcUid
        if srcUid != 0:
            self._entity.itemList[srcUid][3] = dstIndex

    # 整理背包
    def refreshItem(self, user):
        self.invIndex2Uids.sort(reverse=True)
        for i in range(0, self.INVCOUNT):
            if self.invIndex2Uids[i] > 0:
                self._entity.itemList[self.invIndex2Uids[i]][3] = i

        self.storeIndex2Uids.sort(reverse=True)
        for x in range(0, self.SINVCOUNT):
            if self.storeIndex2Uids[x] > 0:
                self._entity.storeList[self.storeIndex2Uids[x]][3] = x
        user.client.onReqItemList(user.itemList, user.storeList, user.equipItemList)

    # 设置为已查看
    def setnotnew(self, user, itemIndex):
        invUid = self.invIndex2Uids[itemIndex]
        if invUid == 0:
            return
        self._entity.itemList[invUid][4] = 0

    # 装备或脱下
    def equipItem(self, itemIndex, equipIndex):
        invUid = self.invIndex2Uids[itemIndex]
        equipUid = self.equipIndex2Uids[equipIndex]
        # 背包索引位置没有物品
        if invUid == 0 and equipUid == 0:
            return -1

        equipItem = {}

        if equipUid != 0:
            equipItem = self._entity.equipItemList[equipUid]
            del self._entity.equipItemList[equipUid]
            self.equipIndex2Uids[equipIndex] = 0

        if invUid != 0:
            self._entity.equipItemList[invUid] = self._entity.itemList[invUid]
            self._entity.equipItemList[invUid][3] = equipIndex
            self.equipIndex2Uids[equipIndex] = invUid
            del self._entity.itemList[invUid]
            self.invIndex2Uids[itemIndex] = 0

        if equipUid != 0:
            self._entity.itemList[equipUid] = equipItem
            self._entity.itemList[equipUid][3] = itemIndex
            self.invIndex2Uids[itemIndex] = equipUid


    def dropequipitem(self, user):
        dropUID = 0
        templist = []
        for i in range(0, self.EQUIPVCOUNT):
            if self.equipIndex2Uids[i] != 0:
                templist.append(i)
        if len(templist) > 0:
            eqindex = random.sample(templist, 1)[0]
            dropUID = self.equipIndex2Uids[eqindex]

            itemId = self._entity.equipItemList[dropUID][1]
            lucky = self._entity.equipItemList[dropUID][5]
            arrt1 = self._entity.equipItemList[dropUID][6]
            arrt2 = self._entity.equipItemList[dropUID][7]
            arrt3 = self._entity.equipItemList[dropUID][8]
            arrt4 = self._entity.equipItemList[dropUID][9]
            arrt5 = self._entity.equipItemList[dropUID][10]
            user.cell.dropNotify(itemId, dropUID, 1, lucky, arrt1, arrt2, arrt3, arrt4, arrt5, 0)
            if eqindex == 0:
                user.cell.updateweaponeffid(0, 1000)
            del self._entity.equipItemList[dropUID]
            self.equipIndex2Uids[eqindex] = 0

    def dropinvitem(self, user):
        dropUID = 0
        templist = []
        for i in range(0, self.INVCOUNT):
            if self.invIndex2Uids[i] != 0:
                templist.append(i)
        if len(templist) > 0:
            eqindex = random.sample(templist, 1)[0]
            itemUUId = self.invIndex2Uids[eqindex]
            itemCount = self._entity.itemList[itemUUId][2]
            lucky = self._entity.itemList[itemUUId][5]
            arrt1 = self._entity.itemList[itemUUId][6]
            arrt2 = self._entity.itemList[itemUUId][7]
            arrt3 = self._entity.itemList[itemUUId][8]
            arrt4 = self._entity.itemList[itemUUId][9]
            arrt5 = self._entity.itemList[itemUUId][10]
            itemId = self.removeItem(itemUUId, itemCount)
            user.cell.dropNotify(itemId, itemUUId, itemCount, lucky, arrt1, arrt2, arrt3, arrt4, arrt5, 1)


    def sendtostore(self, storeIndex, itemIndex):
        storeUid = self.storeIndex2Uids[storeIndex]
        itemUid = self.invIndex2Uids[itemIndex]
        # 背包索引位置没有物品
        if storeUid == 0 and itemUid == 0:
            return -1
        if storeUid != 0 and itemUid != 0:
            return -1

        invItem = {}
        if itemUid != 0:
            emptyIndex = -2
            for i in range(0, self.SINVCOUNT):
                if self.storeIndex2Uids[i] == 0:
                    emptyIndex = i
                    break
            # 仓库已经满了
            if emptyIndex == -2:
                return emptyIndex
            invItem = self._entity.itemList[itemUid]
            del self._entity.itemList[itemUid]
            self.invIndex2Uids[itemIndex] = 0

        if storeUid != 0:
            emptyIndex = -3
            for i in range(0, self.INVCOUNT):
                if self.invIndex2Uids[i] == 0:
                    emptyIndex = i
                    break
            # 背包已经满了
            if emptyIndex == -3:
                return emptyIndex
            self._entity.itemList[storeUid] = self._entity.storeList[storeUid]
            self._entity.itemList[storeUid][3] = itemIndex
            self.invIndex2Uids[itemIndex] = storeUid
            del self._entity.storeList[storeUid]
            self.storeIndex2Uids[storeIndex] = 0

        if itemUid != 0:
            self._entity.storeList[itemUid] = invItem
            self._entity.storeList[itemUid][3] = storeIndex
            self.storeIndex2Uids[storeIndex] = itemUid

    # 检查是否有装备
    def gethaveitem(self, Index):
        equipUid = self.equipIndex2Uids[Index]
        # 背包索引位置没有物品
        if equipUid == 0:
            return -1
        else:
            return 0

    # 检查是否是空格
    def invgethaveitem(self, Index):
        equipUid = self.invIndex2Uids[Index]
        # 背包索引位置没有物品
        if equipUid == 0:
            return -1
        else:
            return 0

    # 武器升级幸运
    def lucky_w(self, user):
        equipUid = self.equipIndex2Uids[0]
        if equipUid == 0:
            return -1
        if self._entity.equipItemList[equipUid][5] > 6:
            return -1
        lucky = 1
        num = random.randint(self._entity.equipItemList[equipUid][5], 7)
        if num == 7:
            lucky = -1
        self._entity.equipItemList[equipUid][5] += lucky
        user.cell.updateweaponeffid(self._entity.equipItemList[equipUid][1], self._entity.equipItemList[equipUid][5])
        user.reqItemList()
        return 1

    # 项链升级幸运
    def lucky_n(self, user):
        equipUid = self.equipIndex2Uids[3]
        if equipUid == 0:
            return -1
        if self._entity.equipItemList[equipUid][5] > 4:
            return -1
        lucky = 1
        num = random.randint(self._entity.equipItemList[equipUid][5], 5)
        if num == 5:
            lucky = -1
        self._entity.equipItemList[equipUid][5] += lucky
        user.reqItemList()
        return 1

    def getItemUidByIndex(self, itemIndex):
        return self.invIndex2Uids[itemIndex]

    def getEquipUidByIndex(self, equipIndex):
        return self.equipIndex2Uids[equipIndex]

    def getStoreUidByIndex(self, storeIndex):
        return self.storeIndex2Uids[storeIndex]





