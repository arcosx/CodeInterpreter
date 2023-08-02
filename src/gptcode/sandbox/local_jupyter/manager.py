import asyncio
import os
import shutil
import signal
import subprocess
import time
from asyncio.subprocess import Process
from typing import Dict, List, Union

import aiohttp
import requests

from gptcode.sandbox.local_jupyter.sandbox import LocalJupyterSandbox
from gptcode.sandbox.manager import SandboxManager
from gptcode.sandbox.schema import SandboxResponse
from gptcode.utils.log import gptcode_log


class LocalJupyterManager(SandboxManager):
    def __init__(self, workdir: str = ".sandbox", port: int = 8888) -> None:
        super().__init__()
        self.session: Union[requests.Session, aiohttp.ClientSession] = None
        self.subprocess: Union[Process, subprocess.Popen, None] = None
        self.workdir = workdir
        self.port = port
        self.sandboxs:Dict[str,LocalJupyterSandbox] = {}

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
                    "--KernelGatewayApp.kernel_manager_class=notebook.services.kernels.kernelmanager.AsyncMappingKernelManager",
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
                    gptcode_log.debug("kernelgateway start success!")
                    break
            except requests.exceptions.ConnectionError:
                pass
            gptcode_log.debug("Waiting for kernelgateway to start...")
            time.sleep(1)

       

    async def ainit(self) -> None:
        self.session = aiohttp.ClientSession()

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
                "--KernelGatewayApp.kernel_manager_class=notebook.services.kernels.kernelmanager.AsyncMappingKernelManager",
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
        return list(self.sandboxs.values())
        
    async def alist(self) -> List[LocalJupyterSandbox]:
        return list(self.sandboxs.values())

    def start(self) -> LocalJupyterSandbox:
        response = self.session.post(f"{self.base_http_url}/kernels", json={})
        kernel_id = response.json()["id"]
        ws_url = f"{self.base_websocket_url}/kernels/{kernel_id}/channels"

        sandbox = LocalJupyterSandbox.sync_init(
            id=kernel_id, ws_url=ws_url, workdir=f"{self.workdir}/{kernel_id}"
        )
        
        self.sandboxs[kernel_id] = sandbox
        
        return sandbox

    async def astart(self) -> LocalJupyterSandbox:
        response = await self.session.post(f"{self.base_http_url}/kernels", json={})
        data = await response.json()
        kernel_id = data["id"]
        ws_url = f"{self.base_websocket_url}/kernels/{kernel_id}/channels"

        sandbox = await LocalJupyterSandbox.async_init(
                    id=kernel_id, ws_url=ws_url, workdir=f"{self.workdir}/{kernel_id}"
                )
        
        self.sandboxs[kernel_id] = sandbox
        
        return sandbox

    def get(self, id: str | None) -> LocalJupyterSandbox:
        return self.sandboxs[id]

    async def aget(self, id: str | None) -> LocalJupyterSandbox:
        return self.sandboxs[id]


    def restart(self, id: str) -> SandboxResponse:
        gptcode_log.debug("restart kernel %s",id)
        response = self.session.post(f"{self.base_http_url}/kernels/{id}/restart", json={})
        if response.status_code == 200:
            self.sandboxs[id].reconnect()
            return SandboxResponse(content="success")
        else:
            return SandboxResponse(content="restart failed")
        
    async def arestart(self, id: str) -> SandboxResponse:
        gptcode_log.debug("restart kernel %s",id)
        response = await self.session.post(f"{self.base_http_url}/kernels/{id}/restart", json={})
        if response.status_code == 200:
            await self.sandboxs[id].areconnect()
            return SandboxResponse(content="success")
        else:
            return SandboxResponse(content="restart failed")

    def delete(self, id: str):
        gptcode_log.debug("delete kernel %s",id)
        self.sandboxs[id].close_websocket()
        response = self.session.delete(f"{self.base_http_url}/kernels/{id}", json={})
        if response.status_code <= 400:
            self.sandboxs.pop(id)
            return SandboxResponse(content="success")

    async def adelete(self, id: str):
        gptcode_log.debug("delete kernel %s",id)
        await self.sandboxs[id].aclose_websocket()
        response = await self.session.delete(f"{self.base_http_url}/kernels/{id}", json={})
        if response.status <= 400:
            self.sandboxs.pop(id)
            return SandboxResponse(content="success")
        
    def stop(self) -> SandboxResponse:
        gptcode_log.debug("Begin stop sandbox manager")
        for sandbox_id in list(self.sandboxs.keys()):
            self.delete(sandbox_id)
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
        shutil.rmtree(self.workdir, ignore_errors=True, onerror=None)
        gptcode_log.debug("sandbox manager stoped")
        
    async def astop(self) -> SandboxResponse:
        gptcode_log.debug("Begin stop sandbox manager")
        if self.sandboxs:
            await asyncio.gather(*(self.adelete(id) for id in list(self.sandboxs.keys())))
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
        shutil.rmtree(self.workdir, ignore_errors=True, onerror=None)
        gptcode_log.debug("sandbox manager stoped")
        
    @property
    def base_http_url(self) -> str:
        return f"http://0.0.0.0:{self.port}/api"

    @property
    def base_websocket_url(self) -> str:
        return f"ws://0.0.0.0:{self.port}/api"
