from abc import ABC, abstractmethod
from typing import Optional, Union
from gptcode.sandbox.schema import (
    SandboxStatus,
    SandboxOutput,
    SandboxFile,
    SandboxRunConfig,
)
import os


class Sandbox(ABC):
    id: str

    @abstractmethod
    def run(
        self, code: Union[str, os.PathLike], config: SandboxRunConfig
    ) -> SandboxOutput:
        ...

    @abstractmethod
    async def arun(
        self, code: Union[str, os.PathLike], config: SandboxRunConfig
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
