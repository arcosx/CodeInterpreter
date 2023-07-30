import os
from typing import Optional, Union
from gptcode.sandbox.sandbox import Sandbox
from websockets.sync.client import connect as ws_sync_connect, ClientConnection
from websockets.client import connect as ws_connect, WebSocketClientProtocol

from gptcode.sandbox.schema import SandboxFile, SandboxOutput, SandboxStatus


class LocalJupyterSandbox(Sandbox):
    def __init__(
        self,
        id: str = None,
        ws: Union[ClientConnection, WebSocketClientProtocol, None] = None,
    ) -> None:
        super().__init__()
        self.id = id
        self.ws = ws

    def run(
        self, code: str | None, file_path: Optional[os.PathLike] | None
    ) -> SandboxOutput:
        ...

    async def arun(
        self, code: str | None, file_path: Optional[os.PathLike] | None
    ) -> SandboxOutput:
        ...

    def upload(self, file_name: str, content: bytes) -> SandboxStatus:
        ...

    async def aupload(self, file_name: str, content: bytes) -> SandboxStatus:
        ...

    def download(self, file_name: str) -> SandboxFile:
        ...

    async def adownload(self, file_name: str) -> SandboxFile:
        ...
