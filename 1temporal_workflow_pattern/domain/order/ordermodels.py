from pydantic import BaseModel
from typing import List, Dict, Optional


class OrderItem(BaseModel):
    sku: str
    qty: int


class OrderProcessingInput(BaseModel):
    order_id: str
    customer_id: str
    payment_method: str
    items: List[OrderItem]


class OrderProcessingState(BaseModel):
    order_id: str
    customer_id: str
    payment_method: str
    items: List[OrderItem]
    inventory_ok: Optional[bool] = None
    fraud_ok: Optional[bool] = None
    status: str = "PENDING"