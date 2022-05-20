from typing import Dict
from .base import HandlerDescriptor, path_handler_factories, File
from ..setting import Setting


def init_handlers(setting: Setting):
    File.handler = HandlerDescriptor(setting)
    from . import file

    file.Handler.init_var()
    path_handler_factories["file"] = path_handler_factories["folder"] = file.Handler
