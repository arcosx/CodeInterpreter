import logging
from codeinterpreter.sandbox.local_jupyter.manager import LocalJupyterManager
import codeinterpreter

logger = logging.getLogger(f"codeinterpreter:{codeinterpreter.__version__}")
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
        manager.stop()
    
if __name__ == "__main__":
    main()