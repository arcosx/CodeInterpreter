import logging
from gptcode.sandbox.local_jupyter.manager import LocalJupyterManager
from gptcode.sandbox.schema import SandboxRunConfig
import gptcode

logger = logging.getLogger(f"gptcode:{gptcode.__version__}")
logger.setLevel(logging.DEBUG)

async def main():
    manager = LocalJupyterManager()
    await manager.ainit()
    sandbox = await manager.astart()
    await sandbox.arun("a = 5",SandboxRunConfig(retry=3))
    await sandbox.arun("b = 10",SandboxRunConfig(retry=3))
    
    result = await sandbox.arun("a * b",SandboxRunConfig(retry=3))
    print(result)
    await manager.astop()
    
if __name__ == "__main__":
    import asyncio

    asyncio.run(main())