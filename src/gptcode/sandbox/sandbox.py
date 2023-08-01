import os
from abc import ABC, abstractmethod
from typing import Union

from gptcode.sandbox.schema import (SandboxFile, SandboxRunOutput,
                                    SandboxResponse)


class Sandbox(ABC):
    id: str

    @abstractmethod
    def run(
        self, code: Union[str, os.PathLike]
    ) -> SandboxRunOutput:
        ...

    @abstractmethod
    async def arun(
        self, code: Union[str, os.PathLike]
    ) -> SandboxRunOutput:
        ...

    @abstractmethod
    def upload(self, file_name: str, content: bytes) -> SandboxResponse:
        ...

    @abstractmethod
    async def aupload(self, file_name: str, content: bytes) -> SandboxResponse:
        ...

    @abstractmethod
    def download(self, file_name: str) -> SandboxFile:
        ...

    @abstractmethod
    async def adownload(self, file_name: str) -> SandboxFile:
        ...
