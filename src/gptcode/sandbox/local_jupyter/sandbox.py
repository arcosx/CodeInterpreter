import os
from typing import Optional, Union
from gptcode.sandbox.sandbox import Sandbox
from websockets.sync.client import connect as ws_sync_connect, ClientConnection
from websockets.client import connect as ws_connect, WebSocketClientProtocol
from gptcode.utils.log import gptcode_log
from gptcode.sandbox.schema import SandboxFile, SandboxOutput, SandboxStatus
from uuid import uuid4
import json


class LocalJupyterSandbox(Sandbox):
    def __init__(
        self,
        id: str = None,
        ws_url: str = None,
        ws: Union[ClientConnection, WebSocketClientProtocol, None] = None,
    ) -> None:
        super().__init__()
        self.id = id
        self.ws_url = ws_url
        self.ws = ws

    def run(self, code: Union[str, os.PathLike]) -> SandboxOutput:
        if not code:
            raise ValueError("Code or Code file path must be specified one.")
        if type(code) is os.PathLike:
            with open(code, "r") as f:
                code = f.read()
        gptcode_log.debug(f"Running code:{code}")
        self.ws.send(
            json.dumps(
                {
                    "header": {
                        "msg_id": (msg_id := uuid4().hex),
                        "msg_type": "execute_request",
                    },
                    "parent_header": {},
                    "metadata": {},
                    "content": {
                        "code": code,
                        "silent": False,
                        "store_history": True,
                        "user_expressions": {},
                        "allow_stdin": False,
                        "stop_on_error": True,
                    },
                    "channel": "shell",
                    "buffers": [],
                }
            )
        )
        result = ""

    async def arun(self, code: Union[str, os.PathLike]) -> SandboxOutput:
        ...

    def upload(self, file_name: str, content: bytes) -> SandboxStatus:
        ...

    async def aupload(self, file_name: str, content: bytes) -> SandboxStatus:
        ...

    def download(self, file_name: str) -> SandboxFile:
        ...

    async def adownload(self, file_name: str) -> SandboxFile:
        ...
