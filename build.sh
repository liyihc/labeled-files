pyinstaller main.spec --upx-dir C:/install/upx-3.96-win64 -y
python -m zipfile -c dist/labeled-files.zip dist/labeled-files