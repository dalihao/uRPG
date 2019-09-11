# -*- coding: utf-8 -*-
import KBEngine
import Functor
from KBEDebug import *
import d_entities
import d_spaces
import d_spaces_person
import copy

CONST_WAIT_CREATE = -1


class SpaceAllocDuplicate:
    """
    副本的场景分配器
    """

    def __init__(self, utype):
        self._spaces = {}
        self._utype = utype
        self._pendingLogonEntities = {}  # 副本如果没有创建有哪些人在其中登录，   一旦创建完毕会将他们创建到副本的cellapp上
        self._pendingEnterEntityMBs = {}  # 副本如果没有创建有哪些人请求进入，   一旦创建完毕会将他们扔到副本

    def init(self, dbid):
        """
        virtual method.
        """
        self.createSpace(dbid, {})

    def getSpaces(self):
        return self._spaces

    def createSpace(self, spaceKey, context):
        """
                if spaceKey <= 0:
            spaceKey = KBEngine.genUUID64()
        """

        spaceKey = int(spaceKey)

        DEBUG_MSG("创建====================私人空间===========spaceUType= %i========spacekey= %i" % (self._utype, spaceKey))

        context = copy.copy(context)

        spaceData = d_spaces_person.datas.get(self._utype)

        KBEngine.createEntityAnywhere(spaceData["entityType"], \
                                      {"spaceUType": spaceKey, \
                                       "spaceKey": spaceKey, \
                                       "context": context, \
										"name" : spaceData["name"],	\
                                       }, \
                                      Functor.Functor(self.onSpaceCreatedCB, spaceKey))

    def onSpaceCreatedCB(self, spaceKey, space):
        """
        一个space创建好后的回调
        """
        DEBUG_MSG("副本Spaces::onSpaceCreatedCB: space %i. entityID=%i" % (self._utype, space.id))

    def onSpaceLoseCell(self, spaceKey):
        """
        space的cell创建好了
        """
        del self._spaces[spaceKey]

    def onSpaceGetCell(self, spaceEntityCall, spaceKey):
        """
        space的cell创建好了
        """
        self._spaces[spaceKey] = spaceEntityCall
        pendingLogonEntities = self._pendingLogonEntities.pop(spaceKey, [])
        pendingEnterEntityMBs = self._pendingEnterEntityMBs.pop(spaceKey, [])

        for e, context in pendingLogonEntities:
            self.loginToSpace(e, self._utype, context)

        for mb, pos, dir, context in pendingEnterEntityMBs:
            self.teleportSpace(mb, pos, dir, context)

    def alloc(self, context):
        """
        virtual method.
        分配一个space
        """
        if self._spaces == {}:
            return CONST_WAIT_CREATE
        return list(self._spaces.values())[0]

    def loginToSpace(self, avatarEntity, spaceUType, context):
        """
        virtual method.
        某个玩家请求登陆到某个space中
        """
        spaceKey = int(str(avatarEntity.databaseID) + str(spaceUType))
        space = self.alloc({"spaceKey": spaceKey})
        if space is None:
            ERROR_MSG("Spaces::loginToSpace: not found space %i. login to space is failed! spaces=%s" % (
                self._utype, self._spaces))
            return

        if space == CONST_WAIT_CREATE:
            if spaceKey not in self._pendingLogonEntities:
                self._pendingLogonEntities[spaceKey] = [(avatarEntity, context)]
            else:
                self._pendingLogonEntities[spaceKey].append((avatarEntity, context))

            return

        space.loginToSpace(avatarEntity, context)

    def teleportSpace(self, entityCall, position, direction, context):
        """
        virtual method.
        请求进入某个space中
        """
        space = self.alloc(context)
        if space is None:
            ERROR_MSG("Spaces::teleportSpace: not found space %i. login to space is failed!" % self._utype)
            return

        if space == CONST_WAIT_CREATE:
            spaceKey = context.get("spaceKey", 0)
            DEBUG_MSG("spaceKey_进入副本%i" % spaceKey)
            if spaceKey not in self._pendingEnterEntityMBs:
                self._pendingEnterEntityMBs[spaceKey] = [(entityCall, position, direction, context)]
            else:
                self._pendingEnterEntityMBs[spaceKey].append((entityCall, position, direction, context))

            DEBUG_MSG("Spaces::teleportSpace: avatarEntity=%s add pending." % entityCall.id)
            return

        DEBUG_MSG("Spaces::teleportSpace: entityCall=%s" % entityCall)
        space.teleportSpace(entityCall, position, direction, context)


    # --------------------------------------------------------------------------------------------
    #                              Callbacks
    # --------------------------------------------------------------------------------------------
    def onTimer(self, tid, userArg):
        """
        KBEngine method.
        引擎回调timer触发
        """

