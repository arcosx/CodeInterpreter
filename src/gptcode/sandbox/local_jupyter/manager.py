import asyncio
import os
import subprocess
import time
from typing import List, Union

import aiohttp
import requests
from websockets.client import connect as ws_connect
from websockets.sync.client import connect as ws_sync_connect

from gptcode.sandbox.local_jupyter.sandbox import LocalJupyterSandbox
from gptcode.sandbox.manager import Manager
from gptcode.sandbox.schema import SandboxStatus
from gptcode.utils import import_jupyter_kernel_gateway
from gptcode.utils.log import gptcode_log

import_jupyter_kernel_gateway()


class LocalJupyterManager(Manager):
    def __init__(self, workdir: str = ".sandbox", port: int = 8888) -> None:
        super().__init__()
        self.session: Union[requests.Session, aiohttp.ClientSession] = None
        self.subprocess: Union[
            asyncio.subprocess.Process, subprocess.Popen, None
        ] = None
        self.workdir = workdir
        self.port = port

    def init(self) -> None:
        self.session = requests.Session()

        out = subprocess.PIPE
        workdir = os.path.abspath(self.workdir)
        os.makedirs(workdir, exist_ok=True)
        gptcode_log.debug("Starting kernelgateway...")

        env = os.environ.copy()
        env["JUPYTER_DATA_DIR"] = workdir

        self.subprocess = subprocess.Popen(
            [
                "jupyter",
                "kernelgateway",
                "--KernelGatewayApp.ip='0.0.0.0'",
                f"--KernelGatewayApp.port={self.port}",
                "--JupyterWebsocketPersonality.list_kernels=true",
                "--KernelGatewayApp.log_level=DEBUG",
                "--JupyterWebsocketPersonality.env_whitelist JUPYTER_DATA_DIR",
            ],
            stdout=out,
            stderr=out,
            cwd=workdir,
            env=env,
        )
        gptcode_log.debug(f"Starting jupyter kernelgateway pid {self.subprocess.pid}")
        with open(
            os.path.join(workdir, f"{self.subprocess.pid}.pid"),
            "w",
        ) as p:
            p.write("kernel")

        while True:
            try:
                response = self.session.get(self.base_HTTP_URL)
                if response.status_code == 200:
                    break
            except requests.exceptions.ConnectionError:
                pass
            gptcode_log.debug("Waiting for kernelgateway to start...")
            time.sleep(1)

        gptcode_log.debug("kernelgateway start success!")

    async def ainit(self) -> None:
        self.session = aiohttp.ClientSession()

        out = subprocess.PIPE
        workdir = os.path.abspath(self.workdir)
        os.makedirs(workdir, exist_ok=True)
        gptcode_log.debug("Starting kernelgateway...")

        env = os.environ.copy()
        env["JUPYTER_DATA_DIR"] = workdir

        out = asyncio.subprocess.PIPE
        self.subprocess = await asyncio.create_subprocess_exec(
            "jupyter",
            "kernelgateway",
            "--KernelGatewayApp.ip='0.0.0.0'",
            f"--KernelGatewayApp.port={self.port}",
            "--JupyterWebsocketPersonality.list_kernels=true",
            "--KernelGatewayApp.log_level=DEBUG",
            "--JupyterWebsocketPersonality.env_whitelist JUPYTER_DATA_DIR",
            stdout=out,
            stderr=out,
            cwd=workdir,
            env=env,
        )
        gptcode_log.debug(f"Starting jupyter kernelgateway pid {self.subprocess.pid}")
        with open(
            os.path.join(workdir, f"{self.subprocess.pid}.pid"),
            "w",
        ) as p:
            p.write("kernel")

        while True:
            try:
                response = await self.session.get(self.base_HTTP_URL)
                if response.status == 200:
                    break
            except aiohttp.ClientConnectorError:
                pass
            except aiohttp.ServerDisconnectedError:
                pass
            await asyncio.sleep(1)

        gptcode_log.debug("kernelgateway start success!")

    def list(self) -> LocalJupyterSandbox:
        ...

    async def alist(self) -> List[LocalJupyterSandbox]:
        ...

    def start(self) -> LocalJupyterSandbox:
        response = self.session.post(f"{self.base_HTTP_URL}/kernels", json={})
        kernel_id = response.json()["id"]
        ws = ws_sync_connect(f"{self.base_WebSocket_URL}/kernels/{kernel_id}/channels")

        return LocalJupyterSandbox(id=kernel_id, ws=ws)

    async def astart(self) -> LocalJupyterSandbox:
        response = self.session.post(f"{self.base_HTTP_URL}/kernels", json={})
        kernel_id = response.json()["id"]
        ws = await ws_connect(f"{self.base_WebSocket_URL}/kernels/{kernel_id}/channels")

        return LocalJupyterSandbox(id=kernel_id, ws=ws)

    def get(self, id: str | None) -> LocalJupyterSandbox:
        ...

    async def get(self, id: str | None) -> LocalJupyterSandbox:
        ...

    def status(self, id: str) -> SandboxStatus:
        ...

    async def astatus(self, id: str) -> SandboxStatus:
        ...

    def restart(self, id: str) -> SandboxStatus:
        ...

    async def arestart(self, id: str) -> SandboxStatus:
        ...

    def delete(self, id: str):
        ...

    async def adelete(self, id: str):
        ...

    def stop(self) -> SandboxStatus:
        if self.subprocess is not None:
            self.subprocess.terminate()
            self.subprocess.wait()
            self.subprocess = None

    async def astop(self) -> SandboxStatus:
        if self.subprocess is not None:
            self.subprocess.terminate()
            await self.subprocess.wait()
            self.subprocess = None

        if self.session is not None:
            await self.session.close()
            self.session = None

    @property
    def base_HTTP_URL(self) -> str:
        return f"http://0.0.0.0:{self.port}/api"

    @property
    def base_WebSocket_URL(self) -> str:
        return f"ws://0.0.0.0:{self.port}/api"
