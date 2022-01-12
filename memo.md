可能是迫于C++的垃圾生态，QT自带文件管理2333，相当于python的pathlib模块

```python3
fileInfo = QtCore.QFileInfo(path)
iconProvider = QtGui.QFileIconProvider()
icon = iconProvider.icon(fileInfo)
```