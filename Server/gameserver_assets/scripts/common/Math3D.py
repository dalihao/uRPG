# -*- coding: utf-8 -*-
import sys
import KBEngine




class Sector( Area ):
	def __init__( self, parent ):
		"""
		构造函数。
		"""
		Area.__init__( self, parent )
		self.radius = 2.0
		self.angle = 120 / 2

	def load( self, dictDat ):
		self.radius = dictDat["value1"]
		self.angle = dictDat["value2"] / 2

	def inArea( self, caster, entity, transmitDir ):
		"""
		实体是否在扇形范围内
		"""
		srcPos = Math.Vector3( caster.position )
		srcPos.y = 0

		desPos = Math.Vector3( entity.position )
		desPos.y = 0

		desDir = desPos - srcPos
		desDir.y = 0
		desDir.normalise()

		an = transmitDir.dot( desDir )

		if an < -1:
			an = -1

		if an == 0:	 # 刚好与施法者在同一个位置
			an = 1

		if an > 1:
			an = 1

		angle = int( math.acos( an ) / 3.1415926 * 180 )
		if angle <= self.angle:	# 小于或等于夹角
			return True
			
		return False