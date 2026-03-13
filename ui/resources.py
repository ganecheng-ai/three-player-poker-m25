# -*- coding: utf-8 -*-
"""UI资源管理"""

import os
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, COLOR_WHITE
from utils.logger import logger

# 初始化pygame
pygame.init()


class ResourceManager:
    """资源管理器"""

    def __init__(self):
        self.screen = None
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self.cards_cache = {}

    def init_screen(self):
        """初始化屏幕"""
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(SCREEN_TITLE)
        logger.info("屏幕初始化完成")

    def load_fonts(self):
        """加载字体"""
        # 尝试加载中文字体
        font_paths = [
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/System/Library/Fonts/PingFang.ttc',  # macOS
            'C:/Windows/Fonts/simhei.ttf',  # Windows
        ]

        font_loaded = False
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    self.font_large = pygame.font.Font(font_path, 48)
                    self.font_medium = pygame.font.Font(font_path, 28)
                    self.font_small = pygame.font.Font(font_path, 18)
                    font_loaded = True
                    logger.info(f"加载字体: {font_path}")
                    break
                except Exception as e:
                    logger.warning(f"字体加载失败: {font_path}, {e}")

        if not font_loaded:
            # 使用默认字体
            self.font_large = pygame.font.SysFont('simhei', 48)
            self.font_medium = pygame.font.SysFont('simhei', 28)
            self.font_small = pygame.font.SysFont('simhei', 18)
            logger.info("使用默认字体")

    def render_text(self, text: str, font_size: str = 'medium', color=COLOR_WHITE):
        """渲染文本"""
        font = {
            'large': self.font_large,
            'medium': self.font_medium,
            'small': self.font_small
        }.get(font_size, self.font_medium)

        return font.render(text, True, color)

    def get_screen(self):
        """获取屏幕"""
        if self.screen is None:
            self.init_screen()
        return self.screen

    def flip(self):
        """刷新屏幕"""
        if self.screen:
            pygame.display.flip()

    def fill_background(self, color):
        """填充背景"""
        if self.screen:
            self.screen.fill(color)


# 全局资源管理器
resources = ResourceManager()