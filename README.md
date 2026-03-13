# 欢乐斗地主 (Dou Dizhu)

三人斗地主扑克游戏，使用 Python + Pygame 开发。

## 游戏特性

- 🎮 经典三人斗地主玩法
- 🤖 AI 对战模式
- 🎨 精美界面设计
- 📝 完整日志系统
- 🪵 Windows / macOS / Linux 多平台支持

## 运行要求

- Python 3.8+
- Pygame 2.0+

## 安装依赖

```bash
pip install pygame
```

## 运行游戏

```bash
python main.py
```

## 打包发布

本项目使用 GitHub Actions 自动构建。创建 Git Tag 即可触发发布：

```bash
git tag v1.0.0
git push origin v1.0.0
```

构建产物包括：
- Windows: `.exe` / `.zip`
- macOS: `.tar.gz`
- Linux: `.tar.gz`
- 包含 SHA256 校验和文件 `checksums.txt`

## 项目结构

```
├── main.py              # 游戏入口
├── config.py            # 游戏配置
├── game/                # 游戏核心模块
│   ├── card.py          # 扑克牌类
│   ├── player.py        # 玩家类
│   ├── ai_player.py     # AI 玩家
│   ├── card_utils.py    # 牌型判断工具
│   └── game_controller.py # 游戏控制器
├── ui/                  # UI 模块
│   ├── resources.py     # 资源管理
│   ├── game_screen.py   # 游戏界面
│   └── widgets.py       # UI 组件
├── utils/               # 工具模块
│   └── logger.py        # 日志系统
└── assets/              # 资源文件
    ├── cards/           # 扑克牌图片
    └── sounds/          # 音效
```

## 操作说明

- 点击"开始游戏"开始新游戏
- 点击手牌选择要出的牌
- 点击"出牌"确认出牌
- 点击"过"放弃出牌

## 开发

```bash
# 克隆项目
git clone https://github.com/ganecheng-ai/three-player-poker-m25.git
cd three-player-poker-m25

# 安装依赖
pip install pygame

# 运行游戏
python main.py
```

## License

MIT