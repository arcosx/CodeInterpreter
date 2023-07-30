import asyncio
import shutil
import time
from gptcode.sandbox.local_jupyter.manager import LocalJupyterManager
import os
import psutil


#  tips: clear all jupyter thread
#  ps aux | grep jupyter | grep -v grep | awk '{ print $2 }' | xargs kill -9


def test_manager_init():
    m = LocalJupyterManager(port=8890)
    m.init()

    assert os.path.exists(".sandbox")
    assert m.subprocess is not None
    assert psutil.pid_exists(m.subprocess.pid)
    psutil.Process(m.subprocess.pid).terminate()

    shutil.rmtree(".sandbox")


def test_manager_alist():
    m = LocalJupyterManager(port=8891)

    async def run_ainit():
        await m.ainit()
        assert os.path.exists(".sandbox")
        assert m.subprocess is not None
        assert psutil.pid_exists(m.subprocess.pid)
        psutil.Process(m.subprocess.pid).terminate()

    asyncio.run(run_ainit())

    shutil.rmtree(".sandbox")
