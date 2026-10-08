from sqlmodel import SQLModel, Field
from typing import Optional

# validation class like pydantic (BaseModel)  
# request body 

class WorkerCreate(SQLModel):
    worker_name: str
    skills: Optional[list[str]] = None 
    phone: str 
    experience: int
    area: str
    services: list[str] = Field(min_length=1)
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
