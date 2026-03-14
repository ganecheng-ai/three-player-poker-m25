# -*- coding: utf-8 -*-
"""音效系统"""

import os
import pygame
from typing import Optional
from config import SOUNDS_DIR
from utils.logger import logger


class SoundManager:
    """音效管理器"""

    def __init__(self):
        self.enabled = True
        self.volume = 0.7
        self.music_volume = 0.5
        self.sounds = {}
        self.music_playing = False

        # 初始化音效
        self._init_sounds()

    def _init_sounds(self):
        """初始化音效系统"""
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            logger.info("音效系统初始化完成")
        except Exception as e:
            logger.warning(f"音效系统初始化失败: {e}")
            self.enabled = False
            return

        # 加载音效
        self._load_sounds()

    def _load_sounds(self):
        """加载音效文件"""
        sound_files = {
            'deal': 'deal.wav',
            'play_card': 'play_card.wav',
            'call_landlord': 'call_landlord.wav',
            'grab_landlord': 'grab_landlord.wav',
            'pass': 'pass.wav',
            'bomb': 'bomb.wav',
            'rocket': 'rocket.wav',
            'win': 'win.wav',
            'lose': 'lose.wav',
            'click': 'click.wav',
        }

        for name, filename in sound_files.items():
            filepath = os.path.join(SOUNDS_DIR, filename)
            if os.path.exists(filepath):
                try:
                    self.sounds[name] = pygame.mixer.Sound(filepath)
                    self.sounds[name].set_volume(self.volume)
                    logger.info(f"加载音效: {filename}")
                except Exception as e:
                    logger.warning(f"加载音效失败 {filename}: {e}")
            else:
                # 音效文件不存在，创建空音效
                logger.debug(f"音效文件不存在: {filename}")

    def play(self, sound_name: str) -> bool:
        """播放音效"""
        if not self.enabled:
            return False

        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].set_volume(self.volume)
                self.sounds[sound_name].play()
                return True
            except Exception as e:
                logger.warning(f"播放音效失败 {sound_name}: {e}")
        return False

    def play_music(self, music_name: str = 'background') -> bool:
        """播放背景音乐"""
        if not self.enabled:
            return False

        filepath = os.path.join(SOUNDS_DIR, f'{music_name}.mp3')
        if not os.path.exists(filepath):
            filepath = os.path.join(SOUNDS_DIR, f'{music_name}.ogg')

        if os.path.exists(filepath):
            try:
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)  # -1 表示循环播放
                self.music_playing = True
                logger.info(f"播放背景音乐: {music_name}")
                return True
            except Exception as e:
                logger.warning(f"播放背景音乐失败: {e}")
        else:
            logger.debug(f"背景音乐文件不存在: {music_name}")

        return False

    def stop_music(self):
        """停止背景音乐"""
        if self.enabled and self.music_playing:
            try:
                pygame.mixer.music.stop()
                self.music_playing = False
            except Exception as e:
                logger.warning(f"停止背景音乐失败: {e}")

    def pause_music(self):
        """暂停背景音乐"""
        if self.enabled and self.music_playing:
            try:
                pygame.mixer.music.pause()
            except Exception as e:
                logger.warning(f"暂停背景音乐失败: {e}")

    def resume_music(self):
        """恢复背景音乐"""
        if self.enabled:
            try:
                pygame.mixer.music.unpause()
            except Exception as e:
                logger.warning(f"恢复背景音乐失败: {e}")

    def set_volume(self, volume: float):
        """设置音量 (0.0 - 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(self.volume)

    def set_music_volume(self, volume: float):
        """设置背景音乐音量 (0.0 - 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.enabled:
            pygame.mixer.music.set_volume(self.music_volume)

    def toggle(self):
        """切换音效开关"""
        self.enabled = not self.enabled
        if not self.enabled:
            self.stop_music()
        return self.enabled


# 全局音效管理器
sound_manager = SoundManager()