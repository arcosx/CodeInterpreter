import asyncio
import os
import subprocess
import time
from asyncio.subprocess import Process
from typing import List, Union
import signal
import aiohttp
import psutil
import requests

from gptcode.sandbox.local_jupyter.sandbox import LocalJupyterSandbox
from gptcode.sandbox.manager import SandboxManager
from gptcode.sandbox.schema import SandboxStatus
from gptcode.utils import import_jupyter_kernel_gateway
from gptcode.utils.log import gptcode_log

import_jupyter_kernel_gateway()


class LocalJupyterManager(SandboxManager):
    def __init__(self, workdir: str = ".sandbox", port: int = 8888) -> None:
        super().__init__()
        self.session: Union[requests.Session, aiohttp.ClientSession] = None
        self.subprocess: Union[Process, subprocess.Popen, None] = None
        self.workdir = workdir
        self.port = port

    def init(self) -> None:
        self.session = requests.Session()

        workdir = os.path.abspath(self.workdir)
        os.makedirs(workdir, exist_ok=True)
        gptcode_log.debug("Starting kernelgateway...")

        env = os.environ.copy()
        env["JUPYTER_DATA_DIR"] = workdir

        with open(
            os.path.join(workdir, "jupyter-kernelgateway.log"), "w", encoding="utf-8"
        ) as subprocess_log_file:
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
                stdout=subprocess_log_file,
                stderr=subprocess_log_file,
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
                response = self.session.get(self.base_http_url)
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

        with open(
            os.path.join(workdir, "jupyter-kernelgateway.log"), "w", encoding="utf-8"
        ) as subprocess_log_file:
            self.subprocess = await asyncio.create_subprocess_exec(
                "jupyter",
                "kernelgateway",
                "--KernelGatewayApp.ip='0.0.0.0'",
                f"--KernelGatewayApp.port={self.port}",
                "--JupyterWebsocketPersonality.list_kernels=true",
                "--KernelGatewayApp.log_level=DEBUG",
                "--JupyterWebsocketPersonality.env_whitelist JUPYTER_DATA_DIR",
                stdout=subprocess_log_file,
                stderr=subprocess_log_file,
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
                response = await self.session.get(self.base_http_url)
                if response.status == 200:
                    break
            except aiohttp.ClientConnectorError:
                pass
            except aiohttp.ServerDisconnectedError:
                pass
            await asyncio.sleep(1)

        gptcode_log.debug("kernelgateway start success!")

    def list(self) -> List[LocalJupyterSandbox]:
        ...

    async def alist(self) -> List[LocalJupyterSandbox]:
        ...

    def start(self) -> LocalJupyterSandbox:
        response = self.session.post(f"{self.base_http_url}/kernels", json={})
        kernel_id = response.json()["id"]
        ws_url = f"{self.base_websocket_url}/kernels/{kernel_id}/channels"

        return LocalJupyterSandbox.sync_init(
            id=kernel_id, ws_url=ws_url, workdir=f"{self.workdir}/{kernel_id}"
        )

    async def astart(self) -> LocalJupyterSandbox:
        response = self.session.post(f"{self.base_http_url}/kernels", json={})
        kernel_id = response.json()["id"]
        ws_url = f"{self.base_websocket_url}/kernels/{kernel_id}/channels"

        return await LocalJupyterSandbox.async_init(
            id=kernel_id, ws_url=ws_url, workdir=f"{self.workdir}/{kernel_id}"
        )

    def get(self, id: str | None) -> LocalJupyterSandbox:
        ...

    async def aget(self, id: str | None) -> LocalJupyterSandbox:
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
        gptcode_log.debug("Begin stop sandbox manager")
        if self.subprocess is not None:
            self.subprocess.send_signal(signal.SIGINT)
            try:
                self.subprocess.wait(30)
            except subprocess.TimeoutExpired:
                self.subprocess.kill()
            finally:
                self.subprocess = None
        if self.session is not None:
            self.session.close()
            self.session = None

    async def astop(self) -> SandboxStatus:
        gptcode_log.debug("Begin stop sandbox manager")
        if self.subprocess is not None:
            self.subprocess.send_signal(signal.SIGINT)
            try:
                await self.subprocess.wait()
            except asyncio.TimeoutError:
                self.subprocess.kill()
            finally:
                self.subprocess = None

        if self.session is not None:
            await self.session.close()
            self.session = None

    @property
    def base_http_url(self) -> str:
        return f"http://0.0.0.0:{self.port}/api"

    @property
    def base_websocket_url(self) -> str:
        return f"ws://0.0.0.0:{self.port}/api"
