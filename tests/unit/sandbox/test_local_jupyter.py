import asyncio
import shutil
import time
from gptcode.sandbox.local_jupyter.manager import LocalJupyterManager
import os
import psutil


def test_manager_init():
    m = LocalJupyterManager()
    m.init()

    assert os.path.exists(".sandbox")
    assert m.subprocess is not None
    assert psutil.pid_exists(m.subprocess.pid)
    psutil.Process(m.subprocess.pid).terminate()

    shutil.rmtree(".sandbox")


def test_manager_alist():
    m = LocalJupyterManager()

    async def run_ainit():
        await m.ainit()
        assert os.path.exists(".sandbox")
        assert m.subprocess is not None
        assert psutil.pid_exists(m.subprocess.pid)
        psutil.Process(m.subprocess.pid).terminate()

    asyncio.run(run_ainit())

    shutil.rmtree(".sandbox")
