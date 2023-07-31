class GPTCodeError(Exception):
    """GPTCode base error"""


class PipInstallError(GPTCodeError):
    """Raise when failed to install package."""

    def __init__(self, package: str):
        super().__init__(f"Run into error installing {package}.")


class SandboxRunMaxRetryError(GPTCodeError):
    def __init__(self):
        super().__init__(f"Sandbox run has reached the maximum number of attempts.")


class PythonPackageNotFoundError(GPTCodeError):
    def __init__(self, package: str, hint: str):
        super().__init__(f"Python package {package} not found.{hint}")


def wrap_error(e: Exception) -> Exception:
    """Add a type to exception `e` while ensuring that the original type is not changed"""

    e.__class__ = type(e.__class__.__name__, (GPTCodeError, e.__class__), {})
    return e
