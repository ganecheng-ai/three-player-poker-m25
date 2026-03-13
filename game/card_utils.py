# -*- coding: utf-8 -*-
"""牌型判断工具"""

from typing import List, Tuple, Optional
from game.card import Card, Suit
from config import (
    CARD_TYPE_SINGLE, CARD_TYPE_PAIR, CARD_TYPE_TRIPLE,
    CARD_TYPE_STRAIGHT, CARD_TYPE_DOUBLE_STRAIGHT,
    CARD_TYPE_TRIPLE_STRAIGHT, CARD_TYPE_BOMB, CARD_TYPE_ROCKET
)
from utils.logger import logger


def get_card_values(cards: List[Card]) -> List[int]:
    """获取牌的数值列表"""
    return sorted([c.value for c in cards], reverse=True)


def count_ranks(cards: List[Card]) -> dict:
    """统计每种牌面出现的次数"""
    counts = {}
    for card in cards:
        counts[card.value] = counts.get(card.value, 0) + 1
    return counts


def is_single(cards: List[Card]) -> bool:
    """单张"""
    return len(cards) == 1


def is_pair(cards: List[Card]) -> bool:
    """对子"""
    if len(cards) != 2:
        return False
    return cards[0].value == cards[1].value


def is_triple(cards: List[Card]) -> bool:
    """三张(不带翅膀)"""
    if len(cards) != 3:
        return False
    return cards[0].value == cards[1].value == cards[2].value


def is_triple_with_wing(cards: List[Card]) -> Tuple[bool, int]:
    """三带(带不带单/对)"""
    if len(cards) not in (4, 5):
        return False, 0

    counts = count_ranks(cards)
    values = list(counts.values())

    # 找三张
    if 3 in values:
        triple_value = [v for v, c in counts.items() if c == 3][0]
        remaining = [v for v, c in counts.items() if c != 3]

        if len(remaining) == 0:
            return False, 0  # 纯三张不带

        # 带一张或带一对
        if len(remaining) == 1:
            wing_count = counts[remaining[0]]
            return True, wing_count

    return False, 0


def is_straight(cards: List[Card]) -> bool:
    """顺子(单顺)"""
    if len(cards) < 5 or len(cards) > 12:
        return False

    values = get_card_values(cards)
    # 不能有2、大小王
    if any(v >= 16 for v in values):
        return False

    # 去掉重复
    values = sorted(set(values), reverse=True)
    if len(values) != len(cards):
        return False

    # 必须是连续的
    for i in range(len(values) - 1):
        if values[i] - values[i + 1] != 1:
            return False

    return True


def is_double_straight(cards: List[Card]) -> bool:
    """连对(双顺)"""
    if len(cards) < 6 or len(cards) % 2 != 0:
        return False

    counts = count_ranks(cards)
    values = list(counts.values())

    # 必须都是对子
    if any(v != 2 for v in values):
        return False

    rank_values = sorted(counts.keys(), reverse=True)

    # 不能有2、大小王
    if any(v >= 16 for v in rank_values):
        return False

    # 必须连续
    for i in range(len(rank_values) - 1):
        if rank_values[i] - rank_values[i + 1] != 1:
            return False

    return True


def is_triple_straight(cards: List[Card]) -> Tuple[bool, int]:
    """飞机(三顺) - 返回(是否飞机, 飞机带牌数量)"""
    counts = count_ranks(cards)
    triples = [v for v, c in counts.items() if c >= 3]

    if len(triples) < 2:
        return False, 0

    # 排序检查连续性
    triples = sorted(triples, reverse=True)
    for i in range(len(triples) - 1):
        if triples[i] - triples[i + 1] != 1:
            return False, 0

    # 不能有2、大小王
    if any(v >= 16 for v in triples):
        return False, 0

    # 计算翅膀数量
    total_cards = len(cards)
    wing_count = total_cards - len(triples) * 3
    return True, wing_count


def is_bomb(cards: List[Card]) -> bool:
    """炸弹"""
    if len(cards) != 4:
        return False
    counts = count_ranks(cards)
    return 4 in counts.values()


