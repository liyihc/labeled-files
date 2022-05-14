import sys


def main():
    from PySide6 import QtWidgets
    from labeled_files.mainUiPy import Window, Config
    from pathlib import Path
    with open(Path(__file__).parent.joinpath('rename-to-config.json'), 'w') as f:
        f.write(Config(
            default="dir1",
            workspaces={
                "dir1": "C:/",
                "dir2": "C:/"
            }
        ).json(indent=4))
    app = QtWidgets.QApplication([])
    win = Window()
    win.show()
    win.search()
    return app


if __name__ == "__main__":
    app = main()
    sys.exit(app.exec())
