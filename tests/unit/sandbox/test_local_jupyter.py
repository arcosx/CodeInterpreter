import asyncio
import os

import psutil

from gptcode.sandbox.local_jupyter.manager import LocalJupyterManager
import tempfile
from pathlib import Path

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




def test_manager_ainit():
    manager = LocalJupyterManager()

    async def run_ainit():
        await manager.ainit()
        assert os.path.exists(".sandbox")
        assert manager.subprocess is not None
        assert os.path.exists(".sandbox/jupyter-kernelgateway.log")
        await manager.astop()

    asyncio.run(run_ainit())


def test_sandbox_start():
    manager = LocalJupyterManager()
    manager.init()
    sandbox = manager.start()
    sandbox.ws.recv()
    manager.stop()


def test_sandbox_astart():
    manager = LocalJupyterManager()

    async def run_astart():
        await manager.ainit()
        sandbox = await manager.astart()
        await sandbox.ws.recv()
        await manager.astop()

    asyncio.run(run_astart())



def test_sandbox_run():
    manager = LocalJupyterManager()
    manager.init()
    sandbox = manager.start()
    sandbox_output = sandbox.run(
        'print("hello,world")'
    )
    assert sandbox_output.content == "hello,world"
    assert sandbox_output.type == "text"

    sandbox_output = sandbox.run(
        'print("to the world")'
    )
    assert sandbox_output.content == "to the world"
    assert sandbox_output.type == "text"

    manager.stop()



def test_sandbox_arun():
    manager = LocalJupyterManager()

    async def run_arun():
        await manager.ainit()
        sandbox = await manager.astart()
        sandbox_output = await sandbox.arun(
            'print("hello,world")'
        )
        assert sandbox_output.content == "hello,world"
        assert sandbox_output.type == "text"

        sandbox_output = await sandbox.arun(
            'print("to the world")'
        )
        assert sandbox_output.content == "to the world"
        assert sandbox_output.type == "text"

        await manager.astop()

    asyncio.run(run_arun())



def test_sandbox_upload_download():
    test_file = tempfile.NamedTemporaryFile(delete=False)
    test_file.write(b"test_content")
    test_file.close()
    with open(test_file.name, "rb") as f:
        content = f.read()
        
    manager = LocalJupyterManager()
    manager.init()
    sandbox = manager.start()

    response = sandbox.upload(Path(test_file.name).name, content)
    assert response.content == f"{Path(test_file.name).name} uploaded successfully"

    with open(os.path.join(sandbox.workdir, Path(test_file.name).name), "rb") as file:
        assert file.read() == content
    
    downloaded_file = sandbox.download(Path(test_file.name).name)
    assert downloaded_file.name == Path(test_file.name).name
    assert downloaded_file.content == content
    
    manager.stop()


def test_sandbox_aupload_adownload():
    test_file = tempfile.NamedTemporaryFile(delete=False)
    test_file.write(b"test_content")
    test_file.close()
    with open(test_file.name, "rb") as f:
        content = f.read()
        
    manager = LocalJupyterManager()
    async def run_aupload():
        await manager.ainit()
        sandbox = await manager.astart()
        response = await sandbox.aupload(Path(test_file.name).name, content)
        assert response.content == f"{Path(test_file.name).name} uploaded successfully"
        with open(os.path.join(sandbox.workdir, Path(test_file.name).name), "rb") as file:
            assert file.read() == content

        downloaded_file = await sandbox.adownload(Path(test_file.name).name)
        assert downloaded_file.name == Path(test_file.name).name
        assert downloaded_file.content == content
        
        await manager.astop()

    asyncio.run(run_aupload())
