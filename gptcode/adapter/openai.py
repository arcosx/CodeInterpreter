from gptcode.utils import import_openai
from gptcode.utils.error import wrap_error

import_openai()

import openai


class ChatCompletion(openai.ChatCompletion):
    """The openai ChatCompletion Wrapper"""

    @classmethod
    def _llm_handler(cls, *llm_args, **llm_kwargs):
        try:
            return (
                super().create(*llm_args, **llm_kwargs)
                if cls.llm is None
                else cls.llm(*llm_args, **llm_kwargs)
            )
        except openai.OpenAIError as e:
            raise wrap_error(e) from e
