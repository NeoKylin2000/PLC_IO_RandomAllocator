# PLC 实训考核 I/O 随机分配器

模拟考试时对 PLC 实训项目的 I/O 点地址进行随机重新分配，避免考生背诵固定地址，保证考核公平性。

## 功能特性

- 单选模式：每次只选择一个项目进行随机分配
- 八进制地址池：X0-X7, X10-X17... 符合 PLC 地址规范
- 深色/浅色双主题：默认深色主题（Catppuccin Mocha），可一键切换
- 结果保留：切换项目后已分配结果不丢失
- 复制/导出：支持复制当前、复制全部、导出 TXT
- 自定义图标：PLC 主题图标，嵌入 EXE

## 技术栈

| 项目 | 说明 |
|------|------|
| 语言 | Python 3.14 |
| GUI | tkinter + ttk |
| 主题 | Catppuccin Mocha (深色) / Windows 11 (浅色) |
| 窗口效果 | Windows DWM API (圆角 + 深色标题栏) |
| 打包 | PyInstaller --onedir |

## 项目结构

```
plc-io-random-allocator/
├── plc_io_random_allocator.py    # 主程序源代码
├── app_icon.ico                  # 应用图标
├── app_icon.png                  # 图标 PNG
├── PLC_IO_RandomAllocator.spec   # PyInstaller 配置
├── dev_doc.md / .html            # 开发文档
├── handover_doc.md / .html       # 交接文档
└── final_delivery.md / .html     # 最终交付文档
```

## 使用方法

1. 运行 `PLC_IO_RandomAllocator.exe`（需配合 `_internal` 目录）
2. 左侧单选一个实训项目
3. 点击「随机分配」或按 F5
4. 点击「复制全部」导出结果

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| F5 | 随机分配 |
| Ctrl+C | 复制当前结果 |

## 许可证

MIT License