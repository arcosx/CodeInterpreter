from gptcode.sandbox.sandbox import Sandbox


class LocalJupyterSandbox(Sandbox):
    def __init__(self, port: int = 8888) -> None:
        super().__init__()
        self.port = port
        self.kernel: Optional[dict] = None
