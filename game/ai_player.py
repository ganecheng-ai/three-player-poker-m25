# -*- coding: utf-8 -*-
"""AI玩家"""

import random
from typing import List, Optional
from game.player import Player
from game.card import Card
from game.card_utils import get_card_type, can_beat, sort_cards, count_ranks
from utils.logger import logger


class AIPlayer(Player):
    """AI玩家"""

    def __init__(self, player_id: int, name: str = "电脑"):
        super().__init__(player_id, name, is_ai=True)
        self.difficulty = 1  # 难度等级

    def decide_landlord(self, landlord_cards: List[Card]) -> bool:
        """决定是否叫地主"""
        # 简单策略：有炸弹或王炸就叫
        counts = count_ranks(self.hand_cards)

        # 统计
        bomb_count = sum(1 for c in counts.values() if c >= 4)
        has_rocket = any(c.rank in ('joker', 'JOKER') for c in self.hand_cards)

        # 有王炸或2个以上炸弹就抢
        if has_rocket:
            return True
        if bomb_count >= 2:
            return True

        # 有大王或小王且牌较好
        has_joker = any(c.rank in ('joker', 'JOKER') for c in self.hand_cards)
        high_cards = sum(1 for c in self.hand_cards if c.value >= 14)  # A以上

        if has_joker and high_cards >= 3:
            return True
        if bomb_count >= 1 and high_cards >= 2:
            return True

        # 随机叫(30%概率)
        return random.random() < 0.3

    def choose_cards_to_play(self, last_player_id: int, last_cards: Optional[List[Card]],
                            history: List[tuple]) -> List[Card]:
        """选择要出的牌"""
        # 如果是首家
        if last_cards is None or len(last_cards) == 0:
            return self._play_first()

        # 获取能管的牌
        playable = self.get_playable_cards(last_cards)
        if not playable:
            return []  # 过

        # 选择最佳的牌
        return self._choose_best_cards(playable, last_player_id)

    def _play_first(self) -> List[Card]:
        """首家出牌策略"""
        # 出单张
        return [self.hand_cards[0]]

    def _choose_best_cards(self, playable: List[List[Card]], last_player_id: int) -> List[Card]:
        """选择最佳出牌"""
        # 优先出小牌
        # 按总牌面值排序，选择最小的
        scored = []
        for cards in playable:
            total = sum(c.value for c in cards)
            scored.append((cards, total))

        scored.sort(key=lambda x: x[1])
        return scored[0][0]

    def pass_cards(self) -> bool:
        """是否要不起"""
        return True