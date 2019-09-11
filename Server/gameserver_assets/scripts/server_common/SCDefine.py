# -*- coding: utf-8 -*-
import KBEngine
import GlobalConst
from KBEDebug import * 


# 服务端timer定义
TIMER_TYPE_BUFF_TICK								= 1 # buff的tick
TIMER_TYPE_SPACE_SPAWN_TICK							= 2 # space出生怪
TIMER_TYPE_CREATE_SPACES							= 3 # 创建space
TIMER_TYPE_DESTROY									= 4 # 延时销毁entity
TIMER_TYPE_HEARDBEAT								= 5	# 心跳
TIMER_TYPE_FIGTH_WATI_INPUT_TIMEOUT					= 6	# 战斗回合等待用户输入超时
TIMER_TYPE_SPAWN									= 7	# 出生点出生timer
TIMER_TYPE_SPAWNWORLD5									= 16	# 出生点出生timer
TIMER_TYPE_SPAWNWORLD10									= 17	# 出生点出生timer
TIMER_TYPE_SPAWNWORLD15									= 18	# 出生点出生timer
TIMER_TYPE_DESTROY									= 8	# entity销毁

TIMER_TYPE_CREATE_SPACESPERSON						= 9 # 销毁定时
TIMER_TYPE_MABI					= 10 # 麻痹恢复
TIMER_TYPE_ADDHP					= 11 # 自动回复HP
TIMER_TYPE_SENDTRADE				= 12 # 获取交易
TIMER_TYPE_DAOJISHI1				= 13 # 倒计时1
TIMER_TYPE_DAOJISHI2				= 14 # 倒计时2
TIMER_TYPE_DAOJISHI3				= 15 # 倒计时3

# 物品消失时间秒
TIMER_DESTROY_ITEMSEC						= 180
TIMER_CANPICK_ITEMSEC						= 30