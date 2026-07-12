# TIPS Prompt Manager

## 中文

TIPS Prompt Manager 是一个离线提示词工程管理器，用于在本机保存、分类、搜索、编辑和复制提示词。它使用 Python/Tkinter 构建界面，使用 SQLite 保存数据，不需要浏览器、账号、服务端或网络连接。

### 功能特点

- 新建、编辑、删除提示词。
- 自定义分类，支持新增、重命名和删除分类。
- 按分类筛选提示词。
- 搜索标题和内容，并在列表和正文中高亮匹配结果。
- 一键复制提示词内容到剪贴板。
- 首次运行设置本地密码；同一次开机通过后不重复验证。
- 中英文界面切换，语言设置保存在本机。

### 安装方法

下载 Release 中的 `tips-prompt-manager-v1.0.0-windows-x64.exe` 后直接运行，或下载 `tips-prompt-manager-v1.0.0-windows-x64.zip` 解压后运行其中的 EXE。

EXE 未进行数字签名。请使用 Release 中的 `SHA256SUMS.txt` 校验文件完整性。

### 使用方法

1. 首次启动时设置本地密码。
2. 使用“新增分类”整理提示词类型。
3. 点击“新建”，填写标题、分类和提示词内容。
4. 点击“保存”写入本地 SQLite 数据库。
5. 使用搜索框查找标题或正文内容。
6. 点击“复制内容”将当前提示词复制到剪贴板。

本地数据文件会在程序同目录自动创建：

- `config.json`：密码盐值和密码哈希，不保存明文密码。
- `.auth_session.json`：本次开机验证状态。
- `settings.json`：语言偏好。
- `prompts.db`：SQLite 提示词数据库。

这些文件是个人数据，已被 `.gitignore` 排除，不应提交到仓库。

### 打包说明

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build.ps1
```

构建脚本会先运行测试和 `compileall`，再使用 PyInstaller 生成 Windows 单文件 EXE、便携 ZIP 和 SHA256 校验文件。

### 作者信息

- Author: HaoXiang Huang
- Email: didadida1688@gmail.com
- Homepage: https://nextweb4.github.io/
- GitHub: https://github.com/NextWeb4

### License

MIT License

## English

TIPS Prompt Manager is an offline prompt engineering manager for storing, categorizing, searching, editing, and copying prompts locally. It uses Python/Tkinter for the interface and SQLite for local storage. No browser, account, server, or network connection is required.

### Features

- Create, edit, and delete prompts.
- Add, rename, and delete custom categories.
- Filter prompts by category.
- Search titles and content with highlighted matches.
- Copy the current prompt content to the clipboard.
- Set a local password on first launch; the app skips repeat verification during the same boot session.
- Switch between Chinese and English; the language preference is stored locally.

### Installation

Download `tips-prompt-manager-v1.0.0-windows-x64.exe` from the Release page and run it directly, or download `tips-prompt-manager-v1.0.0-windows-x64.zip`, extract it, and run the EXE inside.

The EXE is not digitally signed. Verify file integrity with `SHA256SUMS.txt` from the Release page.

### Usage

1. Set a local password on first launch.
2. Use "Add category" to organize prompt types.
3. Click "New", then enter a title, category, and prompt content.
4. Click "Save" to write the prompt to the local SQLite database.
5. Use the search box to find title or content matches.
6. Click "Copy" to copy the current prompt to the clipboard.

Local data files are created next to the program:

- `config.json`: password salt and password hash, never plaintext password.
- `.auth_session.json`: current boot-session verification state.
- `settings.json`: language preference.
- `prompts.db`: SQLite prompt database.

These files are personal data and are excluded by `.gitignore`.

### Packaging

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build.ps1
```

The build script runs tests and `compileall`, then uses PyInstaller to create a Windows single-file EXE, portable ZIP, and SHA256 checksums.

### Author

- Author: HaoXiang Huang
- Email: didadida1688@gmail.com
- Homepage: https://nextweb4.github.io/
- GitHub: https://github.com/NextWeb4

### License

MIT License
