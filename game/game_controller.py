# -*- coding: utf-8 -*-
"""游戏控制器"""

import random
from typing import List, Optional
from game.card import Deck, Card
from game.player import Player
from game.ai_player import AIPlayer
from config import (
    STATE_MENU, STATE_DEALING, STATE_CALLING_LANDLORD,
    STATE_PLAYING, STATE_GAME_OVER, PLAYER_BOTTOM, PLAYER_LEFT, PLAYER_RIGHT
)
from utils.logger import logger

# 叫地主回调函数（供UI调用）
_on_landlord_called = None


def set_landlord_callback(callback):
    """设置叫地主回调"""
    global _on_landlord_called
    _on_landlord_called = callback


class GameController:
    """游戏控制器"""

    def __init__(self):
        self.state = STATE_MENU
        self.deck = Deck()
        self.players: List[Player] = []
        self.landlord_cards: List[Card] = []  # 底牌
        self.landlord_id: Optional[int] = None  # 地主ID
        self.current_player_id: int = 0  # 当前出牌玩家
        self.last_player_id: Optional[int] = None  # 上次出牌玩家
        self.last_cards: Optional[List[Card]] = None  # 上次出的牌
        self.play_history: List[tuple] = []  # 出牌历史

        # 初始化玩家
        self._init_players()

    def _init_players(self):
        """初始化玩家"""
        # 玩家在下方
        self.players.append(Player(PLAYER_BOTTOM, "玩家", is_ai=False))
        # AI在左侧
        self.players.append(AIPlayer(PLAYER_LEFT, "电脑A"))
        # AI在右侧
        self.players.append(AIPlayer(PLAYER_RIGHT, "电脑B"))
        logger.info("玩家初始化完成")

    def start_new_game(self):
        """开始新游戏"""
        logger.info("开始新游戏")
        self.state = STATE_DEALING

        # 重置
        self.deck = Deck()
        self.deck.shuffle()
        self.landlord_cards = []
        self.landlord_id = None
        self.last_cards = None
        self.last_player_id = None
        self.play_history = []

        for player in self.players:
            player.hand_cards = []
            player.played_cards = []
            player.is_landlord = False

        # 发牌
        self._deal_cards()

        # 进入叫地主阶段
        self.state = STATE_CALLING_LANDLORD
        self._call_landlord()

    def _deal_cards(self):
        """发牌"""
        # 发51张牌，每人17张
        for i in range(17):
            for player in self.players:
                cards = self.deck.deal(1)
                player.receive_cards(cards)

        # 留3张底牌
        self.landlord_cards = self.deck.deal(3)
        logger.info(f"底牌: {self.landlord_cards}")

    def _call_landlord(self):
        """叫地主"""
        logger.info("开始叫地主")

        # 随机选择首家叫牌
        first_caller = random.randint(0, 2)

        for i in range(3):
            player = self.players[(first_caller + i) % 3]

            if player.is_ai:
                want_landlord = player.decide_landlord(self.landlord_cards)
            else:
                # 玩家需要手动选择
                want_landlord = True  # 默认叫
                # 这里可以添加UI交互
                logger.info(f"玩家 {player.name} 决定叫地主: {want_landlord}")

            if want_landlord:
                self.landlord_id = player.player_id
                player.is_landlord = True

                # 获得底牌
                player.receive_cards(self.landlord_cards)
                logger.info(f"{player.name} 成为地主，获得底牌: {self.landlord_cards}")

                # 通知UI
                global _on_landlord_called
                if _on_landlord_called:
                    _on_landlord_called(player.player_id, True)
                break
        else:
            # 都没叫，重新发牌
            logger.info("重新发牌")
            self.start_new_game()
            return

        # 进入出牌阶段
        self.state = STATE_PLAYING
        self.current_player_id = self.landlord_id
        logger.info(f"游戏开始，轮到 {self.players[self.current_player_id].name} 出牌")

    def player_play_cards(self, player_id: int, cards: List[Card]) -> bool:
        """玩家出牌"""
        if player_id != self.current_player_id:
            logger.warning(f"不是该玩家的出牌回合")
            return False

        player = self.players[player_id]

        # 检查牌型
        if cards:
            if not player.play_cards(cards):
                return False
            self.last_cards = cards
            self.last_player_id = player_id

        # 记录出牌历史
        self.play_history.append((player_id, cards))

        # 检查是否获胜
        if player.card_count == 0:
            self._game_over(player_id)
            return True

        # 下一家
        self.current_player_id = (self.current_player_id + 1) % 3

        # 检查是否三家都过
        self._check_pass_around()

        return True

    def _check_pass_around(self):
        """检查是否过了一圈"""
        if self.last_player_id is not None:
            next_player = (self.current_player_id + 1) % 3
            if next_player == self.last_player_id:
                # 过了一圈，重置上家牌型
                self.last_cards = None
                self.last_player_id = None
                logger.info("重新轮换，首家可以出任意牌")

    def _game_over(self, winner_id: int):
        """游戏结束"""
        self.state = STATE_GAME_OVER
        winner = self.players[winner_id]
        logger.info(f"游戏结束，{winner.name} 获胜！")

        # 判断胜负
        is_landlord_win = winner.is_landlord
        logger.info(f"{'地主' if is_landlord_win else '农民'}获胜")

    def get_current_player(self) -> Player:
        """获取当前玩家"""
        return self.players[self.current_player_id]

    def is_player_turn(self, player_id: int) -> bool:
        """是否是该玩家的回合"""
        return self.current_player_id == player_id

    def can_play_cards(self, player_id: int, cards: List[Card]) -> bool:
        """检查玩家是否可以出这些牌"""
        if player_id != self.current_player_id:
            return False

        if not cards:
            return True  # 过牌

        player = self.players[player_id]

        # 检查是否拥有这些牌
        for card in cards:
            if card not in player.hand_cards:
                return False

        # 检查是否能管上
        from game.card_utils import can_beat
        if self.last_cards and len(self.last_cards) > 0:
            return can_beat(cards, self.last_cards)

        return True

    def get_game_info(self) -> dict:
        """获取游戏信息"""
        return {
            'state': self.state,
            'landlord_id': self.landlord_id,
            'current_player_id': self.current_player_id,
            'last_player_id': self.last_player_id,
            'landlord_cards': self.landlord_cards,
            'last_cards': self.last_cards,
        }