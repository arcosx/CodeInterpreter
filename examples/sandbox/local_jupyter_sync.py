import logging
from gptcode.sandbox.local_jupyter.manager import LocalJupyterManager
from gptcode.sandbox.schema import SandboxRunConfig
import gptcode

logger = logging.getLogger(f"gptcode:{gptcode.__version__}")
logger.setLevel(logging.DEBUG)

def main():
    try:
        manager = LocalJupyterManager()
        manager.init()
        sandbox_add =  manager.start()
        sandbox_add.run("a = 5")
        sandbox_add.run("b = 10")
        
        add_result =  sandbox_add.run("a + b")
        
        sandbox_mul =  manager.start()
        sandbox_mul.run("a = 5")
        sandbox_mul.run("b = 10")
        mul_result =  sandbox_add.run("a * b")
        
        print(int(add_result.content) * int(mul_result.content))
        
    finally:
        # manager.stop()
        pass
    
if __name__ == "__main__":
    main()