from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

from server_core.utils import get_current_time

SEPERATE_OP = "data: "


def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(part.title() for part in parts[1:])


T = TypeVar("T")


class ResponseMessage(BaseModel):
    status: int = Field(default=200)
    info: str = Field(default="")
    server_at: int = Field(default_factory=get_current_time)


def get_default_response_message() -> ResponseMessage:
    return ResponseMessage(status=200, info="", server_at=get_current_time())


class ResponseSucc(BaseModel, Generic[T]):
    data: T = Field(...)
    extra: ResponseMessage = Field(default_factory=get_default_response_message)


class ResponseError(BaseModel, Generic[T]):
    data: Optional[T] = Field(default=None)
    extra: ResponseMessage = Field(...)

    @classmethod
    def from_error(cls, message: str, status: int = 500) -> "ResponseError":
        return cls(extra=ResponseMessage(info=message, status=status))
