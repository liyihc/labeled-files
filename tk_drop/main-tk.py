# from ctypes import windll
# windll.shcore.SetProcessDpiAwareness(1)


if __name__ == "__main__":
    import tkinter as tk
    from labeled_files.main_ui_tk import App
    root = tk.Tk()
    App(root).search()
    root.mainloop()