def is_rocket(cards: List[Card]) -> bool:
    """王炸"""
    if len(cards) != 2:
        return False
    ranks = [c.rank for c in cards]
    return 'joker' in ranks and 'JOKER' in ranks


def get_card_type(cards: List[Card]) -> Tuple[Optional[int], Optional[int]]:
    """获取牌型, 返回(牌型, 牌型值)

    牌型值用于比较大小:
    - 单张、对子、三张、顺子、连对、飞机: 比较最大单牌
    - 炸弹: 比较牌面值
    - 王炸: 最大的牌型
    """
    if len(cards) == 0:
        return None, None

    # 先检查王炸
    if is_rocket(cards):
        return CARD_TYPE_ROCKET, 100

    # 检查炸弹
    if is_bomb(cards):
        counts = count_ranks(cards)
        bomb_value = [v for v, c in counts.items() if c == 4][0]
        return CARD_TYPE_BOMB, bomb_value

    # 检查三带
    has_triple_with_wing, wing = is_triple_with_wing(cards)
    if has_triple_with_wing:
        counts = count_ranks(cards)
        triple_value = [v for v, c in counts.items() if c == 3][0]
        return CARD_TYPE_TRIPLE, triple_value

    # 检查飞机
    is_plane, wing_count = is_triple_straight(cards)
    if is_plane:
        counts = count_ranks(cards)
        triple_values = sorted([v for v, c in counts.items() if c >= 3], reverse=True)
        return CARD_TYPE_TRIPLE_STRAIGHT, max(triple_values)

    # 检查连对
    if is_double_straight(cards):
        counts = count_ranks(cards)
        max_value = max(counts.keys())
        return CARD_TYPE_DOUBLE_STRAIGHT, max_value

    # 检查顺子
    if is_straight(cards):
        max_value = max(c.value for c in cards)
        return CARD_TYPE_STRAIGHT, max_value

    # 检查三张
    if is_triple(cards):
        return CARD_TYPE_TRIPLE, cards[0].value

    # 检查对子
    if is_pair(cards):
        return CARD_TYPE_PAIR, cards[0].value

    # 检查单张
    if is_single(cards):
        return CARD_TYPE_SINGLE, cards[0].value

    return None, None


def can_beat(cards: List[Card], last_cards: List[Card]) -> bool:
    """检查cards是否能管上last_cards"""
    if not last_cards:
        return True  # 首家出牌

    if not cards:
        return False

    current_type, current_value = get_card_type(cards)
    last_type, last_value = get_card_type(last_cards)

    if current_type is None:
        return False

    # 王炸最大
    if current_type == CARD_TYPE_ROCKET:
        return True

    # 炸弹可以管任何非炸弹的牌
    if current_type == CARD_TYPE_BOMB:
        if last_type != CARD_TYPE_BOMB and last_type != CARD_TYPE_ROCKET:
            return True
        return current_value > last_value

    # 必须同类型才能管
    if current_type != last_type:
        return False

    return current_value > last_value


def sort_cards(cards: List[Card], reverse: bool = True) -> List[Card]:
    """排序手牌"""
    return sorted(cards, key=lambda c: c.value, reverse=reverse)


def organize_cards(cards: List[Card]) -> dict:
    """整理手牌，按牌型分组"""
    counts = count_ranks(cards)
    organized = {1: [], 2: [], 3: [], 4: []}  # 按数量分组

    for card in cards:
        count = counts[card.value]
        organized[count].append(card)

    # 每组内按大小排序
    for count in organized:
        organized[count] = sort_cards(organized[count])

    return organized


if __name__ == '__main__':
    from game.card import Deck

    deck = Deck()
    deck.shuffle()

    # 测试牌型识别
    test_cases = [
        deck.deal(1),   # 单张
        deck.deal(2),   # 对子
        deck.deal(4),   # 炸弹
    ]

    for cards in test_cases:
        card_type, value = get_card_type(cards)
        print(f"{cards} -> type:{card_type}, value:{value}")