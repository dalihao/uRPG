# -*- coding: utf-8 -*-
import KBEngine
import time
import copy
import Functor
import random
from KBEDebug import *
from interfaces.GameObject import GameObject
from TRADE_INFO import TTradeInfo

class trade(KBEngine.Entity, GameObject):
	def __init__(self):
		KBEngine.Entity.__init__(self)
		GameObject.__init__(self)
		KBEngine.globalData["trade"] = self
		self.addTimer(1, 60, 1111)


	def createsuccess(self, issuccess, basecall):
		DEBUG_MSG(issuccess)

	def addtrade(self, user, itemid, price):
		tradeinfo = TTradeInfo()
		itemUUID = KBEngine.genUUID64()
		tradeinfo.extend([itemUUID, 1, itemid, user.databaseID, price, price, int(time.time()+86400 + random.randint(600, 7200)), 0])
		self.tradeList[itemUUID] = tradeinfo

	def reqtradeslist(self, user, page):
		firstget = 1
		if page == -1:
			firstget = -1
			page = 1
		templist = copy.deepcopy(self.tradeList)
		templist.clear()
		maxi = page * 5
		mini = maxi - 5
		i = 0
		for key, info in self.tradeList.items():
			if int(info[6]) - 86400 > int(time.time()):
				continue
			i += 1
			if i <= maxi and i > mini :
				templist[info[0]] = info
				if user.databaseID == info[3]:
					templist[info[0]][7] = 1
				else:
					templist[info[0]][7] = 0
		if len(templist) == 0 and firstget == -1:
			user.client.reqtradeslist(templist, page)
			return
		if len(templist) == 0 and page == -1:
			user.client.reqtradeslist(templist, page)
			user.client.errorInfo("没有物品售卖", 1)
			return
		if len(templist) == 0:
			user.client.errorInfo("已经到最后一页", 1)
			return
		user.client.reqtradeslist(templist, page)
		print(templist)

	def buyok(self, uid):
		databaseID = self.tradeList[uid][3]
		price = self.tradeList[uid][4]
		itemid = self.tradeList[uid][2]
		del self.tradeList[uid]
		KBEngine.createEntityFromDBID("Avatar", databaseID, Functor.Functor(self.buyresult, price, itemid))


	def buyresult(self,price,itemid, baseRef, dbid, wasActive):
		if baseRef is None:  #不存在
			return
		baseRef.GAMEDIAMOND += price
		baseRef.tradeselllogs.insert(0, price)
		baseRef.tradeselllogs.insert(0, itemid)
		del baseRef.tradeselllogs[-1]
		del baseRef.tradeselllogs[-1]
		baseRef.tradeselllogs = baseRef.tradeselllogs
		if baseRef.tradenotsell[0] == itemid and baseRef.tradenotsell[1] == price:
			del baseRef.tradenotsell[0]
			del baseRef.tradenotsell[0]
			baseRef.tradenotsell.append(0)
			baseRef.tradenotsell.append(0)
		elif baseRef.tradenotsell[2] == itemid and baseRef.tradenotsell[3] == price:
			del baseRef.tradenotsell[2]
			del baseRef.tradenotsell[2]
			baseRef.tradenotsell.append(0)
			baseRef.tradenotsell.append(0)
		elif baseRef.tradenotsell[4] == itemid and baseRef.tradenotsell[5] == price:
			del baseRef.tradenotsell[4]
			del baseRef.tradenotsell[4]
			baseRef.tradenotsell.append(0)
			baseRef.tradenotsell.append(0)
		elif baseRef.tradenotsell[6] == itemid and baseRef.tradenotsell[7] == price:
			del baseRef.tradenotsell[6]
			del baseRef.tradenotsell[6]
			baseRef.tradenotsell.append(0)
			baseRef.tradenotsell.append(0)
		elif baseRef.tradenotsell[8] == itemid and baseRef.tradenotsell[9] == price:
			del baseRef.tradenotsell[8]
			del baseRef.tradenotsell[8]
			baseRef.tradenotsell.append(0)
			baseRef.tradenotsell.append(0)
		elif baseRef.tradenotsell[10] == itemid and baseRef.tradenotsell[11] == price:
			del baseRef.tradenotsell[10]
			del baseRef.tradenotsell[10]
			baseRef.tradenotsell.append(0)
			baseRef.tradenotsell.append(0)
		elif baseRef.tradenotsell[12] == itemid and baseRef.tradenotsell[13] == price:
			del baseRef.tradenotsell[12]
			del baseRef.tradenotsell[12]
			baseRef.tradenotsell.append(0)
			baseRef.tradenotsell.append(0)
		elif baseRef.tradenotsell[14] == itemid and baseRef.tradenotsell[15] == price:
			del baseRef.tradenotsell[14]
			del baseRef.tradenotsell[14]
			baseRef.tradenotsell.append(0)
			baseRef.tradenotsell.append(0)
		elif baseRef.tradenotsell[16] == itemid and baseRef.tradenotsell[17] == price:
			del baseRef.tradenotsell[16]
			del baseRef.tradenotsell[16]
			baseRef.tradenotsell.append(0)
			baseRef.tradenotsell.append(0)
		elif baseRef.tradenotsell[18] == itemid and baseRef.tradenotsell[19] == price:
			del baseRef.tradenotsell[18]
			del baseRef.tradenotsell[18]
			baseRef.tradenotsell.append(0)
			baseRef.tradenotsell.append(0)
		baseRef.tradenotsell = baseRef.tradenotsell
		if wasActive:  #在线
			return
		#不在线
		baseRef.destroy()

	def showtrades(self):
		for key, info in self.tradeList.items():
			print(key)
			print(info)

	def getpricebyuid(self, uid):
		if uid in self.tradeList:
			return self.tradeList[uid][4]
		else:
			return None

	def getidbyuid(self, uid):
		if uid in self.tradeList:
			return self.tradeList[uid][2]
		else:
			return None

	def timetoclear(self):
		timeoutlist = {}
		delkeys = []
		for key, info in self.tradeList.items():
				if info[6] < time.time():
					if info[3] in timeoutlist:
						timeoutlist[info[3]].append(info[2])
						timeoutlist[info[3]].append(info[4])
					else:
						timeoutlist[info[3]] = [info[2]]
						timeoutlist[info[3]].append(info[4])
					delkeys.append(key)
		for delkey in delkeys:
			del self.tradeList[delkey]
		for  timekey, timeinfo in timeoutlist.items():
			KBEngine.createEntityFromDBID("Avatar", timekey, Functor.Functor(self.timeback,timeinfo))


	def timeback(self, itemlist, baseRef, dbid, wasActive):
		if baseRef is None:  #不存在
			return
		baseRef.tradeback = copy.deepcopy(itemlist)
		if wasActive:  #在线
			return
		#不在线
		baseRef.destroy()

	def onTimer(self, tid, userArg):
		"""
		KBEngine method.
		引擎回调timer触发
					"UUID"			: self[0],
			"itemCount"		: self[1],
			"itemIndex"		: self[2],
			"saler"		: self[3],
			"startprice"		: self[4],
			"nowprice"		: self[5],
			"time"		: self[6],
			"buyer"		: self[7],
		"""
		if 1111 == userArg:
			self.timetoclear()
		GameObject.onTimer(self, tid, userArg)



