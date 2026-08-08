# PLC 实训考核 I/O 随机分配器 — 最终交付文档

> 本文档由交接文档（handover_doc）与项目技术记忆（project_memory）合并而成，涵盖项目背景、技术架构、迭代历程、核心设计决策、技术经验沉淀、文件清单、已知限制及维护建议，作为最终交付的完整技术资料。

---

## 一、项目概述

### 1.1 任务背景

为 PLC 实训模拟考试场景开发一套 I/O 地址随机分配桌面程序。核心需求是让每个考生在考试时拿到不同的 I/O 地址分配方案，防止背诵固定地址，保证考核公平性。

数据来源为《新实训题 电子及PLC》文档中 5 个 PLC 实训项目的 I/O 分配表，涵盖多种液体混合、花样喷泉、交通灯、简易机械手、运输传送线五个项目，I/O 点数从最少的 7 个（交通灯 3 输入 + 4 输出）到最多的 20 个（机械手 12 输入 + 8 输出）。

### 1.2 项目概况

| 属性 | 内容 |
|------|------|
| 项目名称 | PLC 实训考核 I/O 随机分配器 |
| 项目路径 | `E:\TraeWork\PLC考试IO随机分配` |
| 技术栈 | Python 3.14 + tkinter + ttk + PyInstaller |
| 开始日期 | 2026-08-03 |
| 运行平台 | Windows 10/11 (64 位) |

---

## 二、技术架构

| 层面 | 选型 | 说明 |
|------|------|------|
| 编程语言 | Python 3.14 | 系统安装路径 `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\` |
| GUI 框架 | tkinter + ttk | Python 标准库，无额外依赖 |
| 主题系统 | THEMES 字典 + ttk Style 动态重配 | 运行时切换，无需重启 |
| 窗口效果 | Windows DWM API | 圆角窗口 + 深色标题栏 |
| 打包工具 | PyInstaller 6.21.0 | `--onedir --noconsole --icon` |
| 图标处理 | Pillow | JPG 转 ICO（多尺寸） |

---

## 三、迭代历程

本次开发经历了四轮迭代，每轮均由用户反馈驱动。

### 3.1 初版（多选 + 浅色主题）

首版实现了完整的功能框架：左侧项目列表支持多选（Checkbutton），右侧 Treeview 表格展示分配结果，Windows 11 浅色卡片风格 UI。采用 PyInstaller `--onedir` 模式打包，因中文路径编码问题，最终通过"英文临时目录打包后复制"的策略解决。

### 3.2 单选模式改造

用户反馈"不能全选，每次只能选一个"。将 Checkbutton 替换为 Radiobutton，移除全选/取消按钮，分配逻辑从批量分配改为只对当前选中项目执行。已分配的项目结果会保留，切换项目后可以继续分配。

### 3.3 深色主题

用户要求"加一个深色主题，默认深色主题"。引入了 THEMES 字典管理两套配色方案：深色采用 Catppuccin Mocha 配色（`#1E1E2E` 底色 + `#89B4FA` 蓝色强调），浅色保持原有 Windows 11 风格。标题栏新增主题切换按钮（太阳/月亮图标），点击时重新配置所有 ttk Style、Canvas 背景、Treeview 标签颜色，并通过 Windows DWM API（`DWMWA_USE_IMMERSIVE_DARK_MODE`）同步切换标题栏深浅模式。默认启动深色主题。

### 3.4 自定义图标

用户反馈"左上角的羽毛图标不好看，改掉"。tkinter 默认显示的羽毛（Tcl logo）需要替换。先用 AI 图像生成工具生成了一个 PLC 主题图标（蓝色圆角底 + 白色芯片引脚图案），用 Pillow 转换为多尺寸 ICO 文件（16/32/48/64/128/256）。源代码中优先使用 `iconbitmap` 加载 ICO 文件，找不到时回退到代码绘制的像素图标。同时通过 PyInstaller `--icon` 参数将图标嵌入 EXE 文件本身。

