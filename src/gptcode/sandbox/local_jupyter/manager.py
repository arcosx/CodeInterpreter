import asyncio
import os
import subprocess
from typing import List, Union

import aiohttp
import requests

from gptcode.sandbox.local_jupyter.sandbox import LocalJupyterSandbox
from gptcode.sandbox.manager import Manager
from gptcode.sandbox.schema import SandboxStatus
from gptcode.utils import import_jupyter_kernel_gateway
from gptcode.utils.log import gptcode_log

import_jupyter_kernel_gateway()


class LocalJupyterManager(Manager):
    def __init__(self, workdir: str = ".sandbox") -> None:
        super().__init__()
        self.session: Union[requests.Session, aiohttp.ClientSession] = None
        self.subprocess: Union[
            asyncio.subprocess.Process, subprocess.Popen, None
        ] = None
        self.workdir = workdir

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
                "--KernelGatewayApp.port=8888",
                "--JupyterWebsocketPersonality.list_kernels=true",
                "--KernelGatewayApp.log_level=DEBUG",
                "--JupyterWebsocketPersonality.env_whitelist JUPYTER_DATA_DIR",
            ],
            stdout=out,
            stderr=out,
            cwd=workdir,
            env=env,
        )
        gptcode_log.debug(f"Started jupyter kernelgateway pid {self.subprocess.pid}")
        with open(
            os.path.join(workdir, f"{self.subprocess.pid}.pid"),
            "w",
        ) as p:
            p.write("kernel")

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
            "--KernelGatewayApp.port=8888",
            "--JupyterWebsocketPersonality.list_kernels=true",
            "--KernelGatewayApp.log_level=DEBUG",
            "--JupyterWebsocketPersonality.env_whitelist JUPYTER_DATA_DIR",
            stdout=out,
            stderr=out,
            cwd=workdir,
            env=env,
        )
        gptcode_log.debug(f"Started jupyter kernelgateway pid {self.subprocess.pid}")
        with open(
            os.path.join(workdir, f"{self.subprocess.pid}.pid"),
            "w",
        ) as p:
            p.write("kernel")

    def list(self) -> LocalJupyterSandbox:
        ...

    async def alist(self) -> List[LocalJupyterSandbox]:
        ...

    def start(self) -> LocalJupyterSandbox:
        ...

    async def astart(self) -> LocalJupyterSandbox:
        ...

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
