from typing import Optional
from codeinterpreter.sandbox.manager import SandboxManager
from codeinterpreter.sandbox.factory import get_sandbox_manager


class CodeInterpreter:
    def __init__(self) -> None:
        self.sandbox_manager: Optional[SandboxManager] = None

    def init(self, sandbox_manager: SandboxManager = get_sandbox_manager()):
        self.sandbox_manager = sandbox_manager
        self.sandbox_manager.init()

    async def ainit(self, sandbox_manager: SandboxManager = get_sandbox_manager()):
        self.sandbox_manager = sandbox_manager
        await self.sandbox_manager.ainit()
