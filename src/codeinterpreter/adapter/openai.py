import openai

from codeinterpreter.adapter.adapter import Adapter


class OpenAI(Adapter):
    def __init__(self) -> None:
        super().__init__()
        self.type = "openai"

    @classmethod
    def llm_handler(cls, *llm_args, **llm_kwargs):
        completion = openai.ChatCompletion.create(*llm_args, **llm_kwargs)
        return completion
