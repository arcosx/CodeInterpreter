from codeinterpreter.sandbox.sandbox import Sandbox
from codeinterpreter.adapter.adapter import Adapter


class CodeInterpreterSession:
    def __init__(self) -> None:
        self.sandbox: Sandbox = None
        self.adapter: Adapter = None
