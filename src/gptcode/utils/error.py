class GPTCodeError(Exception):
    """GPTCode base error"""


class PipInstallError(GPTCodeError):
    """Raise when failed to install package."""

    def __init__(self, package):
        super().__init__(f"Ran into error installing {package}.")


def wrap_error(e: Exception) -> Exception:
    """Add a type to exception `e` while ensuring that the original type is not changed"""

    e.__class__ = type(e.__class__.__name__, (GPTCodeError, e.__class__), {})
    return e
