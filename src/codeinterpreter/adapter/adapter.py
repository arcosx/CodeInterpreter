from abc import ABC, abstractmethod


class Adapter(ABC):
    type: str

    @abstractmethod
    def llm_handler(self, *llm_args, **llm_kwargs):
        ...
