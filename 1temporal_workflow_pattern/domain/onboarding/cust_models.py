from pydantic import BaseModel, EmailStr
from typing import Optional


class CustomerOnboardingInput(BaseModel):
    customer_id: str
    first_name: str
    last_name: str
    email: EmailStr


class CustomerOnboardingState(BaseModel):
    customer_id: str
    first_name: str
    last_name: str
    email: EmailStr
    kyc_passed: Optional[bool] = None
    credit_score: Optional[int] = None
    account_activated: bool = False