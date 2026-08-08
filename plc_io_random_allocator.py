# -*- coding: utf-8 -*-
"""
PLC 实训考核 I/O 随机分配器
============================================================
用途: 模拟考试时对 PLC 实训项目的 I/O 点地址进行随机重新分配,
      避免考生背诵固定地址, 保证考核公平性。
规则: 单选模式, 每次只选一个项目, 从八进制地址池中随机抽取(项目内不重复)。
技术: Python + tkinter, 支持深色/浅色双主题, 默认深色主题。
============================================================
"""

import os
import sys
import random
import ctypes
import ctypes.wintypes
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


# ======================== Windows 11 DWM API ========================
DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWCP_ROUND = 2
DWMWA_USE_IMMERSIVE_DARK_MODE = 20  # Windows 11 深色标题栏

dwmapi = ctypes.windll.dwmapi
dwmapi.DwmSetWindowAttribute.argtypes = [
    ctypes.wintypes.HWND, ctypes.wintypes.DWORD,
    ctypes.c_void_p, ctypes.wintypes.DWORD,
]
dwmapi.DwmSetWindowAttribute.restype = ctypes.wintypes.HRESULT

user32 = ctypes.windll.user32


def apply_window_effects(root, dark=True):
    """为窗口应用 Windows 11 圆角 + 深色/浅色标题栏(旧系统静默跳过)。"""
    try:
        hwnd = user32.GetParent(root.winfo_id()) or root.winfo_id()
        # 圆角
        pref = ctypes.c_int(DWMWCP_ROUND)
        dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_WINDOW_CORNER_PREFERENCE,
            ctypes.byref(pref), ctypes.sizeof(pref)
        )
        # 深色/浅色标题栏
        dark_val = ctypes.c_int(1 if dark else 0)
        dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(dark_val), ctypes.sizeof(dark_val)
        )
    except Exception:
        pass


# ======================== 主题配色方案 ========================
# 深色主题: Catppuccin Mocha 风格
# 浅色主题: Windows 11 浅色风格
THEMES = {
    "dark": {
        "BG":        "#1E1E2E",   # 主背景 (Mocha base)
        "CARD":      "#181825",   # 卡片背景 (Mocha mantle)
        "ACCENT":    "#89B4FA",   # 主题蓝 (Mocha blue)
        "ACCENT_H":  "#B4BEFE",   # 悬停 (Mocha lavender)
        "ACCENT_P":  "#74C7EC",   # 按下 (Mocha sapphire)
        "TEXT":      "#CDD6F4",   # 主文字 (Mocha text)
        "TEXT2":     "#7F849C",   # 辅助文字 (Mocha overlay0)
        "BDR":       "#313244",   # 浅边框 (Mocha surface0)
        "BDR2":      "#45475A",   # 深边框 (Mocha surface1)
        "BTN_FACE":  "#313244",   # 按钮面
        "BTN_HOVER": "#45475A",   # 按钮悬停
        "SEL_BG":    "#3B4252",   # 选中行背景
        "SEL_FG":    "#CDD6F4",   # 选中行文字
        "HEADER_BG": "#181825",   # 表头背景
        "INPUT_C":   "#89B4FA",   # 输入点标签色 (蓝)
        "OUTPUT_C":  "#A6E3A1",   # 输出点标签色 (绿)
        "ROW_ALT":   "#181825",   # 斑马纹交替行
        "ACCENT_FG": "#1E1E2E",   # 强调按钮文字色 (深底浅字反过来)
    },
    "light": {
        "BG":        "#F3F3F3",   # 主背景
        "CARD":      "#FFFFFF",   # 卡片白
        "ACCENT":    "#0078D4",   # 主题蓝
        "ACCENT_H":  "#106EBE",   # 悬停深蓝
        "ACCENT_P":  "#005A9E",   # 按下深蓝
        "TEXT":      "#1A1A1A",   # 主文字
        "TEXT2":     "#6B6B6B",   # 辅助文字
        "BDR":       "#E5E5E5",   # 浅边框
        "BDR2":      "#D1D1D1",   # 深边框
        "BTN_FACE":  "#FAFAFA",   # 按钮面
        "BTN_HOVER": "#F0F0F0",   # 按钮悬停
        "SEL_BG":    "#CCE4F7",   # 选中行背景
        "SEL_FG":    "#1A1A1A",   # 选中行文字
        "HEADER_BG": "#F5F5F5",   # 表头背景
        "INPUT_C":   "#0078D4",   # 输入点标签色
        "OUTPUT_C":  "#107C10",   # 输出点标签色 (绿)
        "ROW_ALT":   "#FAFAFA",   # 斑马纹交替行
        "ACCENT_FG": "#FFFFFF",   # 强调按钮文字色
    },
}

