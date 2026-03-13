# -*- coding: utf-8 -*-
"""玩家类"""

from typing import List, Optional
from game.card import Card
from game.card_utils import get_card_type, can_beat, sort_cards
from utils.logger import logger


class Player:
    """玩家基类"""

    def __init__(self, player_id: int, name: str, is_ai: bool = True):
        self.player_id = player_id  # 0: 下方(人), 1: 左侧(AI), 2: 右侧(AI)
        self.name = name
        self.is_ai = is_ai
        self.hand_cards: List[Card] = []  # 手牌
        self.played_cards: List[Card] = []  # 已出的牌
        self.score = 0  # 得分
        self.is_landlord = False  # 是否为地主
        self.is_ready = True  # 是否准备

    @property
    def card_count(self) -> int:
        return len(self.hand_cards)

    def receive_cards(self, cards: List[Card]):
        """收到牌"""
        self.hand_cards.extend(cards)
        self.sort_hand()

    def sort_hand(self):
        """整理手牌"""
        self.hand_cards = sort_cards(self.hand_cards)

    def remove_cards(self, cards: List[Card]):
        """打出手牌"""
        for card in cards:
            if card in self.hand_cards:
                self.hand_cards.remove(card)

    def play_cards(self, cards: List[Card]) -> bool:
        """打牌"""
        if not cards:
            return False

        # 检查是否拥有这些牌
        for card in cards:
            if card not in self.hand_cards:
                logger.warning(f"玩家 {self.name} 没有牌: {card}")
                return False

        self.remove_cards(cards)
        self.played_cards.extend(cards)
        logger.info(f"玩家 {self.name} 出牌: {[str(c) for c in cards]}")
        return True

    def get_playable_cards(self, last_cards: Optional[List[Card]]) -> List[List[Card]]:
        """获取可出的牌型组合"""
        if not last_cards:
            # 首家，可以出任意牌
            return self._get_all_possible_plays()

        last_type, last_value = get_card_type(last_cards)
        if last_type is None:
            return []

        possible_plays = []

        # 检查每种牌型
        for card_combo in self._get_all_possible_plays():
            if can_beat(card_combo, last_cards):
                possible_plays.append(card_combo)

        return possible_plays

    def _get_all_possible_plays(self) -> List[List[Card]]:
        """获取所有可能出的牌型组合"""
        possible = []

        # 单张
        for card in self.hand_cards:
            possible.append([card])

        # 对子
        counts = {}
        for card in self.hand_cards:
            counts[card.value] = counts.get(card.value, 0) + 1

        for value, count in counts.items():
            if count >= 2:
                pair = [c for c in self.hand_cards if c.value == value][:2]
                possible.append(pair)

        # 炸弹
        for value, count in counts.items():
            if count >= 4:
                bomb = [c for c in self.hand_cards if c.value == value][:4]
                possible.append(bomb)

        # 王炸
        has_small = any(c.rank == 'joker' for c in self.hand_cards)
        has_big = any(c.rank == 'JOKER' for c in self.hand_cards)
        if has_small and has_big:
            rocket = [c for c in self.hand_cards if c.rank in ('joker', 'JOKER')]
            possible.append(rocket)

        return possible

    def __str__(self):
        return f"Player({self.name}, 手牌:{self.card_count}张, 地主:{self.is_landlord})"

    def __repr__(self):
        return self.__str__()