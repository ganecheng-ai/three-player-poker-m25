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
        from game.card_utils import (
            is_single, is_pair, is_triple, is_straight,
            is_double_straight, is_triple_straight, is_bomb, is_rocket,
            count_ranks, organize_cards
        )

        possible = []
        counts = count_ranks(self.hand_cards)

        # 单张
        for card in self.hand_cards:
            possible.append([card])

        # 对子
        for value, count in counts.items():
            if count >= 2:
                pair = [c for c in self.hand_cards if c.value == value][:2]
                possible.append(pair)

        # 三张
        for value, count in counts.items():
            if count >= 3:
                triple = [c for c in self.hand_cards if c.value == value][:3]
                possible.append(triple)

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

        # 顺子(5-12张)
        possible.extend(self._find_straights())

        # 连对
        possible.extend(self._find_double_straights())

        # 飞机(不带翅膀)
        possible.extend(self._find_triple_straights())

        # 三带一
        possible.extend(self._find_triple_with_one())

        # 三带二
        possible.extend(self._find_triple_with_two())

        return possible

    def _find_straights(self) -> List[List[Card]]:
        """查找所有顺子"""
        from game.card_utils import is_straight

        straights = []
        # 按牌值分组
        counts = count_ranks(self.hand_cards)
        available_values = sorted([v for v, c in counts.items() if c >= 1 and v < 16], reverse=True)

        # 尝试不同长度的顺子
        for length in range(12, 4, -1):  # 从长到短
            for start_idx in range(len(available_values) - length + 1):
                straight_values = available_values[start_idx:start_idx + length]

                # 检查是否连续
                is_consecutive = all(
                    straight_values[i] - straight_values[i + 1] == 1
                    for i in range(len(straight_values) - 1)
                )
                if is_consecutive:
                    # 构建顺子
                    straight_cards = []
                    for v in straight_values:
                        card = next(c for c in self.hand_cards if c.value == v)
                        straight_cards.append(card)
                    if is_straight(straight_cards):
                        straights.append(straight_cards)

        return straights

    def _find_double_straights(self) -> List[List[Card]]:
        """查找所有连对"""
        from game.card_utils import is_double_straight

        double_straights = []
        counts = count_ranks(self.hand_cards)
        # 找出有对子的值
        pair_values = sorted([v for v, c in counts.items() if c >= 2 and v < 16], reverse=True)

        # 尝试不同长度的连对
        for length in range(10, 2, -1):
            for start_idx in range(len(pair_values) - length + 1):
                straight_values = pair_values[start_idx:start_idx + length]

                # 检查是否连续
                is_consecutive = all(
                    straight_values[i] - straight_values[i + 1] == 1
                    for i in range(len(straight_values) - 1)
                )
                if is_consecutive:
                    # 构建连对
                    ds_cards = []
                    for v in straight_values:
                        cards = [c for c in self.hand_cards if c.value == v][:2]
                        ds_cards.extend(cards)
                    if is_double_straight(ds_cards):
                        double_straights.append(ds_cards)

        return double_straights

    def _find_triple_straights(self) -> List[List[Card]]:
        """查找所有飞机(不带翅膀)"""
        from game.card_utils import is_triple_straight

        triple_straights = []
        counts = count_ranks(self.hand_cards)
        # 找出有三张的值
        triple_values = sorted([v for v, c in counts.items() if c >= 3 and v < 16], reverse=True)

        # 尝试不同长度的飞机
        for length in range(7, 1, -1):
            for start_idx in range(len(triple_values) - length + 1):
                straight_values = triple_values[start_idx:start_idx + length]

                # 检查是否连续
                is_consecutive = all(
                    straight_values[i] - straight_values[i + 1] == 1
                    for i in range(len(straight_values) - 1)
                )
                if is_consecutive:
                    # 构建飞机
                    ts_cards = []
                    for v in straight_values:
                        cards = [c for c in self.hand_cards if c.value == v][:3]
                        ts_cards.extend(cards)
                    if is_triple_straight(ts_cards):
                        triple_straights.append(ts_cards)

        return triple_straights

    def _find_triple_with_one(self) -> List[List[Card]]:
        """查找所有三带一"""
        triples = []
        counts = count_ranks(self.hand_cards)

        # 找出三张
        triple_values = [v for v, c in counts.items() if c >= 3]

        for triple_value in triple_values:
            triple_cards = [c for c in self.hand_cards if c.value == triple_value][:3]

            # 找任意单张作为带牌
            for card in self.hand_cards:
                if card.value != triple_value:
                    combo = triple_cards + [card]
                    triples.append(combo)

        return triples

    def _find_triple_with_two(self) -> List[List[Card]]:
        """查找所有三带二"""
        triples = []
        counts = count_ranks(self.hand_cards)

        # 找出三张
        triple_values = [v for v, c in counts.items() if c >= 3]

        for triple_value in triple_values:
            triple_cards = [c for c in self.hand_cards if c.value == triple_value][:3]

            # 找任意对子作为带牌
            for value, count in counts.items():
                if count >= 2 and value != triple_value:
                    wing_cards = [c for c in self.hand_cards if c.value == value][:2]
                    combo = triple_cards + wing_cards
                    triples.append(combo)

        return triples

    def __str__(self):
        return f"Player({self.name}, 手牌:{self.card_count}张, 地主:{self.is_landlord})"

    def __repr__(self):
        return self.__str__()