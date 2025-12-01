# Everything by mdfind
[English](README.md) | [中文](README_CN.md) | [한국어](README_KO.md) | [日本語](README_JP.md) | [Français](README_FR.md) | [Deutsch](README_DE.md) | [Español](README_ES.md)

<img width="3836" height="2026" alt="image" src="https://github.com/user-attachments/assets/d86c3d6b-6fd4-4cfe-b64f-67c465bb3d3c" /><img width="3832" height="2024" alt="image" src="https://github.com/user-attachments/assets/a91d2b13-07ac-4cae-ab33-506f1fa3bca6" />

一款基于 macOS 原生 Spotlight 引擎的极速文件搜索工具，毫秒级响应速度

## 核心功能

* **闪电搜索：** 基于 macOS Spotlight 索引技术，文件检索快如闪电
* **双模检索：** 同时支持文件名和文件内容搜索，精准定位目标
* **智能过滤：** 多维度筛选条件组合：
    * 文件大小范围（最小/最大字节数）
    * 指定文件类型（如 `pdf`, `docx`）
    * 是否区分大小写
    * 精确匹配或模糊搜索
* **精准定位：** 支持限定特定目录范围，缩小搜索区域
* **全能预览：** 内置文件预览功能支持：
    * 文本文件（自动识别编码）
    * 图片（JPEG/PNG/GIF动画/BMP/WEBP/HEIC）
    * SVG矢量图（自适应缩放+居中显示）
    * 音视频文件（支持播放控制）
* **媒体中心：**
    * 集成音视频播放器（标准控制条）
    * 独立播放窗口
    * 连续播放模式
    * 音量调节与静音功能
* **快捷入口：** 一键直达常用搜索：
    * 大文件（>50MB）
    * 视频文件
    * 音频文件
    * 图片文件
    * 压缩包
    * 应用程序
* **磁盘空间分析：** 分析任意目录的磁盘空间占用：
    * 一键分析主目录空间使用情况
    * 交互式柱状图可视化显示占用空间最大的文件夹
    * 右键点击搜索结果中的任何文件夹即可分析其空间占用
    * 双击图表柱状条深入子目录进行详细分析
    * 以彩色图表直观展示子目录大小分布
    * 自动按大小排序，快速定位最大的文件夹
* **灵活排序：** 支持名称/大小/修改时间/路径多维排序
* **批量处理：** 多选文件一键操作：
    * 使用 Shift 或 Command (⌘) 键多选
    * 批量操作：打开/删除/复制/移动/重命名
    * 丰富的右键菜单功能
* **多标签页搜索：** 同时进行多个搜索任务：
    * 为不同搜索查询创建独立标签页
    * 右键菜单管理标签：关闭、关闭其他、关闭左侧/右侧
    * 每个标签页独立的搜索结果和设置
    * 类似Chrome的标签页体验，支持拖拽排序和滚动按钮
* **个性定制：**
    * 6款精美主题任您选择：
        * 浅色/深色（系统默认）
        * Tokyo Night/Tokyo Night Storm（东京夜色）
        * Chinolor Dark/Chinolor Light（中国传统色）
    * 系统标题栏主题化，与所选主题完美融合
    * 预览面板显示控制
    * 可配置搜索历史记录
    * 自动保存窗口尺寸和排序设置
* **多格式导出：** 支持多种格式导出搜索结果：
    * JSON - 结构化数据格式
    * Excel (.xlsx) - 带格式的电子表格
    * HTML - 网页就绪表格格式
    * Markdown - 文档友好格式
    * CSV - 经典逗号分隔值格式
* **百万级承载：** 分批加载机制轻松处理海量结果
* **拖拽直达：** 直接拖放文件至其他应用
* **路径操作：** 一键复制完整路径/所在目录/纯文件名

## 安装指南

1. **运行环境：**
    * Python 3.6 或更新版本
    * PyQt6 图形界面库

2. **获取代码：**
    ```bash
    git clone https://github.com/appledragon/everythingByMdfind
    cd everythingByMdfind
    ```

3. **安装依赖：**
    ```bash
    pip install -r requirements.txt
    ```

4. **启动软件：**
    ```bash
    python everything.py
    ```

## 下载安装版

您可以直接从 [GitHub Releases](https://github.com/appledragon/everythingByMdfind/releases) 页面下载已打包好的 macOS 应用程序（.dmg 安装包）。

## 贡献代码

欢迎提交 Pull Request 或 Issue 共同完善项目！

## 开源许可

本项目采用 Apache License 2.0 许可证 - 详见 [LICENSE.md](LICENSE.md)

## 开发团队

Apple Dragon

## 当前版本

1.4.0

## 致谢

* 感谢 PyQt6 团队提供的跨平台 GUI 框架
* 致敬优秀开源项目带来的启发

