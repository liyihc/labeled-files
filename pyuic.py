import os
import pathlib

if __name__ == "__main__":
    root = pathlib.Path(__file__).parent
    for file in root.joinpath("labeled_files").glob("*.ui"):
        target_file = file.parent.joinpath(file.stem + "Ui.py")
        if not target_file.exists() or file.stat().st_mtime > target_file.stat().st_mtime:
            os.system(
                f"pyside6-uic {file.relative_to(root)} -o {target_file.relative_to(root)}")