用户随后要求"编译为单文件版"。尝试了 `--onefile --noconsole`、`--onefile --windowed`、`--onefile` + 代码内 `FreeConsole` 三种方案，均在运行时崩溃（退出码 4294967295）。这是 Python 3.14 + PyInstaller 单文件模式的已知兼容性问题。最终与用户确认后回退到 `--onedir` 多文件模式，运行验证通过。

---

## 四、核心设计决策

### 4.1 八进制地址池

PLC 的 I/O 地址按八进制编排（X0-X7, X10-X17...），而非十进制。地址池生成函数利用 Python 的 `oct()` 内置函数实现自动转换，池容量设为 16，足以覆盖所有项目（最大需求 12 输入）。

### 4.2 单选模式下的结果保留

单选模式每次只对一个项目执行分配，但切换到其他项目后，之前已分配的结果不会丢失。`self.results` 字典以项目 ID 为键持久存储，"复制全部"功能可一次性导出所有已分配过的项目。

### 4.3 主题切换的完整性

切换主题时需要同步更新三类组件：ttk Style 配置（按钮、标签、Treeview 等）、非 ttk 组件（tk.Canvas 背景）、Treeview 标签颜色（`tag_configure`）。遗漏任何一类都会导致界面颜色不一致。Windows 标题栏的深浅模式通过 DWM API 的 `DWMWA_USE_IMMERSIVE_DARK_MODE`（属性 ID 20）控制。

### 4.4 中文路径打包策略

PyInstaller 在中文路径下打包可能出现编码问题。采用"英文临时目录打包，再复制到中文目标目录"的两步策略：先将源文件和图标复制到英文路径临时目录，在临时目录执行 PyInstaller，完成后将结果复制到 `E:\TraeWork\PLC考试IO随机分配\`。

---

## 五、技术经验与复用知识

本节沉淀项目开发过程中积累的技术经验，供后续同类项目复用。

### 5.1 Python 3.14 环境信息

- 系统安装路径：`C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe`
- TRAE 内置 Python 缺少 tkinter 模块，需使用系统安装的 Python 3.14
- 验证命令：`& 'C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe' -c "import tkinter; print('OK')"`

### 5.2 PyInstaller 打包经验

- **单文件模式（`--onefile`）不可用**：Python 3.14 + PyInstaller `--onefile` 在 `--noconsole` 和 `--windowed` 模式下打包的 EXE 运行即崩溃（退出码 4294967295）。Console 模式可运行但会闪现控制台窗口
- **推荐方案**：使用 `--onedir` 多文件模式，稳定可靠
- **中文路径问题**：PyInstaller 在中文路径下可能编码错误。策略为英文临时目录打包，再复制到中文目标目录
- **打包参数模板**：`--noconsole --onedir --name <英文名> --icon <ico路径> <源文件>`
- **安装 PyInstaller**：`pip install pyinstaller`

### 5.3 tkinter GUI 开发经验

- **ttk Style 动态切换**：主题切换时调用 `_build_style()` 重新配置所有 ttk Style，需同步更新 ttk Style 配置、tk.Canvas 背景（`configure(bg=...)`）、Treeview 标签颜色（`tag_configure`）
- **ttk theme 选择**：clam 主题兼容性最好（跨平台），vista/winnative 在 Windows 上样式更原生但定制能力有限。推荐先用 clam 再降级
- **Radiobutton 单选模式**：用 `tk.StringVar` 作为 variable，每个 Radiobutton 设置不同的 value，通过 `StringVar.get()` 获取当前选中项

### 5.4 Windows DWM API

- **圆角窗口**：`DwmSetWindowAttribute(hwnd, 33, &2, 4)` — 属性 33 = `DWMWA_WINDOW_CORNER_PREFERENCE`，值 2 = `DWMWCP_ROUND`
- **深色标题栏**：`DwmSetWindowAttribute(hwnd, 20, &1_or_0, 4)` — 属性 20 = `DWMWA_USE_IMMERSIVE_DARK_MODE`，值 1 = 深色，0 = 浅色
- **获取 HWND**：`user32.GetParent(root.winfo_id())` 或 `root.winfo_id()`
- **兼容性**：旧版 Windows 静默跳过（try/except）

### 5.5 自定义图标方案

- **生成流程**：GenerateImage（AI 生成）-> Pillow 转换为多尺寸 ICO -> `root.iconbitmap()` 加载
- **Pillow 安装**：`pip install Pillow`
- **ICO 多尺寸**：`Image.save(path, format="ICO", sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])`
- **回退方案**：代码内用 `tk.PhotoImage` 像素绘制简单图标作为 fallback
- **EXE 图标**：PyInstaller `--icon app_icon.ico` 参数嵌入

### 5.6 Catppuccin Mocha 配色方案（深色主题）

| 色彩变量 | 色值 | 用途 |
|----------|------|------|
| BG | `#1E1E2E` | 主背景 (Mocha base) |
| CARD | `#181825` | 卡片背景 (Mocha mantle) |
| ACCENT | `#89B4FA` | 主题蓝 (Mocha blue) |
| TEXT | `#CDD6F4` | 主文字 (Mocha text) |
| TEXT2 | `#7F849C` | 辅助文字 (Mocha overlay0) |
| BDR | `#313244` | 边框 (Mocha surface0) |
| INPUT | `#89B4FA` | 输入点标签色 (蓝) |
| OUTPUT | `#A6E3A1` | 输出点标签色 (绿) |

