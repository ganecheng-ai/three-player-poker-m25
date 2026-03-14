# -*- coding: utf-8 -*-
"""游戏界面"""

import pygame
import time
from typing import Optional, List
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_GREEN_DARK, COLOR_GREEN_MAIN, COLOR_GOLD, COLOR_WHITE,
    CARD_WIDTH, CARD_HEIGHT, CARD_MARGIN,
    PLAYER_BOTTOM, PLAYER_LEFT, PLAYER_RIGHT,
    STATE_MENU, STATE_DEALING, STATE_CALLING_LANDLORD, STATE_PLAYING, STATE_GAME_OVER
)
from game.card import Card
from game.game_controller import GameController
from ui.resources import resources
from ui.widgets import Button, CardWidget, PlayerInfo, MessageBox
from ui.animation import animation_manager
from ui.sound_manager import sound_manager
from utils.logger import logger


class GameScreen:
    """游戏界面"""

    def __init__(self):
        self.game = GameController()
        self.selected_cards: List[Card] = []
        self.message: Optional[MessageBox] = None
        self.last_ai_play_time = 0
        self.ai_play_delay = 1000  # AI出牌延迟（毫秒）

        # 注册叫地主回调
        from game.game_controller import set_landlord_callback
        set_landlord_callback(self._on_landlord_called)

        # 按钮
        self.buttons = {
            'start': Button(SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 50, 160, 50,
                          "开始游戏", self.on_start_game),
            'play': Button(SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT - 100, 120, 45,
                         "出牌", self.on_play_cards),
            'pass': Button(SCREEN_WIDTH // 2 + 40, SCREEN_HEIGHT - 100, 120, 45,
                         "过", self.on_pass_cards),
            'restart': Button(SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 80, 160, 50,
                            "再来一局", self.on_start_game),
        }

    def update(self):
        """更新游戏状态，处理AI自动出牌"""
        # 更新动画
        animation_manager.update()

        if self.game.state == STATE_PLAYING:
            current_player = self.game.get_current_player()
            # 如果是AI玩家且当前回合不是玩家（人类玩家需要手动出牌）
            if current_player.is_ai and current_player.player_id != PLAYER_BOTTOM:
                current_time = pygame.time.get_ticks()
                # 检查是否需要AI出牌（添加延迟避免瞬间出牌）
                if current_time - self.last_ai_play_time > self.ai_play_delay:
                    self._ai_play_cards(current_player)
                    self.last_ai_play_time = current_time

    def _on_landlord_called(self, player_id: int, is_landlord: bool):
        """叫地主回调"""
        # 播放叫地主音效
        sound_manager.play('call_landlord')
        # 创建叫地主动画
        animation_manager.create_call_landlord_animation(player_id, is_landlord)

    def on_start_game(self):
        """开始游戏"""
        self.game.start_new_game()
        self.selected_cards = []
        self.message = MessageBox("游戏开始!")
        # 播放发牌音效
        sound_manager.play('deal')
        # 创建发牌动画
        animation_manager.create_deal_animation(
            cards=[],
            from_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            to_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            duration=0.3
        )

    def on_play_cards(self):
        """出牌"""
        if not self.selected_cards:
            self.message = MessageBox("请选择要出的牌!")
            return

        player = self.game.players[PLAYER_BOTTOM]
        if self.game.can_play_cards(PLAYER_BOTTOM, self.selected_cards):
            # 播放出牌音效
            if len(self.selected_cards) == 4:
                sound_manager.play('bomb')
            elif len(self.selected_cards) == 2 and self.selected_cards[0].rank == self.selected_cards[1].rank:
                sound_manager.play('rocket')
            else:
                sound_manager.play('play_card')

            self.game.player_play_cards(PLAYER_BOTTOM, self.selected_cards)
            self.selected_cards = []
        else:
            self.message = MessageBox("不能出这些牌!")

    def on_pass_cards(self):
        """过牌"""
        if self.game.last_cards is None or self.game.last_player_id != PLAYER_BOTTOM:
            self.message = MessageBox("你是首家，不能过!")
            return
        # 播放过牌音效
        sound_manager.play('pass')
        self.game.player_play_cards(PLAYER_BOTTOM, [])
        self.selected_cards = []

    def _ai_play_cards(self, ai_player):
        """AI自动出牌"""
        # 获取上家出的牌
        last_cards = self.game.last_cards
        last_player_id = self.game.last_player_id if self.game.last_player_id is not None else -1

        # 获取AI可出的牌
        cards_to_play = ai_player.choose_cards_to_play(last_player_id, last_cards, self.game.play_history)

        # 检查是否能出牌
        if cards_to_play and self.game.can_play_cards(ai_player.player_id, cards_to_play):
            self.game.player_play_cards(ai_player.player_id, cards_to_play)
            logger.info(f"AI {ai_player.name} 出牌: {[str(c) for c in cards_to_play]}")
            # 播放出牌音效
            if len(cards_to_play) == 4:
                sound_manager.play('bomb')
            else:
                sound_manager.play('play_card')
        else:
            # AI过牌
            self.game.player_play_cards(ai_player.player_id, [])
            logger.info(f"AI {ai_player.name} 过牌")
            sound_manager.play('pass')

    def draw(self):
        """绘制游戏界面"""
        screen = resources.get_screen()

        # 背景
        resources.fill_background(COLOR_GREEN_DARK)

        # 绘制动画效果
        animation_manager.draw(screen)

        if self.game.state == STATE_MENU:
            self._draw_menu(screen)
        else:
            self._draw_game(screen)
            self._draw_buttons(screen)

    def _draw_menu(self, screen):
        """绘制菜单"""
        # 标题
        title = resources.render_text("欢乐斗地主", 'large', COLOR_GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(title, title_rect)

        # 副标题
        subtitle = resources.render_text("Three Player Poker", 'medium', COLOR_WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        screen.blit(subtitle, subtitle_rect)

        # 按钮
        self.buttons['start'].draw(screen)

    def _draw_game(self, screen):
        """绘制游戏画面"""
        # 玩家信息
        self._draw_player_info(screen)

        # 底牌
        self._draw_landlord_cards(screen)

        # 出牌区域
        self._draw_played_cards(screen)

        # 玩家手牌
        self._draw_player_hand(screen)

        # 消息提示
        if self.message and self.message.is_visible:
            self.message.draw(screen)

    def _draw_player_info(self, screen):
        """绘制玩家信息"""
        players_info = [
            (PLAYER_LEFT, 50, SCREEN_HEIGHT // 2 - 50),   # 左侧
            (PLAYER_BOTTOM, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 200),  # 下方
            (PLAYER_RIGHT, SCREEN_WIDTH - 180, SCREEN_HEIGHT // 2 - 50),  # 右侧
        ]

        for player_id, x, y in players_info:
            player = self.game.players[player_id]
            is_current = (self.game.current_player_id == player_id and
                         self.game.state == STATE_PLAYING)
            info = PlayerInfo(x, y, player_id)
            info.draw(screen, player, is_current)

    def _draw_landlord_cards(self, screen):
        """绘制底牌"""
        if self.game.landlord_id is not None:
            # 显示底牌
            start_x = SCREEN_WIDTH // 2 - (CARD_WIDTH + 10) * 3 // 2
            for i, card in enumerate(self.game.landlord_cards):
                widget = CardWidget(start_x + i * (CARD_WIDTH + 10), 50, card)
                widget.draw(screen)

            # 底牌标签
            label = resources.render_text("底牌", 'small')
            screen.blit(label, (start_x, 30))

    def _draw_played_cards(self, screen):
        """绘制已出的牌"""
        if self.game.last_cards and len(self.game.last_cards) > 0:
            # 显示上家出的牌
            player = self.game.players[self.game.last_player_id]
            center_x = SCREEN_WIDTH // 2
            center_y = SCREEN_HEIGHT // 2

            start_x = center_x - (CARD_WIDTH + 5) * len(self.game.last_cards) // 2

            for i, card in enumerate(self.game.last_cards):
                # 不同位置显示不同偏移
                offset_y = 0
                if player.player_id == PLAYER_LEFT:
                    offset_y = -50
                elif player.player_id == PLAYER_RIGHT:
                    offset_y = 50

                widget = CardWidget(start_x + i * (CARD_WIDTH + 5), center_y + offset_y, card)
                widget.draw(screen)

    def _draw_player_hand(self, screen):
        """绘制玩家手牌"""
        player = self.game.players[PLAYER_BOTTOM]
        cards = player.hand_cards

        if not cards:
            return

        # 计算牌的位置
        total_width = len(cards) * (CARD_WIDTH // 2 + CARD_MARGIN)
        start_x = (SCREEN_WIDTH - total_width) // 2
        base_y = SCREEN_HEIGHT - CARD_HEIGHT - 20

        for i, card in enumerate(cards):
            x = start_x + i * (CARD_WIDTH // 2 + CARD_MARGIN)
            is_selected = card in self.selected_cards
            widget = CardWidget(x, base_y, card, selected=is_selected)
            widget.draw(screen)

    def _draw_buttons(self, screen):
        """绘制按钮"""
        if self.game.state == STATE_PLAYING and self.game.current_player_id == PLAYER_BOTTOM:
            self.buttons['play'].draw(screen)
            self.buttons['pass'].draw(screen)

        if self.game.state == STATE_GAME_OVER:
            self.buttons['restart'].draw(screen)

            # 显示获胜者
            winner = None
            for player in self.game.players:
                if player.card_count == 0:
                    winner = player
                    break

            if winner:
                result = "胜利!" if winner.is_landlord else "失败!"
                color = COLOR_GOLD if winner.is_landlord else (200, 50, 50)
                result_text = resources.render_text(
                    f"{winner.name} {result}", 'large', color)
                rect = result_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
                screen.blit(result_text, rect)

                # 首次进入游戏结束状态时播放音效和动画
                if not hasattr(self, '_game_over_played') or not self._game_over_played:
                    self._game_over_played = True
                    if winner.player_id == PLAYER_BOTTOM:
                        if winner.is_landlord:
                            sound_manager.play('win')
                            animation_manager.create_win_animation(winner.name)
                        else:
                            sound_manager.play('win')  # 农民赢也是胜利
                            animation_manager.create_win_animation(winner.name)
                    else:
                        sound_manager.play('lose')
                        animation_manager.create_lose_animation()
        else:
            # 重置游戏结束标志
            if hasattr(self, '_game_over_played'):
                self._game_over_played = False

    def handle_event(self, event) -> bool:
        """处理事件"""
        # 按钮事件
        for btn in self.buttons.values():
            if btn.handle_event(event):
                return True

        # 选牌事件
        if event.type == pygame.MOUSEBUTTONDOWN and self.game.state == STATE_PLAYING:
            if self.game.current_player_id == PLAYER_BOTTOM:
                self._handle_card_click(event.pos)

        return True

    def _handle_card_click(self, pos):
        """处理选牌点击"""
        player = self.game.players[PLAYER_BOTTOM]
        cards = player.hand_cards

        # 计算牌的位置
        total_width = len(cards) * (CARD_WIDTH // 2 + CARD_MARGIN)
        start_x = (SCREEN_WIDTH - total_width) // 2
        base_y = SCREEN_HEIGHT - CARD_HEIGHT - 20

        for i, card in enumerate(cards):
            x = start_x + i * (CARD_WIDTH // 2 + CARD_MARGIN)
            widget = CardWidget(x, base_y, card)

            if widget.handle_click(pos):
                if card in self.selected_cards:
                    self.selected_cards.remove(card)
                else:
                    self.selected_cards.append(card)
                break