# -*- coding: utf-8 -*-
"""欢乐斗地主 - 主程序入口"""

import sys
import pygame
from ui.resources import resources
from ui.game_screen import GameScreen
from utils.logger import logger


def main():
    """主函数"""
    # 初始化
    logger.info("游戏启动")
    resources.load_fonts()
    resources.init_screen()

    # 创建游戏屏幕
    game_screen = GameScreen()

    # 游戏主循环
    clock = pygame.time.Clock()
    running = True

    logger.info("进入游戏主循环")

    while running:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            else:
                game_screen.handle_event(event)

        # 绘制
        game_screen.draw()
        resources.flip()

        # 帧率控制
        clock.tick(60)

    logger.info("游戏退出")
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()