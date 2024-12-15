from typing import Any

from pydantic import BaseModel
from pydantic import model_validator
from pydantic import UUID4
from starlette.datastructures import URL


class BaseLogSchema(BaseModel):
    url: Any
    request_id: UUID4 | str

    @model_validator(mode="after")
    def prettify_data(self):
        if isinstance(self.url, URL):
            self.url = self.url.__str__()
        self.request_id = str(self.request_id)
        return self


class RequestLogSchema(BaseLogSchema):
    headers: Any
    body: dict | None = {}

    @model_validator(mode="after")
    def prepare_message(self):
        self.url = f"Request to {self.url}"
        return self


class ResponseLogSchema(BaseLogSchema):
    status_code: int | None = None
    headers: Any | None = None

    body: Any | None = {}

    @model_validator(mode="after")
    def prepare_message(self):
        self.url = f"Response from {self.url}"
        return self
