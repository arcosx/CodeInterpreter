from abc import ABC, abstractmethod
from typing import List

from codeinterpreter.sandbox.sandbox import Sandbox
from codeinterpreter.sandbox.schema import SandboxResponse


class SandboxManager(ABC):
    @abstractmethod
    def init(self):
        ...

    @abstractmethod
    async def ainit(self):
        ...

    @abstractmethod
    def list(self) -> SandboxResponse:
        ...

    @abstractmethod
    async def alist(self) -> List[SandboxResponse]:
        ...

    @abstractmethod
    def start(self) -> Sandbox:
        ...

    @abstractmethod
    async def astart(self) -> Sandbox:
        ...

    @abstractmethod
    def get(self, id: str) -> Sandbox:
        ...

    @abstractmethod
    async def aget(self, id: str) -> Sandbox:
        ...

    @abstractmethod
    def restart(self, id: str) -> SandboxResponse:
        ...

    @abstractmethod
    async def arestart(self, id: str) -> SandboxResponse:
        ...

    @abstractmethod
    def delete(self, id: str):
        ...

    @abstractmethod
    async def adelete(self, id: str):
        ...

    @abstractmethod
    def stop(self):
        ...

    @abstractmethod
    async def astop(self):
        ...
