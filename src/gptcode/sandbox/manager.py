from abc import ABC, abstractmethod
from typing import Optional
from gptcode.sandbox.schema import SandboxStatus, SandboxOutput, SandboxFile
import os
from gptcode.sandbox.sandbox import Sandbox


class Manager(ABC):
    @abstractmethod
    def list(self) -> Sandbox:
        ...

    @abstractmethod
    async def astlistart(self) -> Sandbox:
        ...

    @abstractmethod
    def start(self, id: str | None) -> Sandbox:
        ...

    @abstractmethod
    async def astart(self, id: str | None) -> Sandbox:
        ...

    @abstractmethod
    def get(self, id: str | None) -> Sandbox:
        ...

    @abstractmethod
    async def get(self, id: str | None) -> Sandbox:
        ...

    @abstractmethod
    def status(self, id: str) -> SandboxStatus:
        ...

    @abstractmethod
    async def astatus(self, id: str) -> SandboxStatus:
        ...

    @abstractmethod
    def restart(self, id: str) -> SandboxStatus:
        ...

    @abstractmethod
    async def arestart(self, id: str) -> SandboxStatus:
        ...

    @abstractmethod
    def stop(self, id: str) -> SandboxStatus:
        ...

    @abstractmethod
    async def astop(self, id: str) -> SandboxStatus:
        ...

    @abstractmethod
    def delete(self, id: str):
        ...

    @abstractmethod
    async def adelete(self, id: str):
        ...
