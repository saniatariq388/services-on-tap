from sqlmodel import SQLModel, Field
from typing import List, Optional



# validation class like pydantic (BaseModel)  
# request body 


class ServiceCreate(SQLModel):
    service_name: str


class ServiceUpdate(SQLModel):
    service_name: Optional[str] = None
    is_active: Optional[bool] = None