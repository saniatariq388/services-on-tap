from sqlmodel import JSON, Field,SQLModel
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import Column, JSON

# table  structure/ model

class Service(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    service_name: str = Field(index=True, unique=True)  # filter is pr bhi hoga worker
   

class Worker(SQLModel, table=True):
    id: Optional[int] =Field(default=None, primary_key=True)
    worker_name: str = Field(index=True)   # filter is pr bhi hoga worker
    bio: Optional[str] = None
    skills: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))
    is_available: bool = Field(default=True)
    phone: str =Field(index=True, unique=True)
    experience: Optional[int] = None 
    area: str = Field(index=True) 
    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)




class WorkerService(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    worker_id: int = Field(foreign_key="worker.id", index=True)
    service_id: int = Field(foreign_key="service.id", index=True)
   





# Name *
# Phone *
# Service *
# Skills
# Experience
# Area *
# Availability
# Description
# Profile picture
# Rate


# class like pydantic (BaseModel)  
# response body 

# class ReviewRead():
#     id: int
#     play_name: str
#     reviewer_name: str
#     rating: int = Field(ge=1, le=5)
#     comment: str 
#     created_at: datetime 

# class ReviewUpdate():
#     rating: int = Field(ge=1, le=5)
#     comment: str 



