class CodeInterpreterError(Exception):
    """CodeInterpreter base error"""


class PipInstallError(CodeInterpreterError):
    """Raise when failed to install package."""

    def __init__(self, package: str):
        super().__init__(f"Run into error installing {package}.")


class SandboxRunMaxRetryError(CodeInterpreterError):
    def __init__(self):
        super().__init__("Sandbox run has reached the maximum number of attempts.")


class PythonPackageNotFoundError(CodeInterpreterError):
    def __init__(self, package: str, hint: str):
        super().__init__(f"Python package {package} not found.{hint}")


def wrap_error(e: Exception) -> Exception:
    """Add a type to exception `e` while ensuring that the original type is not changed"""

    e.__class__ = type(e.__class__.__name__, (CodeInterpreterError, e.__class__), {})
    return e
