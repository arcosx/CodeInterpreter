class CodeError(Exception):
    """GPTCode base error"""

class PipInstallError(CodeError):
    """Raise when failed to install package."""
    def __init__(self, package):
        super().__init__(f"Ran into error installing {package}.")
