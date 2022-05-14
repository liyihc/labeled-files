
from datetime import datetime
from functools import partial
import os
import pathlib
import sqlite3
import subprocess
from tkinter import HORIZONTAL, ttk, LEFT, RIGHT, TOP, BOTTOM, X, Y, BOTH
import tkinter as tk
from tkinter import messagebox, filedialog

from .setting_tk import Config, Setting, VERSION, logv
from .tree_tk import build_tree
from .file_ui_tk import File, Window as FileWin


class App:
    def __init__(self, master: tk.Tk):
        self.init_ui_structure(master)
        self.init_ui_content()

        self.setting = Setting()
        config_path = pathlib.Path("config.json")
        if config_path.exists():
            self.config = Config.parse_file(config_path)
        else:
            self.config = Config()
        for key, path in self.config.workspaces.items():
            self.file_menu.add_command(
                label=f"选择工作区：{key}", command=partial(self.change_workspace, path))

        self.tree_view.bind("<Double-Button-1>", self.doubleclick_tag)
        self.clear_button.config(command=self.clear_tag)
        self.search_button.config(command=self.search)
        self.file_table.bind("<Delete>", self.del_file)
        self.file_table.bind("<Double-Button-1>", self.doubleclick_file)
        self.file_table.bind("<Button-3>", self.show_context_menu)

        default = self.config.workspaces.get(self.config.default, None)
        if default:
            self.setting.set_root(default)
            # TODO toggle options
            self.tag_combobox["values"] = self.setting.tags

        self.files: list[File] = []

    def init_ui_structure(self, master: tk.Tk):
        # menu
        menubar = tk.Menu(master, tearoff=0)
        master.config(menu=menubar)
        file_menu = self.file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="打开工作区", command=self.open_workspace)
        file_menu.add_separator()
        menubar.add_cascade(label="文件", menu=file_menu)

        # search box
        frame = ttk.Frame(master)
        ttk.Label(frame, text="关键字").pack(side=tk.LEFT, padx=5)
        self.keyword_entry = ttk.Entry(frame)
        self.keyword_entry.pack(side=tk.LEFT, fill=tk.X, expand=1, padx=5)
        ttk.Label(frame, text="标签").pack(side=tk.LEFT, padx=5)
        self.tag_combobox = ttk.Combobox(frame)
        self.tag_combobox.pack(side=tk.LEFT, fill=tk.X, expand=1, padx=5)
        self.clear_button = ttk.Button(frame, text="清除标签")
        self.clear_button.pack(side=LEFT)
        self.search_button = ttk.Button(frame, text="搜索")
        self.search_button.pack(side=tk.LEFT)
        frame.pack(fill=tk.X)

        # tag view
        frame = ttk.Frame(master)
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(side=LEFT, fill=BOTH)
        scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
        scroll_x.pack(side=tk.BOTTOM, fill=X)
        scroll_y = ttk.Scrollbar(tree_frame)
        scroll_y.pack(side=tk.RIGHT, fill=Y)
        self.tree_view = ttk.Treeview(
            tree_frame, xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        scroll_x.config(command=self.tree_view.xview)
        scroll_y.config(command=self.tree_view.yview)
        self.tree_view.pack(side=LEFT, fill=BOTH)

        # file table
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(side=LEFT, fill=BOTH, expand=1)
        scroll_x = ttk.Scrollbar(tree_frame, orient=HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=X)
        scroll_y = ttk.Scrollbar(tree_frame)
        scroll_y.pack(side=tk.RIGHT, fill=Y)
        self.file_table = ttk.Treeview(
            tree_frame, xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        scroll_x.config(command=self.file_table.xview)
        scroll_y.config(command=self.file_table.yview)
        self.file_table.pack(side=LEFT, fill=BOTH, expand=1)
        frame.pack(fill=BOTH, expand=1)

        self.file_table_context_menu = tk.Menu(tree_frame, tearoff=0)
        self.file_table_context_menu.add_command(
            label="打开", command=self.open_file)
        self.file_table_context_menu.add_command(
            label="编辑", command=self.edit_file)
        self.file_table_context_menu.add_command(
            label="打开路径", command=self.open_path)

    def init_ui_content(self):
        tree_view = self.tree_view
        tree_view['columns'] = ("count",)
        tree_view.heading("#0", text="标签")
        tree_view.heading("count", text="计数")

        file_table = self.file_table
        heading = {
            "file": "文件",
            "time": "时间",
            "tag": "标签",
            "desc": "描述"
        }
        file_table['columns'] = tuple(heading.keys())
        file_table.column("#0", width=0, stretch=0)
        for key, value in heading.items():
            file_table.column(key, stretch=0)
            file_table.heading(key, text=value)
        file_table.column("desc", stretch=1)

    def open_workspace(self):
        pass

    def change_workspace(self, path: pathlib.Path):
        print(path)

    def clear_tag(self):
        self.tag_combobox.set("")
        self.search()

    def search(self):
        if not self.setting.root_path:
            return
        keyword = self.keyword_entry.get().strip()
        tag = self.complete()
        logv("SEARCH", f"keyword {keyword} tag {tag}")

        self.search_tag(keyword, tag)
        self.search_file(keyword, tag)

    def search_tag(self, keyword, tag):
        conn = self.setting.conn

        match keyword, tag:
            case "", "":
                where = ""
            case keyword, "":
                where = f"WHERE label LIKE '%{keyword}%'"
            case "", tag:
                where = f"WHERE label LIKE '{tag}/%'"
            case keyword, tag:
                where = f"WHERE label LIKE '%{keyword}%' AND label LIKE '{tag}/%'"
        sql = f"SELECT label, COUNT(*) FROM file_labels {where} GROUP BY label ORDER BY label"

        tags = conn.execute(sql).fetchall()
        build_tree(self.tree_view, tags)

    def search_file(self, keyword, tag):
        conn = self.setting.conn
        match keyword, tag:
            case "", "":
                file_ids = [f for f, in conn.execute(
                    "SELECT id FROM files ORDER BY vtime DESC LIMIT 50")]
            case "", tag:
                file_ids = {v for v, in conn.execute(
                    f"SELECT file_id FROM file_labels WHERE label = '{tag}' OR label LIKE '{tag}/%'")}
            case keyword, "":
                file_ids = [f for f, in conn.execute(
                    f'SELECT id FROM files WHERE name like "%{keyword}%" ORDER BY vtime DESC')]
            case keyword, tag:
                file_ids = {v for v, in conn.execute(
                    f"SELECT file_id FROM file_labels WHERE label = '{tag}' OR label LIKE '{tag}/%'")}
                if file_ids:
                    file_ids = ','.join(str(f) for f in file_ids)
                    file_ids = [f for f, in conn.execute(
                        f'SELECT id FROM files WHERE name like "%{keyword}%" AND id in ({file_ids}) ORDER BY vtime DESC')]
        if file_ids:
            file_ids = ','.join(str(f) for f in file_ids)
            files: list[File] = [get_file(conn, record) for record in conn.execute(
                f"SELECT id, name, path, is_dir, ctime, vtime, icon, description FROM files WHERE id in ({file_ids}) ORDER BY vtime DESC")]
        else:
            files = []
        self.show_files(files)

    def show_files(self, results: list[File] = None):
        self.file_table.delete(*self.file_table.get_children())
        if results is None:
            results = self.files
        else:
            self.files = results
        for ind, f in enumerate(results):
            self.file_table.insert(
                "",
                'end',
                values=(
                    f.name, f.ctime.strftime("%y%m%d %H:%M:%S"),
                    ' '.join(f'#{tag}' for tag in f.tags),
                    f.description
                ),
                tags=str(ind))

    def complete(self):
        current = self.tag_combobox.get()
        for tag in self.setting.tags:
            if tag.startswith(current):
                self.tag_combobox.set(tag)
                return tag

    def doubleclick_tag(self, event: tk.Event):
        items = self.tree_view.selection()
        if items:
            self.tag_combobox.set(items[0])
            self.search()

    def doubleclick_file(self, event: tk.Event):
        tags = self.file_table.item(
            self.file_table.identify_row(event.y), 'tags')
        if tags:
            self.current_context_file = int(tags[0])
            self.open_file()

    def show_context_menu(self, event: tk.Event):
        tags = self.file_table.item(
            self.file_table.identify_row(event.y), 'tags')
        if tags:
            self.current_context_file = int(tags[0])
            try:
                self.file_table_context_menu.tk_popup(
                    event.x_root, event.y_root)
            except:
                self.file_table_context_menu.grab_release()

    def get_context_file(self):
        f = self.files[self.current_context_file]
        with self.setting.conn:
            self.setting.conn.execute(
                "UPDATE files SET vtime = ? WHERE id = ?", (str(datetime.now()), f.id))
        return f

    def open_file(self):
        p = self.get_context_file().absolute_path(self.setting)
        if p.exists():
            cwd = os.getcwd()
            os.chdir(p.parent)
            os.startfile(p)
            os.chdir(cwd)
        else:
            messagebox.showinfo("文件不存在", str(p))

    def edit_file(self):
        win = FileWin(self.setting, self.get_context_file())

    def open_path(self):
        p = self.get_context_file().absolute_path(self.setting)
        subprocess.Popen(
            f'explorer /select,{p}')

    def reshow(self, file_id: int):
        conn = self.setting.conn
        f = get_file(conn, conn.execute(
            "SELECT id, name, path, is_dir, ctime, vtime, icon, description FROM files WHERE id = ? LIMIT 1", (
                f)
        ))

    def del_file(self, event: tk.Event):
        # items = self.tree_view.selection()
        pass


def get_file(conn: sqlite3.Connection, args):
    id, name, path, is_dir, ctime, vtime, icon, description = args
    tags = [tag for tag, in conn.execute(
        "SELECT label FROM file_labels WHERE file_id = ?", (id,))]
    return File(id, name, str(path), is_dir, tags, datetime.fromisoformat(ctime), icon, description)
