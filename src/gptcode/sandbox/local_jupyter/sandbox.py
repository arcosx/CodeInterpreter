import asyncio
import json
import os
from typing import Union
from uuid import uuid4

from websockets.client import WebSocketClientProtocol
from websockets.client import connect as ws_connect
from websockets.exceptions import ConnectionClosedError
from websockets.sync.client import ClientConnection
from websockets.sync.client import connect as ws_sync_connect

from gptcode.sandbox.sandbox import Sandbox
from gptcode.sandbox.schema import (SandboxFile, SandboxOutput,
                                    SandboxRunConfig, SandboxStatus)
from gptcode.utils.error import SandboxRunMaxRetryError
from gptcode.utils.log import gptcode_log


class LocalJupyterSandbox(Sandbox):
    def __init__(
        self,
        id: str = None,
        ws_url: str = None,
        ws: Union[ClientConnection, WebSocketClientProtocol, None] = None,
        workdir: str = None,
    ) -> None:
        super().__init__()
        self.id = id
        self.ws_url = ws_url
        self.ws = ws
        self.workdir = workdir

    @classmethod
    def sync_init(cls, id: str = None, ws_url: str = None, workdir: str = None):
        ws = ws_sync_connect(ws_url)

        return cls(id=id, ws_url=ws_url, ws=ws, workdir=workdir)

    @classmethod
    async def async_init(cls, id: str = None, ws_url: str = None, workdir: str = None):
        ws = await ws_connect(ws_url)
        return cls(id=id, ws_url=ws_url, ws=ws, workdir=workdir)

    def run(
        self, code: Union[str, os.PathLike], config: SandboxRunConfig
    ) -> SandboxOutput:
        if not code:
            raise ValueError("Code or Code file path must be specified one.")
        if type(code) is os.PathLike:
            with open(code, "r") as f:
                code = f.read()
        if config.retry <= 0:
            raise SandboxRunMaxRetryError()
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
        while True:
            try:
                received_msg = json.loads(self.ws.recv())
            except ConnectionClosedError:
                gptcode_log.warning("reconnect websocket...")
                self.ws = ws_sync_connect(self.ws_url)
                config.retry = config.retry - 1
                return self.run(code=code, config=config)
            if (
                received_msg["header"]["msg_type"] == "stream"
                and received_msg["parent_header"]["msg_id"] == msg_id
            ):
                msg = received_msg["content"]["text"].strip()
                gptcode_log.debug("Received [stream] %s" % msg)
                result += msg
            elif (
                received_msg["header"]["msg_type"] == "execute_result"
                and received_msg["parent_header"]["msg_id"] == msg_id
            ):
                msg = received_msg["content"]["data"]["text/plain"].strip()
                gptcode_log.debug("Received [execute_result] output %s" % msg)
                result += msg
            elif received_msg["header"]["msg_type"] == "display_data":
                if "image/png" in received_msg["content"]["data"]:
                    gptcode_log.debug("Received [display_data] image/png output")
                    return SandboxOutput(
                        type="image/png",
                        content=received_msg["content"]["data"]["image/png"],
                    )

                elif "text/plain" in received_msg["content"]["data"]:
                    gptcode_log.debug("Received [display_data] text/plain output")
                    return SandboxOutput(
                        type="text",
                        content=received_msg["content"]["data"]["text/plain"],
                    )
            elif (
                received_msg["header"]["msg_type"] == "status"
                and received_msg["parent_header"]["msg_id"] == msg_id
                and received_msg["content"]["execution_state"] == "idle"
            ):
                gptcode_log.debug(
                    "Received [status] idle, return the result %s" % result
                )
                return SandboxOutput(
                    type="text", content=result or "code run successfully (no output)"
                )

            elif (
                received_msg["header"]["msg_type"] == "error"
                and received_msg["parent_header"]["msg_id"] == msg_id
            ):
                error = f"{received_msg['content']['ename']}: {received_msg['content']['evalue']}"
                gptcode_log.debug("Received [error], return the error %s" % error)
                return SandboxOutput(type="error", content=error)

    async def arun(
        self, code: Union[str, os.PathLike], config: SandboxRunConfig
    ) -> SandboxOutput:
        if not code:
            raise ValueError("Code or Code file path must be specified one.")
        if type(code) is os.PathLike:
            with open(code, "r") as f:
                code = await f.read()
        if config.retry <= 0:
            raise SandboxRunMaxRetryError()
        gptcode_log.debug(f"Running code:{code}")
        await self.ws.send(
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
        while True:
            try:
                received_msg = json.loads(await self.ws.recv())
            except ConnectionClosedError:
                gptcode_log.warning("reconnect websocket...")
                self.ws = await ws_connect(self.ws_url)
                config.retry = config.retry - 1
                return await self.arun(code=code, config=config)
            if (
                received_msg["header"]["msg_type"] == "stream"
                and received_msg["parent_header"]["msg_id"] == msg_id
            ):
                msg = received_msg["content"]["text"].strip()
                gptcode_log.debug("Received [stream] %s", msg)
                result += msg
            elif (
                received_msg["header"]["msg_type"] == "execute_result"
                and received_msg["parent_header"]["msg_id"] == msg_id
            ):
                msg = received_msg["content"]["data"]["text/plain"].strip()
                gptcode_log.debug("Received [execute_result] output %s", msg)
                result += msg
            elif received_msg["header"]["msg_type"] == "display_data":
                if "image/png" in received_msg["content"]["data"]:
                    gptcode_log.debug("Received [display_data] image/png output")
                    return SandboxOutput(
                        type="image/png",
                        content=received_msg["content"]["data"]["image/png"],
                    )

                elif "text/plain" in received_msg["content"]["data"]:
                    gptcode_log.debug("Received [display_data] text/plain output")
                    return SandboxOutput(
                        type="text",
                        content=received_msg["content"]["data"]["text/plain"],
                    )
            elif (
                received_msg["header"]["msg_type"] == "status"
                and received_msg["parent_header"]["msg_id"] == msg_id
                and received_msg["content"]["execution_state"] == "idle"
            ):
                gptcode_log.debug(
                    "Received [status] idle, return the result %s", result
                )
                return SandboxOutput(
                    type="text", content=result or "code run successfully (no output)"
                )

            elif (
                received_msg["header"]["msg_type"] == "error"
                and received_msg["parent_header"]["msg_id"] == msg_id
            ):
                error = f"{received_msg['content']['ename']}: {received_msg['content']['evalue']}"
                gptcode_log.debug("Received [error], return the error %s", error)
                return SandboxOutput(type="error", content=error)

    def upload(self, file_name: str, content: bytes) -> SandboxStatus:
        os.makedirs(self.workdir, exist_ok=True)
        with open(os.path.join(self.workdir, file_name), "wb") as file:
            file.write(content)

        return SandboxStatus(status=f"{file_name} uploaded successfully")

    async def aupload(self, file_name: str, content: bytes) -> SandboxStatus:
        return await asyncio.to_thread(self.upload, file_name, content)

    def download(self, file_name: str) -> SandboxFile:
        with open(os.path.join(self.workdir, file_name), "rb") as file:
            content = file.read()

        return SandboxFile(name=file_name, content=content)

    async def adownload(self, file_name: str) -> SandboxFile:
        return await asyncio.to_thread(self.download, file_name)
