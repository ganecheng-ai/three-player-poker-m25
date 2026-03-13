# -*- coding: utf-8 -*-
"""游戏配置"""

import os

# 屏幕设置
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "欢乐斗地主"

# 颜色定义
COLOR_GREEN_DARK = (27, 94, 32)      # 深绿背景
COLOR_GREEN_MAIN = (46, 125, 50)     # 主绿色
COLOR_GOLD = (255, 215, 0)           # 金色
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (220, 20, 60)            # 红色(红桃/方片)
COLOR_BLACK_CARD = (30, 30, 30)      # 黑色(黑桃/草花)
COLOR_BG_LIGHT = (240, 255, 240)     # 浅绿
COLOR_TEXT_DARK = (50, 50, 50)
COLOR_BUTTON = (34, 139, 34)
COLOR_BUTTON_HOVER = (46, 125, 50)

# 扑克牌设置
CARD_WIDTH = 90
CARD_HEIGHT = 130
CARD_MARGIN = 10

# 玩家位置
PLAYER_BOTTOM = 0  # 玩家在下方
PLAYER_LEFT = 1    # 左侧电脑
PLAYER_RIGHT = 2   # 右侧电脑

# 游戏状态
STATE_MENU = 0         # 菜单
STATE_DEALING = 1      # 发牌中
STATE_CALLING_LANDLORD = 2  # 叫地主
STATE_PLAYING = 3      # 出牌中
STATE_GAME_OVER = 4    # 游戏结束

# 牌型
CARD_TYPE_SINGLE = 1       # 单张
CARD_TYPE_PAIR = 2         # 对子
CARD_TYPE_TRIPLE = 3       # 三张
CARD_TYPE_STRAIGHT = 4     # 顺子
CARD_TYPE_DOUBLE_STRAIGHT = 5  # 连对
CARD_TYPE_TRIPLE_STRAIGHT = 6  # 飞机
CARD_TYPE_BOMB = 7         # 炸弹
CARD_TYPE_ROCKET = 8       # 王炸

# 资源路径
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
CARDS_DIR = os.path.join(ASSETS_DIR, 'cards')
SOUNDS_DIR = os.path.join(ASSETS_DIR, 'sounds')