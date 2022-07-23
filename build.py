import json
import os
import shutil
import subprocess
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path

from git import Repo
import pytest

from labeled_files.setting import VERSION


@dataclass
class Config:
    test: bool = True
    build: bool = True
    zip_file: bool = True
    release: bool = True
    copy_to_target: bool = True

    upx_dir: str = ""
    target_dir: str = ""


CONFIG_PATH = Path('build-config.json')
DIST_DIR = Path("dist")
EXE_DIR = DIST_DIR / "labeled-files"
ZIP_PATH = DIST_DIR / f"labeled-files-{VERSION.replace('.','_')}.zip"


def read_config():
    exists = CONFIG_PATH.exists()
    if exists:
        config = Config(**json.loads(CONFIG_PATH.read_text()))
    else:
        config = Config()
    CONFIG_PATH.write_text(json.dumps(asdict(config), indent=4))
    return exists, config


def run_test(config: Config):
    ret = pytest.main()
    if ret != 0:
        print("Test failed with code", ret)
    return False


def run_build(config: Config):
    if not config.upx_dir:
        print("please provide upx path")
        return False
    os.system(f'pyinstaller main.spec --upx-dir {config.upx_dir} -y')
    return True


def run_package(config: Config):
    with zipfile.ZipFile(ZIP_PATH, 'w') as file:
        for path in EXE_DIR.glob("**/*"):
            print("write to zip file:", path)
            file.write(path, path.relative_to(EXE_DIR), zipfile.ZIP_DEFLATED)

    subprocess.Popen(
        f'explorer /select,"{ZIP_PATH.absolute()}"')


def run_release(config: Config, repo: Repo):
    """
    https://docs.github.com/en/rest/releases/releases#create-a-release
    这个没讲清楚啊……
    https://docs.github.com/en/rest/releases/assets#upload-a-release-asset
    curl \
        -X POST \
        -H "Accept: application/vnd.github+json" \ 
        -H "Authorization: token <TOKEN>" \
        https://api.github.com/repos/OWNER/REPO/releases \
        -d '{"tag_name":"v1.0.0","target_commitish":"master","name":"v1.0.0","body":"Description of the release","draft":false,"prerelease":false,"generate_release_notes":false}'
    """
    pass


def run_copy(config: Config):
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


if __name__ == "__main__":
    repo = Repo(".")
    assert not repo.bare
    assert repo.active_branch.name == "master"

    exists, config = read_config()
    if not exists:
        print("build-config.json was created, please check it\n rand rerun this script to continue")
        exit()
    if config.test:
        if not run_test(config):
            exit(-1)
    if config.build:
        if not run_build(config):
            exit(-1)
    if config.zip_file:
        run_package(config)
    if config.release:
        run_release(config, repo)
    if config.copy_to_target:
        run_copy(config)
