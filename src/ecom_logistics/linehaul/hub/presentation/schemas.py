from pydantic import BaseModel, Field


class HubResponse(BaseModel):
    id: str
    name: str
    type: int
    address_text: str
    lat: float
    lng: float
    status: int
    deleted_at: str | None = None


class PaginatedHubResponse(BaseModel):
    items: list[HubResponse]
    total: int
    page: int
    size: int
    pages: int


class CreateHubRequest(BaseModel):
    name: str
    type: int
    address_text: str
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)


class UpdateHubRequest(BaseModel):
    name: str
    type: int
    address_text: str
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    status: int
