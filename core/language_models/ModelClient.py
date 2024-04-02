from pydantic import BaseModel, Field


class SideKickClient(BaseModel):
    base_url: str
    api_key: str
    timeout: int
    max_retries: int



