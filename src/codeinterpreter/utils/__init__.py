__all__ = ["import_openai", "import_jupyter_kernel_gateway"]

import importlib.util
from typing import Optional

from codeinterpreter.utils.dependency import pip_install


def _check_library(libname: str, prompt: bool = True, package: Optional[str] = None):
    is_avail = False
    if importlib.util.find_spec(libname):
        is_avail = True
    if not is_avail and prompt:
        pip_install(package if package else libname)
    return is_avail


def import_openai():
    _check_library("openai")


def import_jupyter_kernel_gateway():
    _check_library("jupyter-kernel-gateway")
