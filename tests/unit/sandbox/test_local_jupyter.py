import asyncio
import shutil
import time
from gptcode.sandbox.local_jupyter.manager import LocalJupyterManager
import os
import psutil


#  tips: clear all jupyter thread
#  ps aux | grep jupyter | grep -v grep | awk '{ print $2 }' | xargs kill -9


def test_manager_init():
    manager = LocalJupyterManager(port=8890)
    manager.init()

    assert os.path.exists(".sandbox")
    assert manager.subprocess is not None
    assert psutil.pid_exists(manager.subprocess.pid)
    manager.stop()

    shutil.rmtree(".sandbox")


def test_manager_alist():
    manager = LocalJupyterManager(port=8891)

    async def run_ainit():
        await manager.ainit()
        assert os.path.exists(".sandbox")
        assert manager.subprocess is not None
        await manager.astop()

    asyncio.run(run_ainit())

    shutil.rmtree(".sandbox")


def test_start():
    manager = LocalJupyterManager(port=8892)
    manager.init()
    sandbox = manager.start()
    assert sandbox.ws is not None
    sandbox.ws.close()
    manager.stop()
    shutil.rmtree(".sandbox")
