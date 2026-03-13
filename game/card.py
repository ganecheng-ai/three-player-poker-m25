# -*- coding: utf-8 -*-
"""扑克牌类"""

import random
from enum import Enum
from config import COLOR_RED, COLOR_BLACK_CARD
from utils.logger import logger


class Suit(Enum):
    """花色"""
    SPADE = 0      # 黑桃
    HEART = 1      # 红桃
    CLUB = 2       # 梅花
    DIAMOND = 3    # 方片
    JOKER = 4      # 王


class Card:
    """扑克牌"""

    # 牌面大小顺序(从小到大)
    RANK_ORDER = {
        '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
        'J': 11, 'Q': 12, 'K': 13, 'A': 14, '2': 15,
        'joker': 16, 'JOKER': 17
    }

    RANK_NAMES = {
        '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8',
        '9': '9', '10': '10', 'J': 'J', 'Q': 'Q', 'K': 'K', 'A': 'A',
        '2': '2', 'joker': '小王', 'JOKER': '大王'
    }

    def __init__(self, rank: str, suit: Suit):
        self.rank = rank  # 牌面: 3-2, J, Q, K, A, joker, JOKER
        self.suit = suit

    @property
    def value(self) -> int:
        """获取牌面大小值"""
        return self.RANK_ORDER.get(self.rank, 0)

    @property
    def color(self):
        """获取牌的颜色"""
        if self.suit in (Suit.HEART, Suit.DIAMOND):
            return COLOR_RED
        elif self.suit == Suit.JOKER:
            return COLOR_RED if self.rank == 'JOKER' else COLOR_BLACK_CARD
        return COLOR_BLACK_CARD

    @property
    def name(self) -> str:
        """获取牌名"""
        if self.suit == Suit.JOKER:
            return self.RANK_NAMES.get(self.rank, '')
        suit_name = {Suit.SPADE: '♠', Suit.HEART: '♥', Suit.CLUB: '♣', Suit.DIAMOND: '♦'}
        return f"{suit_name.get(self.suit, '')}{self.RANK_NAMES.get(self.rank, '')}"

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Card('{self.rank}', {self.suit})"

    def __lt__(self, other):
        if not isinstance(other, Card):
            return False
        return self.value < other.value

    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        return hash((self.rank, self.suit))


class Deck:
    """牌堆"""

    def __init__(self):
        self.cards = self._create_deck()
        self._is_shuffled = False

    def _create_deck(self):
        """创建一副牌"""
        cards = []
        ranks = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2']
        suits = [Suit.SPADE, Suit.HEART, Suit.CLUB, Suit.DIAMOND]

        # 52张普通牌
        for suit in suits:
            for rank in ranks:
                cards.append(Card(rank, suit))

        # 大小王
        cards.append(Card('joker', Suit.JOKER))
        cards.append(Card('JOKER', Suit.JOKER))

        return cards

    def shuffle(self):
        """洗牌"""
        random.shuffle(self.cards)
        self._is_shuffled = True
        logger.info("牌堆已洗牌")

    def deal(self, num: int = 1):
        """发牌"""
        if len(self.cards) < num:
            logger.warning(f"牌堆剩余牌数不足: 需要{num}, 剩余{len(self.cards)}")
            return []
        dealt = self.cards[:num]
        self.cards = self.cards[num:]
        return dealt

    def reset(self):
        """重置牌堆"""
        self.cards = self._create_deck()
        self._is_shuffled = False
        logger.info("牌堆已重置")

    def __len__(self):
        return len(self.cards)

    def __str__(self):
        return ' '.join(str(c) for c in self.cards)


def create_and_shuffle_deck():
    """创建并洗牌"""
    deck = Deck()
    deck.shuffle()
    return deck


if __name__ == '__main__':
    # 测试
    deck = create_and_shuffle_deck()
    print(f"牌堆大小: {len(deck)}")
    print(f"前5张牌: {deck.deal(5)}")