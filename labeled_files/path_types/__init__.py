from typing import Dict
from .base import HandlerDescriptor, path_handler_types, File
from ..setting import Setting


def init_handlers(setting: Setting):
    File.handler = HandlerDescriptor(setting)
    from . import file

    if file.Handler.init_var():
        path_handler_types["file"] = path_handler_types["folder"] = file.Handler

    from . import vscode
    if vscode.Handler.init_var():
        path_handler_types["vscode"] = vscode.Handler