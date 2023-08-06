from codeinterpreter.sandbox.local_jupyter.manager import LocalJupyterManager
from codeinterpreter.sandbox.manager import SandboxManager


def get_sandbox_manager() -> SandboxManager:
    return LocalJupyterManager()
