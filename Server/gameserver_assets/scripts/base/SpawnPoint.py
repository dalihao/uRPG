# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
from interfaces.GameObject import GameObject

class SpawnPoint(KBEngine.Entity, GameObject):
	def __init__(self):
		KBEngine.Entity.__init__(self)
		GameObject.__init__(self)
		self.createCellEntity(self.createToCell)

	def sendChatMessage(self, msg):
		DEBUG_MSG("allplayers[%i].sendChatMessage:%s" % (self.id, msg))
		if msg[0:5] == "snnui":
			for player in KBEngine.entities.values():
				if player.__class__.__name__ == "Avatar":
					player.client.ReceiveChatMessage(msg)
			return

