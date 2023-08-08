from typing import List
from codeinterpreter.adapter.adapter import Adapter
from codeinterpreter.agent.openai_functions_agent.base import CustomOpenAIFunctionsAgent
from codeinterpreter.utils.log import codeinterpreter_log
from codeinterpreter.sandbox.schema import SandboxRunOutput

from pydantic import BaseModel
from langchain.schema.language_model import BaseLanguageModel
from codeinterpreter.sandbox.sandbox import Sandbox

from langchain.chat_models import ChatOpenAI

from langchain.agents import AgentExecutor, BaseSingleActionAgent
from langchain.tools import BaseTool, StructuredTool


class OpenAI(Adapter):
    def __init__(self, sandbox: Sandbox, model: str = "gpt-3.5-turbo-0613") -> None:
        super().__init__()
        self.sandbox: Sandbox = sandbox
        self.llm: BaseLanguageModel = ChatOpenAI(temperature=0, model=model)
        self.agent_executor: AgentExecutor = self._agent_executor()

    def _tools(self) -> List[BaseTool]:
        class CodeInput(BaseModel):
            code: str

        return [
            StructuredTool(
                name="python",
                description="Input a string of code to a ipython interpreter. "
                "Write the entire code in a single string. This string can "
                "be really long, so you can use the `;` character to split lines. "
                "Variables are preserved between runs. ",
                func=self._sandbox_run_handler,
                coroutine=self._asandbox_run_handler,
                args_schema=CodeInput,
            )
        ]

    def _agent(self) -> BaseSingleActionAgent:
        return CustomOpenAIFunctionsAgent.from_llm_and_tools(
            llm=self.llm, tools=self._tools()
        )

    def _agent_executor(self) -> AgentExecutor:
        return AgentExecutor(agent=self._agent(), tools=self._tools())

    def _sandbox_run_handler(self, code: str):
        output: SandboxRunOutput = self.sandbox.run(code=code)
        return output.content

    async def _asandbox_run_handler(self, code: str):
        output: SandboxRunOutput = await self.sandbox.arun(code=code)
        return output.content

    def run(self, code: str):
        return self.agent_executor.run(code)

    async def arun(self, code: str):
        return self.agent_executor.arun(code)
