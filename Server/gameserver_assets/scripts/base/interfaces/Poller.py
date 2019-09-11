# -*- coding: utf-8 -*-
import KBEngine
import Functor
import socket
import urllib.parse
import hashlib
from KBEDebug import *

class Poller:
	"""
	演示：
	可以向kbengine注册一个socket，由引擎层的网络模块处理异步通知收发。
	用法: 
	from Poller import Poller
	poller = Poller()
	
	开启(可在onBaseappReady执行)
	poller.start("localhost", 12345)
	
	停止
	poller.stop()
	"""
	def __init__(self):
		self._socket = None
		self._clients = {}
		
	def start(self, addr, port):
		"""
		virtual method.
		"""
		self._socket = socket.socket()
		self._socket.bind((addr, port))
		self._socket.listen(10)
		
		KBEngine.registerReadFileDescriptor(self._socket.fileno(), self.onRecv)
		# KBEngine.registerWriteFileDescriptor(self._socket.fileno(), self.onWrite)

	def stop(self):
		if self._socket:
			KBEngine.deregisterReadFileDescriptor(self._socket.fileno())
			self._socket.close()
			self._socket = None
		
	def onWrite(self, fileno):
		pass
		
	def onRecv(self, fileno):
		if self._socket.fileno() == fileno:
			sock, addr = self._socket.accept()
			self._clients[sock.fileno()] = (sock, addr)
			KBEngine.registerReadFileDescriptor(sock.fileno(), self.onRecv)
			DEBUG_MSG("Poller::onRecv: new channel[%s/%i]" % (addr, sock.fileno()))
		else:
			sock, addr = self._clients.get(fileno, None)
			if sock is None:
				return

			data = sock.recv(20480)
			DEBUG_MSG("Poller::onRecv: %s/%i get data, size=%i .decode('UTF-8')" % (addr, sock.fileno(), len(data)))

			sock.send("HTTP/1.1 200".encode())
			KBEngine.deregisterReadFileDescriptor(sock.fileno())
			sock.close()
			del self._clients[fileno]
			self.processData(sock, data)

	def processData(self, sock, datas):
		"""
		处理接收数据
		"""
		params = urllib.parse.parse_qs(datas.decode('UTF-8')[datas.decode('UTF-8').find('paysapi_id'):], keep_blank_values=False, encoding='utf-8', strict_parsing=False,
									   errors='replace')
		if len(params) == 0:
			return

		if params["orderid"][0] == None or params["orderuid"][0] == None or params["paysapi_id"][0] == None or params["price"][0] == None or params["realprice"][0] == None :
			return
		paramMap = {}
		paramMap["orderid"] = params["orderid"][0]
		paramMap["orderuid"] = params["orderuid"][0]
		paramMap["paysapi_id"] = params["paysapi_id"][0]
		paramMap["price"] = params["price"][0]
		paramMap["realprice"] = params["realprice"][0]
		paramMap["key"] = self.getKey(paramMap)
		orderid = params["orderid"][0]
		realprice = float(params["realprice"][0])

		if paramMap["key"] == params["key"][0]:
			print("key相同")
			sqlstr = "SELECT * FROM `kbe`.`orders` WHERE `orderid` = " + orderid
			KBEngine.executeRawDatabaseCommand(sqlstr, Functor.Functor(self.sqlback, realprice))

	def sqlback(self, realprice, result, rows, insertid, error):
		#print(result, rows, insertid, error)
		if error == None and len(result) > 0:
			print(result)
			orderid = result[0][2].decode('UTF-8')
			d_databaseID = int(result[0][3].decode('UTF-8'))
			state = result[0][6].decode('UTF-8')
			sqlstr = "UPDATE `kbe`.`orders` SET  `price`='" + str(realprice) + "', `state`='success' WHERE `orderid` = " + str(orderid)
			if state == "failure":
				KBEngine.executeRawDatabaseCommand(sqlstr,	Functor.Functor(self.updatestateok, d_databaseID, realprice))

	def updatestateok(self, d_databaseID, realprice, result, rows, insertid, error):
		if error == None:
			#print(result, rows, insertid, error)
			KBEngine.createEntityFromDBID("Avatar", d_databaseID, Functor.Functor(self.updateavatar, realprice))

	def updateavatar(self, realprice, baseRef, dbid, wasActive):
		if baseRef is None:  # 不存在
			return
		diamond = int(realprice * 100)
		if realprice > 99:
			diamond = int(realprice * 100) * 1.05
		if realprice > 197:
			diamond = int(realprice * 100) * 1.1
		if realprice > 397:
			diamond = int(realprice * 100) * 1.2
		if realprice > 597:
			diamond = int(realprice * 100) * 1.25
		if realprice > 887:
			diamond = int(realprice * 100) * 1.3

		print("充值成功:%i" % diamond)
		baseRef.GAMEDIAMOND += int(diamond)
		baseRef.money += int(realprice)
		if baseRef.adswho != 0:
			KBEngine.createEntityFromDBID("Avatar", int(baseRef.adswho / 2386), Functor.Functor(self.adsback3, realprice, diamond))
		if wasActive:  # 在线
			return
		# 不在线
		baseRef.destroy()

	def adsback3(self, realprice, diamond, baseRef, dbid, wasActive):
		if baseRef is None:  # 不存在
			return
		baseRef.adspoint += int(10 * realprice)
		baseRef.adsdiamond += int(0.1 * diamond)
		if wasActive:  # 在线
			return
		# 不在线
		baseRef.destroy()

	def getKey(self, remoteMap):
		TOKEN = "82ea3040998bf5deab26213a96f18fda"
		key = ""
		key += str(remoteMap["orderid"])
		key += remoteMap["orderuid"]
		key += remoteMap["paysapi_id"]
		key += str(remoteMap["price"])
		key += str(remoteMap["realprice"])
		key += TOKEN
		return hashlib.md5(key.encode(encoding='UTF-8')).hexdigest()

