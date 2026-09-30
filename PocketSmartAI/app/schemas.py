from typing import Literal
from pydantic import BaseModel, Field, EmailStr, field_validator

PlannerType = Literal["home", "party", "jewelry"]

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class HomeRequest(BaseModel):
    budget: int = Field(gt=0, le=10_000_000)
    city: str = Field(default="Chennai", min_length=2, max_length=100)
    rooms: list[str] = Field(min_length=1)
    style: str = Field(default="modern", max_length=80)
    priorities: str = Field(default="functionality, value for money", max_length=300)
    quantities: dict[str, int] = Field(default_factory=dict)

class PartyRequest(BaseModel):
    budget: int = Field(gt=0, le=10_000_000)
    city: str = Field(default="Chennai", min_length=2, max_length=100)
    event_type: str = Field(min_length=2, max_length=80)
    guests: int = Field(gt=0, le=10000)
    venue: str = Field(default="flexible", max_length=200)
    food_preference: str = Field(default="mixed", max_length=100)
    priorities: str = Field(default="food, comfort, decoration", max_length=300)

class JewelryRequest(BaseModel):
    budget: int = Field(gt=0, le=10_000_000)
    occasion: str = Field(min_length=2, max_length=100)
    style: str = Field(default="elegant", max_length=100)
    metal_preference: str = Field(default="any", max_length=100)
    outfit_description: str = Field(default="", max_length=1000)

class RecommendationItem(BaseModel):
    name: str
    category: str
    estimated_price: int
    platform: str
    url: str
    reason: str
    quantity: int = 1

class BudgetAllocation(BaseModel):
    category: str
    amount: int
    percentage: float
    note: str

class RecommendationResponse(BaseModel):
    planner: PlannerType
    title: str
    summary: str
    budget: int
    estimated_total: int
    remaining_budget: int
    allocations: list[BudgetAllocation]
    recommendations: list[RecommendationItem]
    tips: list[str]
    disclaimer: str = "Prices and availability are estimates; verify details on the linked platform before purchase."

class SessionInfo(BaseModel):
    logged_in: bool
    user_id: int | None = None
    name: str | None = None
    email: str | None = None