FONT = "Microsoft YaHei UI"   # 微软雅黑


# ======================== PLC 实训项目数据 ========================
PROJECTS = [
    {
        "id": "plc1",
        "name": "PLC\u5b9e\u8bad\u4e00  \u591a\u79cd\u6db2\u4f53\u6df7\u5408",
        "short": "\u591a\u79cd\u6db2\u4f53\u6df7\u5408",
        "inputs": [
            "\u542f\u52a8", "\u624b\u52a8/\u81ea\u52a8", "\u6db2\u4f4dL", "\u6db2\u4f4dM", "\u6db2\u4f4dH",
            "\u505c\u6b62", "\u6025\u505c", "\u624b\u52a8\u6d41\u5165A", "\u624b\u52a8\u6d41\u5165B", "\u624b\u52a8\u6d41\u51faC", "\u624b\u52a8\u6405\u62ccM",
        ],
        "outputs": ["\u6405\u62cc\u7535\u52a8\u673aM", "\u9600\u95e8YV1", "\u9600\u95e8YV2", "\u9600\u95e8YV3"],
    },
    {
        "id": "plc2",
        "name": "PLC\u5b9e\u8bad\u4e8c  \u82b1\u6837\u55b7\u6cc9",
        "short": "\u82b1\u6837\u55b7\u6cc9",
        "inputs": ["\u542f\u52a8", "\u82b1\u6837\u9009\u62e91", "\u82b1\u6837\u9009\u62e92", "\u505c\u6b62"],
        "outputs": ["\u55b7\u59341 KM1", "\u55b7\u59342 KM2", "\u55b7\u59343 KM3", "\u55b7\u59344 KM4"],
    },
    {
        "id": "plc3",
        "name": "PLC\u5b9e\u8bad\u4e09  \u4ea4\u901a\u706f",
        "short": "\u4ea4\u901a\u706f",
        "inputs": ["\u542f\u52a8", "\u505c\u6b62", "\u767d\u5929/\u591c\u95f4\u9009\u62e9"],
        "outputs": [
            "\u4e1c\u897f\u5411\u7ea2\u706f", "\u4e1c\u897f\u5411\u7eff\u706f", "\u4e1c\u897f\u5411\u9ec4\u706f",
            "\u5357\u5317\u5411\u7ea2\u706f", "\u5357\u5317\u5411\u7eff\u706f", "\u5357\u5317\u5411\u9ec4\u706f",
        ],
    },
    {
        "id": "plc4",
        "name": "PLC\u5b9e\u8bad\u56db  \u7b80\u6613\u673a\u68b0\u624b",
        "short": "\u7b80\u6613\u673a\u68b0\u624b",
        "inputs": [
            "\u81ea\u52a8/\u624b\u52a8\u8f6c\u6362", "\u505c\u6b62", "\u81ea\u52a8\u8d77\u52a8",
            "\u4e0a\u9650\u4f4dSQ2", "\u4e0b\u9650\u4f4dSQ1", "\u5de6\u9650\u4f4dSQ4", "\u53f3\u9650\u4f4dSQ3",
            "\u624b\u52a8\u4e0a\u5347", "\u624b\u52a8\u4e0b\u964d", "\u624b\u52a8\u5de6\u79fb", "\u624b\u52a8\u53f3\u79fb", "\u624b\u52a8\u653e\u677e",
        ],
        "outputs": [
            "\u5939\u7d27/\u653e\u677e", "\u4e0a\u5347", "\u4e0b\u964d", "\u5de6\u79fb", "\u53f3\u79fb",
            "\u539f\u70b9\u6307\u793a", "\u8fd0\u884c\u6307\u793a\u706f", "\u505c\u6b62\u6307\u793a\u706f",
        ],
    },
    {
        "id": "plc5",
        "name": "PLC\u5b9e\u8bad\u4e94  \u8fd0\u8f93\u4f20\u9001\u7ebf",
        "short": "\u8fd0\u8f93\u4f20\u9001\u7ebf",
        "inputs": [
            "\u81ea\u52a8/\u624b\u52a8\u5f00\u5173", "\u81ea\u52a8\u8d77\u52a8", "\u6b63\u5e38\u505c\u6b62", "\u7d27\u6025\u505c\u6b62",
            "\u70b9\u52a8\u7535\u78c1\u9600", "\u70b9\u52a8M1", "\u70b9\u52a8M2", "\u70b9\u52a8M3", "\u70b9\u52a8M4",
            "\u6ee1\u4ed3\u4fe1\u53f7", "\u7a7a\u4ed3\u4fe1\u53f7", "\u70ed\u7ee7\u7535\u5668FR",
        ],
        "outputs": ["\u7535\u78c1\u9600DT", "M1\u7535\u52a8\u673a", "M2\u7535\u52a8\u673a", "M3\u7535\u52a8\u673a", "M4\u7535\u52a8\u673a"],
    },
]

