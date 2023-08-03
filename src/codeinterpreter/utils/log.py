import logging

import codeinterpreter

FORMAT = "%(asctime)s - %(thread)d - %(filename)s-%(module)s:%(lineno)s - %(levelname)s: %(message)s"
logging.basicConfig(format=FORMAT)

codeinterpreter_log = logging.getLogger(f"codeinterpreter:{codeinterpreter.__version__}")
