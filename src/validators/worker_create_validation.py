from sqlmodel import SQLModel, Field
from typing import Optional

from src.models.model import ServiceName

# validation class like pydantic (BaseModel)  
# request body 

class WorkerCreate(SQLModel):
    worker_name: str
    phone: str
    area: str
    services: list[ServiceName] = Field(min_length=1)    # dropdown se, ek ya zyada
    skills: Optional[list[str]] = None
    experience: Optional[int] = None
    bio: Optional[str] = None
    is_available: bool = True




# id: Optional[int] =Field(default=None, primary_key=True)
#     worker_name: str = Field(index=True)   # filter is pr bhi hoga worker
#     bio: Optional[str] = None
#     skills: Optional[str] = None
#     is_available: bool = Field(default=True)
#     phone: str =Field(index=True, unique=True)
#     rating: Optional[int] = Field(ge=1, le=5)
#     experience: Optional[int] = None 
#     area: str = Field(index=True) 
#     service_id: int = Field(foreign_key="Service.id", index=True)
#     created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))
#     updated_at: Optional[datetime] = Field(default=None)
