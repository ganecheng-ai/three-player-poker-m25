# -*- coding: utf-8 -*-
"""动画系统"""

import pygame
from typing import List, Callable, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import time


class AnimationType(Enum):
    """动画类型"""
    DEAL_CARDS = "deal_cards"          # 发牌
    PLAY_CARDS = "play_cards"          # 出牌
    RETURN_CARDS = "return_cards"      # 收牌
    CALL_LANDLORD = "call_landlord"    # 叫地主
    SHOW_LANDLORD_CARDS = "show_landlord_cards"  # 显示底牌
    WIN = "win"                        # 胜利
    LOSE = "lose"                      # 失败


@dataclass
class Animation:
    """动画对象"""
    animation_type: AnimationType
    start_time: float
    duration: float
    is_active: bool = True
    callback: Optional[Callable] = None
    data: Dict[str, Any] = field(default_factory=dict)


class AnimationManager:
    """动画管理器"""

    def __init__(self):
        self.animations: List[Animation] = []
        self.screen = None

    def set_screen(self, screen):
        """设置屏幕"""
        self.screen = screen

    def create_deal_animation(self, cards: List, from_pos: tuple, to_pos: tuple,
                              duration: float = 0.5, callback: Optional[Callable] = None):
        """创建发牌动画"""
        animation = Animation(
            animation_type=AnimationType.DEAL_CARDS,
            start_time=pygame.time.get_ticks() / 1000.0,
            duration=duration,
            callback=callback,
            data={
                'cards': cards,
                'from_pos': from_pos,
                'to_pos': to_pos,
                'progress': 0.0
            }
        )
        self.animations.append(animation)
        return animation

    def create_play_animation(self, cards: List, from_pos: tuple, to_pos: tuple,
                              duration: float = 0.3, callback: Optional[Callable] = None):
        """创建出牌动画"""
        animation = Animation(
            animation_type=AnimationType.PLAY_CARDS,
            start_time=pygame.time.get_ticks() / 1000.0,
            duration=duration,
            callback=callback,
            data={
                'cards': cards,
                'from_pos': from_pos,
                'to_pos': to_pos,
                'progress': 0.0
            }
        )
        self.animations.append(animation)
        return animation

    def create_call_landlord_animation(self, player_id: int, is_landlord: bool,
                                       duration: float = 1.0, callback: Optional[Callable] = None):
        """创建叫地主动画"""
        animation = Animation(
            animation_type=AnimationType.CALL_LANDLORD,
            start_time=pygame.time.get_ticks() / 1000.0,
            duration=duration,
            callback=callback,
            data={
                'player_id': player_id,
                'is_landlord': is_landlord,
                'progress': 0.0
            }
        )
        self.animations.append(animation)
        return animation

    def create_win_animation(self, winner_name: str, duration: float = 2.0,
                             callback: Optional[Callable] = None):
        """创建胜利动画"""
        animation = Animation(
            animation_type=AnimationType.WIN,
            start_time=pygame.time.get_ticks() / 1000.0,
            duration=duration,
            callback=callback,
            data={
                'winner_name': winner_name,
                'progress': 0.0,
                'particles': self._create_particles()
            }
        )
        self.animations.append(animation)
        return animation

    def create_lose_animation(self, duration: float = 2.0, callback: Optional[Callable] = None):
        """创建失败动画"""
        animation = Animation(
            animation_type=AnimationType.LOSE,
            start_time=pygame.time.get_ticks() / 1000.0,
            duration=duration,
            callback=callback,
            data={
                'progress': 0.0,
                'flicker': 0
            }
        )
        self.animations.append(animation)
        return animation

    def _create_particles(self):
        """创建庆祝粒子"""
        import random
        particles = []
        for _ in range(50):
            particles.append({
                'x': random.randint(0, 1280),
                'y': random.randint(0, 720),
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-5, -1),
                'color': (random.randint(200, 255), random.randint(150, 255), 0),
                'size': random.randint(3, 8)
            })
        return particles

    def update(self):
        """更新所有动画"""
        current_time = pygame.time.get_ticks() / 1000.0

        for animation in self.animations[:]:
            if not animation.is_active:
                continue

            # 计算进度
            elapsed = current_time - animation.start_time
            progress = min(elapsed / animation.duration, 1.0)
            animation.data['progress'] = progress

            if progress >= 1.0:
                animation.is_active = False
                if animation.callback:
                    animation.callback()

                # 移除完成的动画
                self.animations.remove(animation)

    def is_animating(self) -> bool:
        """是否有动画在播放"""
        return any(a.is_active for a in self.animations)

    def draw(self, screen):
        """绘制动画效果"""
        if not self.screen:
            self.screen = screen

        for animation in self.animations:
            if not animation.is_active:
                continue

            if animation.animation_type == AnimationType.WIN:
                self._draw_win_animation(screen, animation.data)
            elif animation.animation_type == AnimationType.LOSE:
                self._draw_lose_animation(screen, animation.data)

    def _draw_win_animation(self, screen, data):
        """绘制胜利动画"""
        import random
        from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD

        # 更新和绘制粒子
        particles = data.get('particles', [])
        for p in particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.1  # 重力

            if p['y'] > SCREEN_HEIGHT:
                p['y'] = 0
                p['x'] = random.randint(0, SCREEN_WIDTH)

            pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), p['size'])

    def _draw_lose_animation(self, screen, data):
        """绘制失败动画"""
        # 简单的闪烁效果
        data['flicker'] = (data['flicker'] + 1) % 30
        if data['flicker'] < 15:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(30)
            overlay.fill((100, 0, 0))
            screen.blit(overlay, (0, 0))

    def clear(self):
        """清除所有动画"""
        self.animations.clear()


# 全局动画管理器
animation_manager = AnimationManager()