from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    user_id: str


class User(UserBase):
    id: int


class PackageBase(BaseModel):
    package_name: str
    weight: float
    type_id: int
    cost_content: float


class CreatePackage(PackageBase):
    user_id: str
    unic_id: str
    cost_shipping: float = 0


class GetPackage(BaseModel):
    package_name: str
    unic_id: str
    weight: float
    cost_content: float
    cost_shipping: float | None
    type_name: str
    created_at: datetime | None
    updated_at: datetime | None


class TypeOrder(BaseModel):
    id: int
    type_name: str
