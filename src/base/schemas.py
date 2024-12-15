from pydantic import BaseModel


class PingResponseSchema(BaseModel):
    """Ping response schema"""

    OK: bool
