# -*- coding: utf-8 -*-
import KBEngine
import GlobalConst
from KBEDebug import * 

class TItemInfo(list):
	"""
	"""
	def __init__(self):
		"""
		"""
		list.__init__(self)
		
	def asDict(self):
		data = {
			"UUID"			: self[0],
			"itemId"		: self[1],
			"itemCount"		: self[2],
			"itemIndex"		: self[3],
			"isnew"		: self[4],
			"lucky"		: self[5],
			"arrt1"		: self[6],
			"arrt2"		: self[7],
			"arrt3"		: self[8],
			"arrt4"		: self[9],
			"arrt5"		: self[10],
		}
		
		return data

	def createFromDict(self, dictData):
		self.extend([dictData["UUID"], dictData["itemId"], dictData["itemCount"], dictData["itemIndex"], dictData["isnew"], dictData["lucky"], dictData["arrt1"], dictData["arrt2"], dictData["arrt3"], dictData["arrt4"], dictData["arrt5"]])
		return self
		
class ITEM_INFO_PICKLER:
	def __init__(self):
		pass

	def createObjFromDict(self, dct):
		return TItemInfo().createFromDict(dct)

	def getDictFromObj(self, obj):
		return obj.asDict()

	def isSameType(self, obj):
		return isinstance(obj, TItemInfo)

item_info_inst = ITEM_INFO_PICKLER()

class TItemInfoList(dict):
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
		return TItemInfoList().createFromDict(dct)

	def getDictFromObj(self, obj):
		return obj.asDict()

	def isSameType(self, obj):
		return isinstance(obj, TItemInfoList)

item_info_list_inst = AVATAR_INFO_LIST_PICKLER()