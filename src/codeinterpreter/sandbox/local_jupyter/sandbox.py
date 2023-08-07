import asyncio
import json
import os
import time
from typing import Union
from uuid import uuid4

from websockets.client import WebSocketClientProtocol
from websockets.client import connect as ws_connect
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from websockets.sync.client import ClientConnection
from websockets.sync.client import connect as ws_sync_connect

from codeinterpreter.sandbox.sandbox import Sandbox
from codeinterpreter.sandbox.schema import (
    SandboxFile,
    SandboxResponse,
    SandboxRunOutput,
)
from codeinterpreter.utils.log import codeinterpreter_log

WEBSOCKETS_RECONNECT_MAX_RETRIES = 3
WEBSOCKETS_RECONNECT_RETRY_DELAY = 5


class LocalJupyterSandbox(Sandbox):
    def __init__(
        self,
        id: str = None,
        ws_url: str = None,
        ws: Union[ClientConnection, WebSocketClientProtocol, None] = None,
        workdir: str = None,
    ) -> None:
        super().__init__()
        self.type = "local_jupyter"
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

    def run(self, code: Union[str, os.PathLike]) -> SandboxRunOutput:
        if not code:
            raise ValueError("Code or Code file path must be specified one.")
        if type(code) is os.PathLike:
            with open(code, "r") as f:
                code = f.read()
        codeinterpreter_log.debug(f"Running code:{code}")
        retries = 0
        while retries < WEBSOCKETS_RECONNECT_MAX_RETRIES:
            try:
                msg_id = self.send_code_to_sandbox(code=code)
                return self.get_sandbox_output(msg_id)
            except ConnectionClosedError or ConnectionClosedOK:
                codeinterpreter_log.warning("reconnect websocket...")
                self.reconnect()
                time.sleep(WEBSOCKETS_RECONNECT_RETRY_DELAY)
                retries += 1
            except Exception as exception:
                codeinterpreter_log.error("websocket get exception")
                raise exception

        return SandboxRunOutput(
            type="error", content="Failed to execute code after multiple retries."
        )

    async def arun(self, code: Union[str, os.PathLike]) -> SandboxRunOutput:
        if not code:
            raise ValueError("Code or Code file path must be specified one.")
        if type(code) is os.PathLike:
            with open(code, "r") as f:
                code = await f.read()
        codeinterpreter_log.debug(f"Running code:{code}")
        retries = 0
        while retries < WEBSOCKETS_RECONNECT_MAX_RETRIES:
            try:
                msg_id = await self.asend_code_to_sandbox(code=code)
                return await self.aget_sandbox_output(msg_id)
            except ConnectionClosedError or ConnectionClosedOK:
                codeinterpreter_log.warning("reconnect websocket...")
                await self.areconnect()
                time.sleep(WEBSOCKETS_RECONNECT_RETRY_DELAY)
                retries += 1
            except Exception as exception:
                codeinterpreter_log.error("websocket get exception")
                raise exception

        return SandboxRunOutput(
            type="error", content="Failed to execute code after multiple retries."
        )

    def upload(self, file_name: str, content: bytes) -> SandboxResponse:
        os.makedirs(self.workdir, exist_ok=True)
        with open(os.path.join(self.workdir, file_name), "wb") as file:
            file.write(content)

        return SandboxResponse(content=f"{file_name} uploaded successfully")

    async def aupload(self, file_name: str, content: bytes) -> SandboxResponse:
        return await asyncio.get_running_loop().run_in_executor(
            None, self.upload, file_name, content
        )

    def download(self, file_name: str) -> SandboxFile:
        with open(os.path.join(self.workdir, file_name), "rb") as file:
            content = file.read()

        return SandboxFile(name=file_name, content=content)

    async def adownload(self, file_name: str) -> SandboxFile:
        return await asyncio.get_running_loop().run_in_executor(
            None, self.download, file_name
        )

    def close_websocket(self) -> None:
        self.ws.close()

    async def aclose_websocket(self) -> None:
        await self.ws.close()

    def reconnect(self) -> None:
        self.ws = ws_sync_connect(self.ws_url)

    async def areconnect(self) -> None:
        self.ws = await ws_connect(self.ws_url)

    def send_code_to_sandbox(self, code: str) -> str:
        msg_id = uuid4().hex

        self.ws.send(
            json.dumps(
                {
                    "header": {
                        "msg_id": msg_id,
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

        return msg_id

    async def asend_code_to_sandbox(self, code: str) -> str:
        msg_id = uuid4().hex

        await self.ws.send(
            json.dumps(
                {
                    "header": {
                        "msg_id": msg_id,
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

        return msg_id

    def get_sandbox_output(self, msg_id: str) -> SandboxRunOutput:
        result = ""

        while True:
            received_msg = json.loads(self.ws.recv())
            if (
                received_msg["header"]["msg_type"] == "stream"
                and received_msg["parent_header"]["msg_id"] == msg_id
            ):
                msg = received_msg["content"]["text"].strip()
                codeinterpreter_log.debug("Received [stream] %s" % msg)
                result += msg
            elif (
                received_msg["header"]["msg_type"] == "execute_result"
                and received_msg["parent_header"]["msg_id"] == msg_id
            ):
                msg = received_msg["content"]["data"]["text/plain"].strip()
                codeinterpreter_log.debug("Received [execute_result] output %s" % msg)
                result += msg
            elif received_msg["header"]["msg_type"] == "display_data":
                if "image/png" in received_msg["content"]["data"]:
                    codeinterpreter_log.debug(
                        "Received [display_data] image/png output"
                    )
                    return SandboxRunOutput(
                        type="image/png",
                        content=received_msg["content"]["data"]["image/png"],
                    )

                elif "text/plain" in received_msg["content"]["data"]:
                    codeinterpreter_log.debug(
                        "Received [display_data] text/plain output"
                    )
                    return SandboxRunOutput(
                        type="text",
                        content=received_msg["content"]["data"]["text/plain"],
                    )
            elif (
                received_msg["header"]["msg_type"] == "status"
                and received_msg["parent_header"]["msg_id"] == msg_id
                and received_msg["content"]["execution_state"] == "idle"
            ):
                codeinterpreter_log.debug(
                    "Received [status] idle, return the result %s" % result
                )
                return SandboxRunOutput(
                    type="text", content=result or "code run successfully (no output)"
                )

            elif (
                received_msg["header"]["msg_type"] == "error"
                and received_msg["parent_header"]["msg_id"] == msg_id
            ):
                error = f"{received_msg['content']['ename']}: {received_msg['content']['evalue']}"
                codeinterpreter_log.debug(
                    "Received [error], return the error %s" % error
                )
                return SandboxRunOutput(type="error", content=error)

    async def aget_sandbox_output(self, msg_id: str) -> SandboxRunOutput:
        result = ""

        while True:
            received_msg = json.loads(await self.ws.recv())

            if (
                received_msg["header"]["msg_type"] == "stream"
                and received_msg["parent_header"]["msg_id"] == msg_id
            ):
                msg = received_msg["content"]["text"].strip()
                codeinterpreter_log.debug("Received [stream] %s" % msg)
                result += msg
            elif (
                received_msg["header"]["msg_type"] == "execute_result"
                and received_msg["parent_header"]["msg_id"] == msg_id
            ):
                msg = received_msg["content"]["data"]["text/plain"].strip()
                codeinterpreter_log.debug("Received [execute_result] output %s" % msg)
                result += msg
            elif received_msg["header"]["msg_type"] == "display_data":
                if "image/png" in received_msg["content"]["data"]:
                    codeinterpreter_log.debug(
                        "Received [display_data] image/png output"
                    )
                    return SandboxRunOutput(
                        type="image/png",
                        content=received_msg["content"]["data"]["image/png"],
                    )

                elif "text/plain" in received_msg["content"]["data"]:
                    codeinterpreter_log.debug(
                        "Received [display_data] text/plain output"
                    )
                    return SandboxRunOutput(
                        type="text",
                        content=received_msg["content"]["data"]["text/plain"],
                    )
            elif (
                received_msg["header"]["msg_type"] == "status"
                and received_msg["parent_header"]["msg_id"] == msg_id
                and received_msg["content"]["execution_state"] == "idle"
            ):
                codeinterpreter_log.debug(
                    "Received [status] idle, return the result %s" % result
                )
                return SandboxRunOutput(
                    type="text", content=result or "code run successfully (no output)"
                )

            elif (
                received_msg["header"]["msg_type"] == "error"
                and received_msg["parent_header"]["msg_id"] == msg_id
            ):
                error = f"{received_msg['content']['ename']}: {received_msg['content']['evalue']}"
                codeinterpreter_log.debug(
                    "Received [error], return the error %s" % error
                )
                return SandboxRunOutput(type="error", content=error)
