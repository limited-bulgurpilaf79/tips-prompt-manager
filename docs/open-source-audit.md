# 开源方案审计

## 当前项目审计结论

- 技术栈：Python 3 / Tkinter / SQLite。
- 架构：单机离线桌面工具，不需要浏览器、服务端或联网同步。
- 运行依赖：标准库即可。
- 打包目标：Windows 单文件 EXE 和便携 ZIP。
- 隐私边界：`prompts.db`、`config.json`、`.auth_session.json`、`settings.json` 均为用户本机数据，不进入 Git 或 Release。

## 候选方案对比

| 方案名称 | 来源 | 许可证 | 核心能力 | 优点 | 缺点 | 维护状态 | 与当前项目的契合度 | 可能冲突点 | 是否采用 | 采用方式 |
|---|---|---|---|---|---|---|---|---|---|---|
| Python 标准库 Tkinter + sqlite3 | Python 官方标准库 | Python Software Foundation License | GUI、SQLite、本地文件与密码哈希 | 零运行依赖、离线、体积小、与现有代码完全兼容 | UI 组件基础，需自行组织界面 | 随 Python 维护 | 高 | 无 | 采用 | 直接作为运行时实现 |
| PyInstaller | PyPI / pyinstaller.org | GPL-2.0-or-later with bootloader exception | Python 桌面程序打包为 Windows EXE | 本机已安装、适合 Tkinter、可生成单文件 EXE、元数据可控 | 产物未签名时可能被误报 | 活跃 | 高 | GPL 工具不能复制源码进项目；只作为构建工具 | 采用 | 仅作为开发/构建依赖 |
| Nuitka | PyPI / nuitka.net | Apache-2.0 | Python 编译打包 | 可生成优化后的二进制 | 构建链更重，对本项目收益不明显 | 活跃 | 中 | 增加编译器复杂度和构建时间 | 不采用 | 保留为未来性能需求备选 |
| BeeWare Briefcase | PyPI / beeware.org | BSD-3-Clause | 桌面应用打包和安装器工程 | 跨平台应用工程化 | 对 Tkinter 不是当前主路径，项目复杂度超过收益 | 活跃 | 低 | 会改变目录结构和运行方式 | 不采用 | 不引入 |

## 最终采用范围

- 直接复用：Python 标准库的 Tkinter、sqlite3、hashlib、hmac、json；PyInstaller 的 Windows EXE 打包能力。
- 只借鉴设计：不需要额外框架；只保留“数据层/认证层/UI 层分离”的常规桌面应用结构。
- 不采用：联网同步、云端提示词库、Electron、Tauri、Nuitka、Briefcase。
- 需要适配：原 `PromptManager.pyw` 改为启动器；业务代码迁入 `src/tips_prompt_manager/`；打包入口改为 `scripts/entry_prompt_manager.py`。
- 保留：原有离线、本地密码、SQLite 分类/提示词管理、搜索高亮和剪贴板复制行为。
- 替换：单文件混合 UI/SQL/认证逻辑、单语界面、缺失作者元数据和不可复现打包流程。
