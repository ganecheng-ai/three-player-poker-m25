# -*- coding: utf-8 -*-
"""UI组件"""

import pygame
from typing import Callable, Optional, List
from config import (
    COLOR_WHITE, COLOR_BLACK, COLOR_BUTTON, COLOR_BUTTON_HOVER,
    SCREEN_WIDTH, SCREEN_HEIGHT, CARD_WIDTH, CARD_HEIGHT
)
from game.card import Card, Suit
from ui.resources import resources


class Button:
    """按钮组件"""

    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 callback: Optional[Callable] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.is_hovered = False

    def draw(self, screen):
        """绘制按钮"""
        color = COLOR_BUTTON_HOVER if self.is_hovered else COLOR_BUTTON
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, COLOR_WHITE, self.rect, 2, border_radius=10)

        text_surface = resources.render_text(self.text, 'medium', COLOR_WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event) -> bool:
        """处理事件"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
        return False


class CardWidget:
    """扑克牌组件"""

    def __init__(self, x: int, y: int, card: Optional[Card] = None,
                 selected: bool = False, backside: bool = False):
        self.x = x
        self.y = y
        self.card = card
        self.selected = selected
        self.backside = backside

    @property
    def rect(self) -> pygame.Rect:
        offset_y = -20 if self.selected else 0
        return pygame.Rect(self.x, self.y + offset_y, CARD_WIDTH, CARD_HEIGHT)

    def draw(self, screen):
        """绘制扑克牌"""
        offset_y = -20 if self.selected else 0
        card_y = self.y + offset_y

        if self.backside:
            # 背面
            pygame.draw.rect(screen, (200, 50, 50),
                           (self.x, card_y, CARD_WIDTH, CARD_HEIGHT), border_radius=8)
            pygame.draw.rect(screen, (150, 30, 30),
                           (self.x, card_y, CARD_WIDTH, CARD_HEIGHT), 3, border_radius=8)
            # 花纹
            for i in range(3):
                for j in range(3):
                    if (i + j) % 2 == 0:
                        pygame.draw.circle(screen, (180, 80, 80),
                                         (self.x + 20 + i * 25, card_y + 20 + j * 30), 5)
        elif self.card:
            # 正面
            pygame.draw.rect(screen, COLOR_WHITE,
                           (self.x, card_y, CARD_WIDTH, CARD_HEIGHT), border_radius=8)
            pygame.draw.rect(screen, (200, 200, 200),
                           (self.x, card_y, CARD_WIDTH, CARD_HEIGHT), 2, border_radius=8)

            # 绘制牌面
            rank_text = self.card.rank if self.card.rank not in ('joker', 'JOKER') else ('小' if self.card.rank == 'joker' else '大')

            # 角标
            small_font = resources.font_small
            rank_suit = small_font.render(f"{rank_text}", True, self.card.color)
            suit_name = {0: '♠', 1: '♥', 2: '♣', 3: '♦', 4: 'JOKER'}
            suit_text = suit_name.get(self.card.suit.value, '')

            # 左上角
            screen.blit(rank_suit, (self.x + 5, card_y + 5))
            suit_surf = small_font.render(suit_text, True, self.card.color)
            screen.blit(suit_surf, (self.x + 5, card_y + 22))

            # 右下角(旋转)
            rank_surf_r = pygame.transform.rotate(rank_suit, 180)
            screen.blit(rank_surf_r, (self.x + CARD_WIDTH - 25, card_y + CARD_HEIGHT - 25))

            # 中心花色
            if self.card.suit != Suit.JOKER:
                center_suit = resources.font_large.render(suit_text, True, self.card.color)
                center_rect = center_suit.get_rect(center=(self.x + CARD_WIDTH//2, card_y + CARD_HEIGHT//2))
                screen.blit(center_suit, center_rect)

    def handle_click(self, pos) -> bool:
        """检查点击"""
        return self.rect.collidepoint(pos)


class PlayerInfo:
    """玩家信息显示"""

    def __init__(self, x: int, y: int, player_id: int):
        self.x = x
        self.y = y
        self.player_id = player_id

    def draw(self, screen, player, is_current: bool = False):
        """绘制玩家信息"""
        # 玩家名
        name = player.name
        if player.is_landlord:
            name += " (地主)"

        name_surf = resources.render_text(name, 'medium')
        screen.blit(name_surf, (self.x, self.y))

        # 牌数
        count_surf = resources.render_text(f"{player.card_count}张", 'small')
        screen.blit(count_surf, (self.x, self.y + 30))

        # 当前回合指示
        if is_current:
            indicator = resources.render_text("◀", 'medium', (255, 215, 0))
            screen.blit(indicator, (self.x - 30, self.y + 5))


class MessageBox:
    """消息提示"""

    def __init__(self, message: str, duration: int = 2000):
        self.message = message
        self.duration = duration
        self.start_time = pygame.time.get_ticks()

    @property
    def is_visible(self) -> bool:
        return pygame.time.get_ticks() - self.start_time < self.duration

    def draw(self, screen):
        """绘制消息"""
        if not self.is_visible:
            return

        # 半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, 60))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, SCREEN_HEIGHT // 2 - 30))

        text = resources.render_text(self.message, 'medium')
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text, text_rect)