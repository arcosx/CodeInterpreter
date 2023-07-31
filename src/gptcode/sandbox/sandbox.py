import os
from abc import ABC, abstractmethod
from typing import Union

from gptcode.sandbox.schema import (SandboxFile, SandboxOutput,
                                    SandboxRunConfig, SandboxStatus)


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
