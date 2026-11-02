from pydantic import BaseModel, Field

class InvestigationRequest(BaseModel):
    service: str = Field(min_length=2, max_length=100, pattern=r"^[a-zA-Z0-9._-]+$")
    incident: str = Field(min_length=8, max_length=2000)

class InvestigationResponse(BaseModel):
    request_id: str
    service: str
    answer: str
    steps: int
    tools_called: list[str]
