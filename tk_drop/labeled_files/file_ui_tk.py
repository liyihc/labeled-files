
import base64
from dataclasses import dataclass
from datetime import datetime
import io
from pathlib import Path
import tkinter as tk
from tkinter import DISABLED, LEFT, RIGHT, ttk, X
from tkinter import filedialog
from PIL import Image, ImageTk
import icoextract

from .setting_tk import Setting


@dataclass
class File:
    id: int
    name: str
    path: str
    is_dir: bool
    tags: list[str]
    ctime: datetime
    icon: str
    description: str

    def absolute_path(self, setting: Setting):
        path = Path(self.path)
        if path.is_absolute():
            return path
        return setting.root_path.joinpath(path)


class Window:
    def __init__(self, setting: Setting, file: File) -> None:
        self.init_ui()

        self.setting = setting
        self.origin_file = file
        self.id_var.set(file.id)
        self.name_var.set(file.name)
        self.time_var.set(file.ctime.strftime("%Y-%m-%d %H:%M:%S"))
        self.tag_var.set(" ".join([f'#{t}' for t in file.tags]))
        if file.icon:
            self.icon = base64.b64decode(file.icon)
            self.image.config(data=base64.b64decode(file.icon))

    def init_ui(self):
        win = tk.Toplevel()
        for i, key in enumerate(
                ["id", "名称", "路径", "时间", "标签", "图标", "描述"]):
            ttk.Label(win, text=key).grid(row=i, column=0, pady=5)
        self.id_var = tk.IntVar(win)
        id_entry = ttk.Entry(win, state=DISABLED, textvariable=self.id_var)
        self.name_var = tk.StringVar(win)
        name_entry = ttk.Entry(win, textvariable=self.name_var)
        path_button = ttk.Button(win, text="打开路径")
        self.time_var = tk.StringVar(win)
        time_entry = ttk.Entry(win, state=DISABLED, textvariable=self.time_var)
        self.tag_var = tk.StringVar(win)
        tag_entry = ttk.Entry(win, textvariable=self.tag_var)
        icon_frame = ttk.Frame(win)
        self.image = tk.PhotoImage()
        ttk.Label(icon_frame, image=self.image).pack(side=LEFT)
        ttk.Button(icon_frame, text="选择图片",
                   command=self.choose_image).pack(side=RIGHT)
        ttk.Button(icon_frame, text="选择图标",
                   command=self.choose_icon).pack(side=RIGHT)
        for i, widget in enumerate(
                [id_entry, name_entry, path_button, time_entry, tag_entry, icon_frame]):
            widget.grid(row=i, column=1, sticky="nswe")
        self.desc_var = tk.StringVar(win)
        ttk.Entry(win, textvariable=self.desc_var).grid(
            row=6, column=1, pady=5, sticky="nswe")
        button_frame = ttk.Frame(win)
        button_frame.grid(row=7, column=0, columnspan=2, sticky="nswe")
        self.confirm_button = ttk.Button(button_frame, text="确认")
        self.confirm_button.pack(side=RIGHT)
        self.cancel_button = ttk.Button(button_frame, text="取消")
        self.cancel_button.pack(side=RIGHT)

        win.grid_columnconfigure(1, weight=1)
        win.grid_rowconfigure(6, weight=1)

    def choose_image(self):
        path = filedialog.askopenfilename(title="选择一个图片", initialdir=str(
            self.origin_file.absolute_path(self.setting).parent))
        if not path:
            return
        image = Image.open(path)
        w = image.width
        h = image.height
        if w > h:
            w, h = 20, h // w * 20
        else:
            w, h = w // h * 20, 20
        image = image.resize((w, h))
        buf = io.BytesIO()
        image.save(buf, 'PNG')
        if not buf.closed:
            buf.close()
        self.icon = buf.getvalue()
        self.image.configure(data=self.icon)

    def choose_icon(self):
        path = filedialog.askopenfilename(title="选择一个文件", initialdir=str(
            self.origin_file.absolute_path(self.setting).parent))
        if not path:
            return
        # icoextract.IconExtractor(path).get_icon()
        # https://stackoverflow.com/questions/524137/get-icons-for-common-file-types
