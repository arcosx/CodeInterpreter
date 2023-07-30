from typing import Optional

from pydantic import BaseModel


class SandboxStatus(BaseModel):
    status: str


class SandboxOutput(BaseModel):
    type: str
    content: str


class SandboxFile(BaseModel):
    name: str
    content: Optional[bytes] = None
