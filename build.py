from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
from shutil import copy
import shutil
import subprocess
import zipfile
from labeled_files.setting import VERSION


@dataclass
class Config:
    build: bool = True
    zip_file: bool = True
    copy_to_target: bool = True

    upx_dir: str = ""
    target_dir: str = ""


CONFIG_PATH = Path('build-config.json')
if CONFIG_PATH.exists():
    config = Config(**json.loads(CONFIG_PATH.read_text()))
else:
    config = Config()

CONFIG_PATH.write_text(json.dumps(asdict(config), indent=4))

if config.build:
    if not config.upx_dir:
        print("please provide upx path")
        exit()
    os.system(f'pyinstaller main.spec --upx-dir {config.upx_dir} -y')


DIST_DIR = Path("dist")
EXE_DIR = DIST_DIR / "labeled-files"

ZIP_PATH = DIST_DIR / f"labeled-files-{VERSION.replace('.','_')}.zip"
if config.zip_file:
    with zipfile.ZipFile(ZIP_PATH, 'w') as file:
        for path in EXE_DIR.glob("**/*"):
            print("write to zip file:", path)
            file.write(path, path.relative_to(EXE_DIR), zipfile.ZIP_DEFLATED)

    subprocess.Popen(
        f'explorer /select,"{ZIP_PATH.absolute()}"')

if config.copy_to_target:
    target_dir = Path(config.target_dir)
    if target_dir.exists():
        target_config_path = target_dir / "config.json"
        target_config = target_config_path.read_text()
        print(target_config)
        shutil.rmtree(target_dir)
    else:
        target_config = ""
    print(EXE_DIR, target_dir)
    shutil.copytree(EXE_DIR, target_dir)
    if target_config:
        target_config_path.write_text(target_config)
    os.startfile(target_dir)