# ======================== 八进制地址池 ========================
POOL_SIZE = 16


def gen_octal_pool(prefix, count):
    pool = []
    for i in range(count):
        pool.append(f"{prefix}{oct(i)[2:]}")
    return pool


X_POOL = gen_octal_pool("X", POOL_SIZE)
Y_POOL = gen_octal_pool("Y", POOL_SIZE)


def random_allocate(points, pool):
    n = len(points)
    if n > len(pool):
        raise ValueError(f"\u5730\u5740\u6c60\u5bb9\u91cf\u4e0d\u8db3: \u9700\u8981 {n} \u4e2a, \u4ec5\u6709 {len(pool)} \u4e2a")
    addrs = random.sample(pool, n)
    return list(zip(points, addrs))


# ======================== 主界面 ========================
class Application:
    """PLC I/O \u968f\u673a\u5206\u914d\u5668\u4e3b\u754c\u9762\u3002"""

    def __init__(self, root):
        self.root = root
        self.root.title("PLC \u5b9e\u8bad\u8003\u6838 I/O \u968f\u673a\u5206\u914d\u5668")
        self.root.geometry("980x620")
        self.root.minsize(860, 520)

        # 当前主题 (默认深色)
        self.theme_name = "dark"
        self.C = THEMES[self.theme_name]

        # 数据
        self.results = {}
        self.selected_project = tk.StringVar(value=PROJECTS[0]["id"])
        self.current_project = PROJECTS[0]["id"]

        self._build_style()
        self._build_ui()
        apply_window_effects(self.root, dark=(self.theme_name == "dark"))

        # 启动时自动执行一次随机分配
        self.do_allocate(silent=True)
        self._show_project(self.current_project)

        # 快捷键
        self.root.bind("<F5>", lambda e: self.do_allocate())
        self.root.bind("<Control-c>", lambda e: self.copy_current())

    @property
    def colors(self):
        return THEMES[self.theme_name]

    # -------------------- 样式 --------------------
    def _build_style(self):
        """构建/刷新所有 ttk 样式 (使用当前主题颜色)。"""
        c = self.colors
        style = ttk.Style()
        for theme in ("clam", "vista", "winnative"):
            try:
                style.theme_use(theme)
                break
            except Exception:
                continue

        style.configure(".", background=c["BG"], foreground=c["TEXT"], font=(FONT, 10))
        style.map(".", background=[("active", c["BG"])])

        # 普通按钮
        style.configure("TButton", background=c["BTN_FACE"], foreground=c["TEXT"],
                        bordercolor=c["BDR2"], borderwidth=1, padding=(12, 5),
                        font=(FONT, 10))
        style.map("TButton",
                  background=[("active", c["BTN_HOVER"]), ("pressed", c["BDR2"])],
                  bordercolor=[("active", c["ACCENT"])])

        # 强调按钮 (随机分配)
        style.configure("Accent.TButton", background=c["ACCENT"], foreground=c["ACCENT_FG"],
                        bordercolor=c["ACCENT"], borderwidth=1, padding=(16, 6),
                        font=(FONT, 10, "bold"))
        style.map("Accent.TButton",
                  background=[("active", c["ACCENT_H"]), ("pressed", c["ACCENT_P"])],
                  bordercolor=[("active", c["ACCENT_H"])])

        # 主题切换按钮 (小型)
        style.configure("Icon.TButton", background=c["BTN_FACE"], foreground=c["TEXT"],
                        bordercolor=c["BDR2"], borderwidth=1, padding=(8, 4),
                        font=(FONT, 11))
        style.map("Icon.TButton",
                  background=[("active", c["BTN_HOVER"]), ("pressed", c["BDR2"])])

        # 标签
        style.configure("TLabel", background=c["BG"], foreground=c["TEXT"], font=(FONT, 10))
        style.configure("Card.TLabel", background=c["CARD"], foreground=c["TEXT"], font=(FONT, 10))
        style.configure("Muted.TLabel", background=c["BG"], foreground=c["TEXT2"], font=(FONT, 9))
        style.configure("CardMuted.TLabel", background=c["CARD"], foreground=c["TEXT2"], font=(FONT, 9))
        style.configure("Title.TLabel", background=c["BG"], foreground=c["TEXT"], font=(FONT, 15, "bold"))
        style.configure("Sub.TLabel", background=c["BG"], foreground=c["TEXT2"], font=(FONT, 9))

        # 标签框
        style.configure("TLabelframe", background=c["BG"], bordercolor=c["BDR"],
                        borderwidth=1, padding=10, relief=tk.FLAT)
        style.configure("TLabelframe.Label", background=c["BG"],
                        foreground=c["TEXT"], font=(FONT, 10, "bold"))

        # 单选按钮
        style.configure("TRadiobutton", background=c["BG"], foreground=c["TEXT"],
                        font=(FONT, 10), padding=(2, 2))
        style.map("TRadiobutton", background=[("active", c["BG"])],
                  indicatorcolor=[("selected", c["ACCENT"])])

        # Treeview
        style.configure("Treeview", background=c["CARD"], foreground=c["TEXT"],
                        fieldbackground=c["CARD"], bordercolor=c["BDR"], borderwidth=1,
                        font=(FONT, 10), rowheight=26)
        style.map("Treeview",
                  background=[("selected", c["SEL_BG"])],
                  foreground=[("selected", c["SEL_FG"])])
        style.configure("Treeview.Heading", background=c["HEADER_BG"],
                        foreground=c["TEXT"], font=(FONT, 10, "bold"),
                        bordercolor=c["BDR"], borderwidth=1, padding=(6, 6))
        style.map("Treeview.Heading", background=[("active", c["BTN_HOVER"])])

        style.configure("TSeparator", background=c["BDR"])

        # 滚动条
        style.configure("TScrollbar", background=c["BTN_FACE"],
                        troughcolor=c["BG"], bordercolor=c["BDR"],
                        arrowcolor=c["TEXT2"])
        style.map("TScrollbar",
                  background=[("active", c["BTN_HOVER"])])

    # -------------------- 界面构建 --------------------
    def _build_ui(self):
        c = self.colors
        self.root.configure(bg=c["BG"])
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # ===== 顶部标题栏 (row 0) =====
        header = ttk.Frame(self.root, padding=(16, 12, 16, 8))
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ttk.Label(header, text="PLC \u5b9e\u8bad\u8003\u6838 I/O \u968f\u673a\u5206\u914d\u5668",
                  style="Title.TLabel").pack(side=tk.LEFT)
        ttk.Label(header,
                  text=f"\u5730\u5740\u6c60  \u8f93\u5165 {X_POOL[0]}-{X_POOL[-1]}   \u8f93\u51fa {Y_POOL[0]}-{Y_POOL[-1]}   \u516b\u8fdb\u5236\u7f16\u6392",
                  style="Sub.TLabel").pack(side=tk.LEFT, padx=(16, 0), pady=(4, 0))

        # 右侧按钮组: 主题切换 + 关于
        right_btns = ttk.Frame(header)
        right_btns.pack(side=tk.RIGHT)

        self.theme_btn = ttk.Button(right_btns, text="\u6df1\u8272",
                                    command=self.toggle_theme, style="Icon.TButton", width=6)
        self.theme_btn.pack(side=tk.LEFT, padx=(0, 6))

        ttk.Button(right_btns, text="\u5173\u4e8e", command=self.show_about,
                   width=8).pack(side=tk.LEFT)

        # ===== 主内容区 (row 1) =====
        body = ttk.Frame(self.root, padding=(16, 0, 16, 0))
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)

        # --- 左侧项目面板 ---
        left = ttk.Frame(body, width=280)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.grid_propagate(False)
        left.grid_rowconfigure(1, weight=1)
        left.grid_columnconfigure(0, weight=1)

        lp_header = ttk.Frame(left)
        lp_header.grid(row=0, column=0, sticky="ew")
        ttk.Label(lp_header, text="\u5b9e\u8bad\u9879\u76ee", font=(FONT, 11, "bold")).pack(side=tk.LEFT)
        ttk.Label(lp_header, text="(\u5355\u9009)", style="Muted.TLabel"
                  ).pack(side=tk.LEFT, padx=(8, 0))

        list_wrap = ttk.Frame(left)
        list_wrap.grid(row=1, column=0, sticky="nsew")
        list_wrap.grid_rowconfigure(0, weight=1)
        list_wrap.grid_columnconfigure(0, weight=1)

        self.proj_canvas = tk.Canvas(list_wrap, bg=c["BG"], highlightthickness=0)
        vsb = ttk.Scrollbar(list_wrap, orient=tk.VERTICAL,
                            command=self.proj_canvas.yview)
        self.proj_canvas.configure(yscrollcommand=vsb.set)
        self.proj_canvas.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        self.proj_inner = ttk.Frame(self.proj_canvas)
        self.proj_inner.bind("<Configure>",
                             lambda e: self.proj_canvas.configure(
                                 scrollregion=self.proj_canvas.bbox("all")))
        self.proj_canvas.create_window((0, 0), window=self.proj_inner, anchor="nw")
        self.proj_inner.grid_columnconfigure(0, weight=1)

        self.proj_canvas.bind("<Enter>",
                              lambda e: self.proj_canvas.bind_all("<MouseWheel>", self._on_wheel))
        self.proj_canvas.bind("<Leave>",
                              lambda e: self.proj_canvas.unbind_all("<MouseWheel>"))

        self._build_project_cards()

        # --- 右侧结果面板 ---
        right = ttk.Frame(body)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        toolbar = ttk.Frame(right)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.proj_title_var = tk.StringVar(value="")
        ttk.Label(toolbar, textvariable=self.proj_title_var,
                  font=(FONT, 11, "bold")).pack(side=tk.LEFT)

        btns = ttk.Frame(toolbar)
        btns.pack(side=tk.RIGHT)
        ttk.Button(btns, text="\u968f\u673a\u5206\u914d", command=self.do_allocate,
                   style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(btns, text="\u590d\u5236\u5f53\u524d", command=self.copy_current, width=10
                   ).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(btns, text="\u590d\u5236\u5168\u90e8", command=self.copy_all, width=10
                   ).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(btns, text="\u5bfc\u51faTXT", command=self.export_txt, width=10
                   ).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(btns, text="\u91cd\u7f6e", command=self.reset_all, width=8
                   ).pack(side=tk.LEFT)

        # 结果表格
        tree_frame = ttk.Frame(right)
        tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        columns = ("idx", "name", "type", "addr")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                 selectmode="browse", height=18)
        col_cfg = {
            "idx":   ("\u5e8f\u53f7", 60, tk.CENTER),
            "name":  ("I/O \u529f\u80fd\u540d\u79f0", 280, tk.W),
            "type":  ("\u7c7b\u578b", 90, tk.CENTER),
            "addr":  ("\u5206\u914d\u5730\u5740", 120, tk.CENTER),
        }
        for col_key in columns:
            title, w, anchor = col_cfg[col_key]
            self.tree.heading(col_key, text=title)
            self.tree.column(col_key, width=w, anchor=anchor, minwidth=50)
        self.tree.column("name", stretch=True)

        vsb2 = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb2.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb2.grid(row=0, column=1, sticky="ns")

        self._apply_tree_tags()

        # ===== 底部状态栏 (row 2) =====
        status = ttk.Frame(self.root, relief=tk.FLAT)
        status.grid(row=2, column=0, sticky="ew")
        ttk.Separator(status, orient=tk.HORIZONTAL).pack(fill=tk.X)
        self.status_var = tk.StringVar(value="\u5c31\u7eea")
        ttk.Label(status, textvariable=self.status_var, style="Muted.TLabel",
                  padding=(12, 4)).pack(side=tk.LEFT)
        ttk.Label(status, text="F5 \u968f\u673a\u5206\u914d  Ctrl+C \u590d\u5236\u5f53\u524d",
                  style="Muted.TLabel", padding=(12, 4)).pack(side=tk.RIGHT)

    def _apply_tree_tags(self):
        """根据当前主题配置 Treeview 标签颜色。"""
        c = self.colors
        self.tree.tag_configure("input", foreground=c["INPUT_C"])
        self.tree.tag_configure("output", foreground=c["OUTPUT_C"])
        self.tree.tag_configure("alt", background=c["ROW_ALT"])

    def _build_project_cards(self):
        """构建左侧项目卡片列表(单选模式)。"""
        for p in PROJECTS:
            card = ttk.Frame(self.proj_inner, relief=tk.FLAT, padding=(8, 8))
            card.grid(sticky="ew", pady=(0, 6))
            card.grid_columnconfigure(1, weight=1)

            rb = ttk.Radiobutton(card, variable=self.selected_project,
                                 value=p["id"],
                                 command=lambda pid=p["id"]: self._on_select(pid))
            rb.grid(row=0, column=0, sticky="ns", padx=(0, 6))

            info = ttk.Frame(card)
            info.grid(row=0, column=1, sticky="ew")
            name_lbl = ttk.Label(info, text=p["short"], font=(FONT, 10, "bold"),
                                 cursor="hand2")
            name_lbl.pack(anchor=tk.W)
            n_in = len(p["inputs"])
            n_out = len(p["outputs"])
            ttk.Label(info, text=f"{n_in} \u8f93\u5165  /  {n_out} \u8f93\u51fa",
                      style="Muted.TLabel").pack(anchor=tk.W)

            for w in (card, name_lbl, info):
                w.bind("<Button-1>", lambda e, pid=p["id"]: self._on_select(pid))

    def _on_wheel(self, event):
        self.proj_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # -------------------- 主题切换 --------------------
    def toggle_theme(self):
        """在深色/浅色主题之间切换。"""
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        self.C = THEMES[self.theme_name]
        c = self.colors

        # 重新构建所有样式
        self._build_style()

        # 更新非 ttk 组件背景
        self.root.configure(bg=c["BG"])
        self.proj_canvas.configure(bg=c["BG"])

        # 更新 Treeview 标签颜色
        self._apply_tree_tags()

        # 更新主题按钮图标
        if self.theme_name == "dark":
            self.theme_btn.configure(text="\u6df1\u8272")   # 当前深色
        else:
            self.theme_btn.configure(text="\u6d45\u8272")   # 当前浅色

        # 更新窗口标题栏颜色
        apply_window_effects(self.root, dark=(self.theme_name == "dark"))

        # 刷新表格以应用新颜色
        self._refresh_tree(self.current_project)

        self._set_status(f"\u5df2\u5207\u6362\u81f3{'\u6df1\u8272' if self.theme_name == 'dark' else '\u6d45\u8272'}\u4e3b\u9898")

    # -------------------- 项目选择 --------------------
    def _on_select(self, pid):
        self.selected_project.set(pid)
        self._show_project(pid)

    def _show_project(self, pid):
        self.current_project = pid
        proj = self._get_project(pid)
        self.proj_title_var.set(proj["name"])
        self._refresh_tree(pid)
        self._set_status(f"\u5f53\u524d\u67e5\u770b: {proj['short']}")

    def _get_project(self, pid):
        for p in PROJECTS:
            if p["id"] == pid:
                return p
        return PROJECTS[0]

    # -------------------- 随机分配 --------------------
    def do_allocate(self, silent=False):
        pid = self.selected_project.get()
        p = self._get_project(pid)

        in_alloc = random_allocate(p["inputs"], X_POOL)
        out_alloc = random_allocate(p["outputs"], Y_POOL)
        self.results[p["id"]] = {
            "inputs": in_alloc,
            "outputs": out_alloc,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        self.current_project = pid
        self._refresh_tree(pid)
        self._set_status(f"\u5df2\u5b8c\u6210\u968f\u673a\u5206\u914d: {p['short']}")

    def _refresh_tree(self, pid):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if pid not in self.results:
            return

        res = self.results[pid]
        idx = 0
        row_alt = False
        for name, addr in res["inputs"]:
            tags = ["input"]
            if row_alt:
                tags.append("alt")
            idx += 1
            self.tree.insert("", tk.END, values=(idx, name, "\u8f93\u5165", addr), tags=tags)
            row_alt = not row_alt

        for name, addr in res["outputs"]:
            tags = ["output"]
            if row_alt:
                tags.append("alt")
            idx += 1
            self.tree.insert("", tk.END, values=(idx, name, "\u8f93\u51fa", addr), tags=tags)
            row_alt = not row_alt

    # -------------------- 复制 / 导出 --------------------
    def _format_project(self, pid, with_header=True):
        proj = self._get_project(pid)
        res = self.results.get(pid)
        lines = []
        if with_header:
            lines.append("=" * 48)
            lines.append(f"  {proj['name']}")
            if res:
                lines.append(f"  \u5206\u914d\u65f6\u95f4: {res['time']}")
            lines.append("=" * 48)
        if not res:
            lines.append("  (\u5c1a\u672a\u5206\u914d)")
            return "\n".join(lines)

        lines.append("")
        lines.append("  \u3010\u8f93\u5165\u70b9 X\u3011")
        for name, addr in res["inputs"]:
            lines.append(f"    {addr:<6}  {name}")

        lines.append("")
        lines.append("  \u3010\u8f93\u51fa\u70b9 Y\u3011")
        for name, addr in res["outputs"]:
            lines.append(f"    {addr:<6}  {name}")
        lines.append("")
        return "\n".join(lines)

    def copy_current(self):
        text = self._format_project(self.current_project)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        proj = self._get_project(self.current_project)
        self._set_status(f"\u5df2\u590d\u5236: {proj['short']} \u7684\u5206\u914d\u7ed3\u679c")

    def copy_all(self):
        parts = []
        for p in PROJECTS:
            if p["id"] in self.results:
                parts.append(self._format_project(p["id"]))
        if not parts:
            messagebox.showinfo("\u63d0\u793a", "\u6682\u65e0\u5206\u914d\u7ed3\u679c, \u8bf7\u5148\u6267\u884c\u968f\u673a\u5206\u914d")
            return
        text = "\n".join(parts)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self._set_status(f"\u5df2\u590d\u5236\u5168\u90e8 {len(parts)} \u4e2a\u9879\u76ee\u7684\u5206\u914d\u7ed3\u679c")

    def export_txt(self):
        parts = []
        for p in PROJECTS:
            if p["id"] in self.results:
                parts.append(self._format_project(p["id"]))
        if not parts:
            messagebox.showinfo("\u63d0\u793a", "\u6682\u65e0\u5206\u914d\u7ed3\u679c, \u8bf7\u5148\u6267\u884c\u968f\u673a\u5206\u914d")
            return

        default_name = f"PLC_IO_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        path = filedialog.asksaveasfilename(
            title="\u5bfc\u51fa I/O \u5206\u914d\u7ed3\u679c",
            initialfile=default_name,
            defaultextension=".txt",
            filetypes=[("\u6587\u672c\u6587\u4ef6", "*.txt"), ("\u6240\u6709\u6587\u4ef6", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(parts))
            self._set_status(f"\u5df2\u5bfc\u51fa: {path}")
            if messagebox.askyesno("\u5bfc\u51fa\u6210\u529f", f"\u5df2\u4fdd\u5b58\u5230:\n{path}\n\n\u662f\u5426\u7acb\u5373\u6253\u5f00?"):
                os.startfile(path)
        except Exception as e:
            messagebox.showerror("\u5bfc\u51fa\u5931\u8d25", str(e))

    # -------------------- 重置 --------------------
    def reset_all(self):
        if not self.results:
            return
        if messagebox.askyesno("\u786e\u8ba4\u91cd\u7f6e", "\u5c06\u6e05\u7a7a\u6240\u6709\u9879\u76ee\u7684\u5206\u914d\u7ed3\u679c, \u786e\u5b9a\u5417?"):
            self.results.clear()
            self._refresh_tree(self.current_project)
            self._set_status("\u5df2\u91cd\u7f6e, \u6240\u6709\u5206\u914d\u7ed3\u679c\u5df2\u6e05\u7a7a")

    # -------------------- 工具方法 --------------------
    def _set_status(self, text):
        self.status_var.set(text)

    def show_about(self):
        messagebox.showinfo("\u5173\u4e8e",
            "PLC \u5b9e\u8bad\u8003\u6838 I/O \u968f\u673a\u5206\u914d\u5668\n\n"
            "\u7528\u9014: \u6a21\u62df\u8003\u8bd5\u65f6\u5bf9 PLC \u5b9e\u8bad\u9879\u76ee\u7684 I/O \u70b9\u5730\u5740\n"
            "      \u8fdb\u884c\u968f\u673a\u91cd\u65b0\u5206\u914d, \u4fdd\u8bc1\u8003\u6838\u516c\u5e73\u6027\u3002\n\n"
            "\u89c4\u5219: \u5355\u9009\u6a21\u5f0f, \u4ece\u516b\u8fdb\u5236\u5730\u5740\u6c60\n"
            "      \u968f\u673a\u62bd\u53d6(\u9879\u76ee\u5185\u4e0d\u91cd\u590d)\u3002\n\n"
            f"\u8f93\u5165\u5730\u5740\u6c60: {X_POOL[0]}-{X_POOL[-1]}  (\u5171 {len(X_POOL)} \u4e2a)\n"
            f"\u8f93\u51fa\u5730\u5740\u6c60: {Y_POOL[0]}-{Y_POOL[-1]}  (\u5171 {len(Y_POOL)} \u4e2a)\n\n"
            "\u5305\u542b\u9879\u76ee: 5 \u4e2a PLC \u5b9e\u8bad\n"
            "\u4e3b\u9898: \u6df1\u8272/\u6d45\u8272\u53cc\u4e3b\u9898 (\u9ed8\u8ba4\u6df1\u8272)\n"
            "\u6280\u672f\u5b9e\u73b0: Python + tkinter")


# ======================== 窗口图标 ========================
def make_app_icon(size=32):
    """用 PhotoImage 像素绘制 PLC 主题图标 (蓝底白色芯片图案)。"""
    img = tk.PhotoImage(width=size, height=size)

    # 配色
    bg_color  = "#0078D4"   # 蓝色底
    bg_dark   = "#005A9E"   # 深蓝边
    chip_fill = "#FFFFFF"   # 白色芯片
    pin_color = "#FFFFFF"   # 白色引脚
    center    = "#89B4FA"   # 中心点浅蓝
    transparent = ""        # 透明

    m = 2   # 外边距

    # 填充圆角蓝色背景
    for y in range(size):
        for x in range(size):
            # 圆角判断: 四角透明
            corner_r = 6
            in_corner = False
            # 左上
            if x < m + corner_r and y < m + corner_r:
                dx = (m + corner_r) - x
                dy = (m + corner_r) - y
                if dx * dx + dy * dy > corner_r * corner_r:
                    in_corner = True
            # 右上
            elif x >= size - m - corner_r and y < m + corner_r:
                dx = x - (size - m - corner_r - 1)
                dy = (m + corner_r) - y
                if dx * dx + dy * dy > corner_r * corner_r:
                    in_corner = True
            # 左下
            elif x < m + corner_r and y >= size - m - corner_r:
                dx = (m + corner_r) - x
                dy = y - (size - m - corner_r - 1)
                if dx * dx + dy * dy > corner_r * corner_r:
                    in_corner = True
            # 右下
            elif x >= size - m - corner_r and y >= size - m - corner_r:
                dx = x - (size - m - corner_r - 1)
                dy = y - (size - m - corner_r - 1)
                if dx * dx + dy * dy > corner_r * corner_r:
                    in_corner = True

            if in_corner or x < m or x >= size - m or y < m or y >= size - m:
                img.transparency_set(x, y, True)
            else:
                img.put(bg_color, (x, y))

    # 绘制中心芯片方块 (白色)
    chip_x1, chip_y1 = 10, 10
    chip_x2, chip_y2 = 21, 21

    for y in range(chip_y1, chip_y2 + 1):
        for x in range(chip_x1, chip_x2 + 1):
            img.put(chip_fill, (x, y))

    # 绘制引脚 (上下左右各3个)
    pin_len = 3
    # 上方引脚
    for px in (12, 15, 18):
        for py in range(chip_y1 - pin_len, chip_y1):
            if 0 <= px < size and 0 <= py < size:
                img.put(pin_color, (px, py))
    # 下方引脚
    for px in (12, 15, 18):
        for py in range(chip_y2 + 1, chip_y2 + 1 + pin_len):
            if 0 <= px < size and 0 <= py < size:
                img.put(pin_color, (px, py))
    # 左方引脚
    for py in (12, 15, 18):
        for px in range(chip_x1 - pin_len, chip_x1):
            if 0 <= px < size and 0 <= py < size:
                img.put(pin_color, (px, py))
    # 右方引脚
    for py in (12, 15, 18):
        for px in range(chip_x2 + 1, chip_x2 + 1 + pin_len):
            if 0 <= px < size and 0 <= py < size:
                img.put(pin_color, (px, py))

    # 中心点 (浅蓝)
    for y in range(14, 18):
        for x in range(14, 18):
            img.put(center, (x, y))

    return img


# ======================== 程序入口 ========================
def main():
    if os.name != "nt":
        print("\u6b64\u7a0b\u5e8f\u4ec5\u652f\u6301 Windows \u7cfb\u7edf\u3002")
        sys.exit(1)

    root = tk.Tk()
    # 设置自定义窗口图标 (替换默认羽毛图标)
    try:
        _ico = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_icon.ico")
        if os.path.isfile(_ico):
            root.iconbitmap(_ico)
        else:
            _icon = make_app_icon(32)
            root.iconphoto(False, _icon)
    except Exception:
        try:
            _icon = make_app_icon(32)
            root.iconphoto(False, _icon)
        except Exception:
            pass
    app = Application(root)

    # 窗口居中
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    root.geometry(f"+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    main()
