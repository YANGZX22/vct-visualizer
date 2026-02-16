# VCT Display Demo - Valorant 赛事日程生成器

一个用于生成 Valorant Champions Tour (VCT) 赛事日程图的桌面应用程序。支持手动编辑和从 VLR.gg 自动导入赛程，可导出为高清竖向长图。

<img src="assets/screenshot/scr.png" width="50%" alt="App Screenshot">

## 主要功能

### 1. 赛程管理
- **可视化卡片**：直观展示比赛时间、对阵双方、赛事类型。
- **增删改查**：轻松添加、编辑、删除和排序比赛卡片。
- **拖拽排序**：支持按时间自动排序。
- **快捷键支持**：
  - `Ctrl+C`：复制选中比赛信息
  - `Ctrl+V`：粘贴比赛信息
  - `Delete`：删除选中比赛
- **数据持久化**：自动保存赛程数据到本地 `matches.json`。

### 2. 自动化导入
- **VLR.gg 集成**：内置 API 接口，一键导入 VLR.gg 赛程数据。
- **智能解析**：
  - 自动识别赛事类型 (Masters, Champions, Pacific, EMEA, Americas, CN, etc.)
  - 自动转换时区和时间格式
  - 智能匹配队伍名称和图标 (例如 "EDward Gaming" -> "EDG")
  - 支持导入 Upcoming, Results, Live Score 等多种数据类型

### 3. 图片导出
- **自定义背景**：支持导入自定义背景图片，自动适配宽度。
- **高清导出**：一键生成 1080px 宽度的竖向长图，适合社交媒体分享。
- **智能排版**：自动计算高度，支持背景图片平铺或裁断。

### 4. 丰富的资源库
- **队伍图标**：内置四大赛区 (Pacific, EMEA, Americas, CN) 及次级联赛队伍图标。
- **赛事标识**：支持各种级别的赛事 Logo 显示。
- **自定义队伍**：支持在 "Others" 分区手动输入未收录的队伍名称。

## 使用说明

### 运行程序
1.  确保已安装 Python 3.10+。
2.  安装依赖库：
    ```bash
    pip install -r requirements.txt
    ```
3.  运行主程序：
    ```bash
    python main.py
    ```

### 编译为 EXE
双击运行根目录下的 `build.bat` 脚本，即可自动打包为单文件可执行程序 `dist/VCT_Display.exe`。

## 文件结构

- `main.py`: 程序入口
- `preview.py`: 主界面与预览逻辑
- `dialogs.py`: 编辑与设置对话框
- `cards.py`: 比赛卡片 UI 组件
- `api_import.py`: VLR.gg API 导入逻辑
- `widgets.py`: 自定义控件 (如队伍选择器)
- `utils.py`: 工具函数
- `config.py`: 全局配置与常量
- `assets/`: 字体、图标与图片资源

## 技术栈

- **GUI Framework**: PyQt6
- **Image Processing**: Pillow (PIL)
- **Data Source**: VLR.gg API (Unofficial)

## 贡献

欢迎提交 Issue 或 Pull Request 来完善队伍图标库或映射规则。

---
*Disclaimer: This project is not affiliated with Riot Games or VLR.gg.*
