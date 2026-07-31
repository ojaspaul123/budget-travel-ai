from pydantic import BaseModel, Field

class SearchRequest(BaseModel):
    query: str = Field(..., example="budget restaurants")
    lat: float = Field(..., example=22.5726)
    lng: float = Field(..., example=88.3639)
    radius: int = Field(default=5000, description="Search radius in meters")
    max_budget_level: int = Field(
        default=1,
        ge=0,
        le=4,
        description="0=free, 1=inexpensive, 2=moderate, 3=expensive, 4=very expensive",
    )