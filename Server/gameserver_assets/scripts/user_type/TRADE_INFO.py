# -*- coding: utf-8 -*-
import KBEngine
import GlobalConst
from KBEDebug import *

class TTradeInfo(list):
	"""
	"""
	def __init__(self):
		"""
		"""
		list.__init__(self)
		
	def asDict(self):
		data = {
			"UUID"			: self[0],
			"itemCount"		: self[1],
			"itemIndex"		: self[2],
			"saler"		: self[3],
			"startprice"		: self[4],
			"nowprice"		: self[5],
			"time"		: self[6],
			"buyer"		: self[7],
		}
		return data

	def createFromDict(self, dictData):
		self.extend([dictData["UUID"],  dictData["itemCount"], dictData["itemIndex"], dictData["saler"], dictData["startprice"], dictData["nowprice"], dictData["time"], dictData["buyer"]])
		return self
		
class TRADE_INFO_PICKLER:
	def __init__(self):
		pass

	def createObjFromDict(self, dct):
		return TTradeInfo().createFromDict(dct)

	def getDictFromObj(self, obj):
		return obj.asDict()

	def isSameType(self, obj):
		return isinstance(obj, TTradeInfo)

trade_info_inst = TRADE_INFO_PICKLER()

class TTradeInfoList(dict):
	"""
	"""
	def __init__(self):
		"""
		"""
		dict.__init__(self)
		
	def asDict(self):
		datas = []
		dct = {"values" : datas}

		for key, val in self.items():
			datas.append(val)
			
		return dct

	def createFromDict(self, dictData):
		for data in dictData["values"]:
			self[data[0]] = data
		return self
		
class AVATAR_INFO_LIST_PICKLER:
	def __init__(self):
		pass

	def createObjFromDict(self, dct):
		return TTradeInfoList().createFromDict(dct)

	def getDictFromObj(self, obj):
		return obj.asDict()

	def isSameType(self, obj):
		return isinstance(obj, TTradeInfoList)

trade_info_list_inst = AVATAR_INFO_LIST_PICKLER()