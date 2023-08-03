from typing import Optional

from pydantic import BaseModel


class SandboxResponse(BaseModel):
    content: str


class SandboxRunOutput(BaseModel):
    type: str
    content: str


class SandboxFile(BaseModel):
    name: str
    content: Optional[bytes] = None


class SandboxRunConfig(BaseModel):
    retry: int = 3
