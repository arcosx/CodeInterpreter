import asyncio
import shutil
import time
from gptcode.sandbox.local_jupyter.manager import LocalJupyterManager
import os
import psutil


#  tips: clear all jupyter thread
#  ps aux | grep jupyter | grep -v grep | awk '{ print $2 }' | xargs kill -9


def test_manager_init():
    manager = LocalJupyterManager()
    manager.init()

    assert os.path.exists(".sandbox")
    assert manager.subprocess is not None
    assert psutil.pid_exists(manager.subprocess.pid)
    assert os.path.exists(".sandbox/jupyter-kernelgateway.log")
    manager.stop()

    shutil.rmtree(".sandbox")


def test_manager_alist():
    manager = LocalJupyterManager()

    async def run_ainit():
        await manager.ainit()
        assert os.path.exists(".sandbox")
        assert manager.subprocess is not None
        await manager.astop()
        assert os.path.exists(".sandbox/jupyter-kernelgateway.log")

    asyncio.run(run_ainit())

    shutil.rmtree(".sandbox")


def test_sandbox_start():
    manager = LocalJupyterManager()
    manager.init()
    sandbox = manager.start()
    sandbox.ws.recv(3)
    sandbox.ws.close()
    manager.stop()
    shutil.rmtree(".sandbox")


def test_sandbox_astart():
    manager = LocalJupyterManager(port=8892)
    manager.init()
    sandbox = manager.start()
    sandbox.ws.recv(3)
    sandbox.ws.close()
    manager.stop()
    shutil.rmtree(".sandbox")
