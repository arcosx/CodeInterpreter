import asyncio
import logging

from notebook.services.kernels.kernelmanager import MappingKernelManager

import codeinterpreter
from codeinterpreter.sandbox.local_jupyter.manager import LocalJupyterManager

logger = logging.getLogger(f"codeinterpreter:{codeinterpreter.__version__}")
logger.setLevel(logging.DEBUG)

async def calculate_add(manager:LocalJupyterManager)->int:
    sandbox_add = await manager.astart()
    await sandbox_add.arun("a = 5")
    await sandbox_add.arun("b = 10")
    add_result = await sandbox_add.arun("a + b")
    return int(add_result.content)

async def calculate_mul(manager:LocalJupyterManager)->int:
    sandbox_mul = await manager.astart()
    await sandbox_mul.arun("a = 5")
    await sandbox_mul.arun("b = 10")
    mul_result = await sandbox_mul.arun("a * b")
    return int(mul_result.content)

async def main():
    try:
        manager = LocalJupyterManager()
        await manager.ainit()
        add_result, mul_result = await asyncio.gather(calculate_add(manager), calculate_mul(manager))
        print(int(add_result) * int(mul_result))

    finally:
        await manager.astop()

if __name__ == "__main__":
    asyncio.run(main())
