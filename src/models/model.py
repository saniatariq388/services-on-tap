from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Field, Relationship, SQLModel, Column, JSON


from enum import Enum

class ServiceName(str, Enum):
    PLUMBER = "Plumber"
    ELECTRICIAN = "Electrician"
    PAINTER = "Painter"
    CARPENTER = "Carpenter"
    AC_TECHNICIAN = "AC Technician"
    MASON = "Mason"
    
# table  structure/ model

# class Service(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     service_name: str = Field(index=True, unique=True)  # filter is pr bhi hoga worker
   

# class Worker(SQLModel, table=True):
#     id: Optional[int] =Field(default=None, primary_key=True)
#     worker_name: str = Field(index=True)   # filter is pr bhi hoga worker
#     bio: Optional[str] = None
#     skills: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))
#     is_available: bool = Field(default=True)
#     phone: str =Field(index=True, unique=True)
#     experience: Optional[int] = None 
#     area: str = Field(index=True) 
#     created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))
#     updated_at: Optional[datetime] = Field(default=None)




# class WorkerService(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     worker_id: int = Field(foreign_key="worker.id", index=True)
#     service_id: int = Field(foreign_key="service.id", index=True)
   





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





class WorkerService(SQLModel, table=True):      # sab se pehle likhein
    worker_id: int = Field(foreign_key="worker.id", primary_key=True)
    service_id: int = Field(foreign_key="service.id", primary_key=True)


class Service(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    service_name: str = Field(index=True, unique=True)
    is_active: bool = Field(default=True)

    workers: list["Worker"] = Relationship(back_populates="services", link_model=WorkerService)


class Worker(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    worker_name: str = Field(index=True)
    phone: str = Field(index=True, unique=True)
    area: str = Field(index=True)
    skills: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))
    experience: Optional[int] = None
    bio: Optional[str] = None
    is_available: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    services: list[Service] = Relationship(back_populates="workers", link_model=WorkerService)

