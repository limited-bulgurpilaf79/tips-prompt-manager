# 项目协作规则

## 1. 项目结构
- 当前项目是一个离线 Python/Tkinter 桌面提示词管理器，入口为 `PromptManager.pyw`。
- `prompts.db`、`config.json`、`.auth_session.json` 是用户本机运行数据，不属于可发布源码；发布版必须在首次运行时自动创建这些文件。
- 后续整理源码时，将应用代码放入可导入的 `src/` 包，测试放入 `tests/`，构建脚本放入 `scripts/`，发布产物只放在被 Git 忽略的 `release-assets/`。

## 2. 运行命令
- 当前已发现源码运行方式：`pythonw.exe PromptManager.pyw` 或双击 `启动提示词管理器.bat`。
- 命令行调试时可用：`python PromptManager.pyw`。
- 应用必须保持离线运行，不得要求浏览器、服务端或网络连接。

## 3. 测试命令
- 自动测试：先设置 `$env:PYTHONPATH='src'`，再运行 `python -m unittest discover -s tests -v`。
- 构建后 GUI/ZIP 烟雾测试：`.\tests\run_ui_smoke.ps1`；CI 或无交互桌面时可使用 `-SkipLaunch`。
- 当前未发现独立 lint / format 命令；提交前至少运行 `python -m compileall -q src scripts tests`。

## 4. 构建命令
- 构建命令：`powershell -ExecutionPolicy Bypass -File scripts/build.ps1`。
- 构建脚本必须先运行测试和 `compileall`，再生成 Windows 单文件 EXE、便携 ZIP 和 SHA256。
- 不强行生成 MSI；没有安装器配置时只发布 Windows 单文件 EXE 和便携 ZIP。

## 5. 代码风格
- Python 使用 UTF-8、4 空格缩进、类型提示和小函数；数据库、认证、UI 文案、窗口样式应拆分到职责清晰的模块。
- 中英文 UI 文案集中管理，不在控件创建处散落硬编码文案。
- 不新增非标准库依赖，除非先完成兼容性、许可证、体积、维护状态和离线边界审计。

## 6. 模块边界
- 密码哈希、会话判断和本地配置读写放在认证/配置模块；UI 对话框只调用接口。
- SQLite schema、分类和提示词 CRUD 放在存储模块；UI 不直接拼接业务 SQL。
- Tkinter 组件和窗口布局放在 UI 模块；构建脚本不得导入或修改用户数据库。

## 7. 禁止事项
- 不得提交 `.auth_session.json`、`config.json`、`prompts.db`、本机快捷方式、旧 `.git` 历史、缓存、日志、密钥、令牌或个人提示词内容。
- 不得把密码哈希描述为加密数据库；当前设计只保护启动入口，不加密 `prompts.db` 文件本身。
- 不得引入联网同步、云账号、遥测或自动更新。
- 不得伪造数字签名；无证书时只设置作者、版权、产品名、公司名和版本元数据。

## 8. 完成标准
- 发布版包含可维护源码、双语 README、MIT License、作者信息、可复现构建脚本、测试和 Release Notes。
- 首次运行能创建空数据库、默认分类和本地密码配置；便携 ZIP 解压后可独立运行。
- Release 资产必须包含 EXE、ZIP 和 `SHA256SUMS.txt`。

## 9. Review 标准
- Review 必须核对：离线边界、运行数据排除、密码哈希参数、会话文件失效逻辑、SQLite schema 迁移、CRUD 边界、搜索高亮、剪贴板复制、作者和版本元数据。
- 修改认证、存储或数据迁移逻辑必须增加或更新回归测试。

## 10. 常见风险
- 现有 `prompts.db` 含用户提示词正文，任何导出、测试 fixture 或截图都可能泄露隐私。
- `config.json` 和 `.auth_session.json` 含密码哈希/会话状态，不能进入 Git 或 Release。
- Tkinter 无头环境无法可靠验证完整 GUI；发布前至少做模块测试、构建产物存在性检查和本地启动烟雾测试。
- PyInstaller 单文件包未签名时可能被 Windows Defender 误报；发布说明必须明确未签名状态和 SHA256 校验方式。
