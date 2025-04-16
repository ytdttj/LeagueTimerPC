# League Timer - 英雄联盟召唤师技能计时器

## 免责声明

*League Timer不隶属于Riot Games，也不反映Riot Games或任何官方参与英雄联盟制作或管理的人的观点或意见。*

## 开源声明

本项目完全开源且免费，采用MIT许可证。详情请参阅[LICENSE](./LICENSE)。如果在任意渠道购买到本APP皆为盗版。

## 项目简介

League Timer 是一款专为英雄联盟（League of Legends）玩家设计的召唤师技能冷却时间计时工具。在对局中，准确记录敌方召唤师技能的冷却时间对于团队决策和战术安排至关重要。本应用提供了简单直观的界面，帮助玩家精确追踪所有位置的敌方召唤师技能冷却时间。

## 使用方法

1. 为每个位置选择对应的召唤师技能。
2. 根据情况勾选是否使用星界洞悉天赋和CD鞋。
3. 点击"开始计时"按钮启动计时。
4. 倒计时结束后，会有声音和颜色提示。
5. 再次点击"开始计时"可开始新的计时。

## 安装与运行

对于大多数用户，推荐直接下载预编译好的可执行文件（`.exe`），无需安装 Python 环境即可运行。

1.  访问项目的 [Releases 页面](https://github.com/ytdttj/LeagueTimerPC/releases/latest) 。
2.  在最新版本的 "Assets" 部分，下载后缀名为 `.exe` 的文件。
3.  下载完成后，双击运行 `.exe` 文件即可。

## 自行构建

如果你想自行从源代码构建或运行，请按以下步骤操作：

1.  **确保已安装 Python:** 如果你还没有安装 Python，请从 [Python官网](https://www.python.org/) 下载并安装最新版本。
2.  **克隆或下载项目:**
    ```bash
    git clone https://github.com/ytdttj/LeagueTimerPC.git
    cd LeagueTimerPC
    ```
    或者直接下载项目的 ZIP 文件并解压。
3.  **安装依赖:**
    ```bash
    pip install -r requirements.txt
    ```
    requirements.txt 中包含了项目所需的依赖库，包括 `pyinstaller` 。
4.  **运行应用:**
    ```bash
    python league_timer.py
    ```
5.  **（可选）打包为可执行文件:** 如果你想创建独立的可执行文件（.exe），可以使用 PyInstaller：
    ```bash
    pyinstaller --onefile --windowed --version-file version.txt --add-data "notification_sound.mp3;." league_timer.py
    ```
    可执行文件将生成在 `dist` 目录下。

## 开发者信息

- 开发者：ytdttj
- 联系方式：[新浪微博](https://weibo.com/u/2265348910)

---

*League Timer不隶属于Riot Games，也不反映Riot Games或任何官方参与英雄联盟制作或管理的人的观点或意见。*