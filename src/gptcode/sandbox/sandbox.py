from abc import ABC, abstractmethod
from typing import Optional
from gptcode.sandbox.schema import SandboxStatus, SandboxOutput, SandboxFile
import os


class Sandbox(ABC):
    id: str

    @abstractmethod
    def run(
        self, code: str | None, file_path: Optional[os.PathLike] | None
    ) -> SandboxOutput:
        ...

    @abstractmethod
    async def arun(
        self, code: str | None, file_path: Optional[os.PathLike] | None
    ) -> SandboxOutput:
        ...

    @abstractmethod
    def upload(self, file_name: str, content: bytes) -> SandboxStatus:
        ...

    @abstractmethod
    async def aupload(self, file_name: str, content: bytes) -> SandboxStatus:
        ...

    @abstractmethod
    def download(self, file_name: str) -> SandboxFile:
        ...

    @abstractmethod
    async def adownload(self, file_name: str) -> SandboxFile:
        ...