### 5.7 全局开发规范要点

- 代码优先 Python，文档输出 md + html 双格式
- 文档字体：微软雅黑（Microsoft YaHei）
- 文件存放：`E:\TraeWork\<中文名任务文件夹>\`
- 文件名：仅英文，见名知意
- 交付前：逐条核对规范 + 内容校验

---

## 六、文件清单

| 文件 | 大小 | 说明 |
|------|------|------|
| `plc_io_random_allocator.py` | 33 KB | 主程序源代码 |
| `app_icon.ico` | 81 KB | 自定义窗口图标（多尺寸） |
| `app_icon.png` | 6 KB | 图标 PNG 版本 |
| `PLC_IO_RandomAllocator.spec` | 1 KB | PyInstaller 打包配置 |
| `PLC_IO_RandomAllocator\PLC_IO_RandomAllocator.exe` | 2.2 MB | 可执行文件（--onedir 模式） |
| `dev_doc.md` | 7 KB | 开发文档（Markdown） |
| `dev_doc.html` | 11 KB | 开发文档（网页） |
| `handover_doc.md` | 5 KB | 交接文档（Markdown） |
| `handover_doc.html` | 9 KB | 交接文档（网页） |
| `final_delivery.md` | — | 最终交付文档（Markdown） |
| `final_delivery.html` | — | 最终交付文档（网页） |

---

## 七、已知限制

**单文件打包不可用**：Python 3.14 与 PyInstaller `--onefile` 模式存在兼容性问题，`--noconsole` 和 `--windowed` 模式下打包的 EXE 运行即崩溃（退出码 4294967295）。Console 模式可以运行但会闪现控制台窗口。当前使用 `--onedir` 多文件模式作为替代方案，EXE 依赖同目录下的 `_internal` 文件夹。

**主题切换不持久化**：切换主题后重启程序会恢复为默认深色主题。如需持久化，可在用户目录下保存主题偏好配置文件。

---

## 八、教训与注意事项

1. **先验证语法再打包**：每次修改源代码后，先用 `py_compile` 验证语法，再执行打包
2. **打包后必须运行验证**：EXE 生成后用 `subprocess.Popen` 启动，等待 6-8 秒检查进程是否存活
3. **临时脚本放工作目录**：所有临时脚本放在 `c:\Users\Administrator\.trae-cn\work\...` 下，不污染用户工作区
4. **修改源代码用脚本**：因路径限制无法直接编辑 E 盘文件，需编写 Python 脚本执行读取-修改-写回操作

---

## 九、后续维护建议

- 如需修改项目数据（I/O 点名称、数量），直接编辑源代码顶部的 `PROJECTS` 列表
- 如需扩展地址池容量，修改 `POOL_SIZE` 常量（当前为 16）
- 如需调整配色，编辑 `THEMES` 字典中对应主题的颜色值
- 重新打包时运行打包脚本，该脚本自动完成清理、打包、复制、验证全流程
- 如未来 PyInstaller 修复 Python 3.14 单文件兼容性，可将打包参数改回 `--onefile`