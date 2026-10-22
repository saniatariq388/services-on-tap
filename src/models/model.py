from typing import List, Optional
from datetime import datetime, timezone
from sqlmodel import Field, Relationship, SQLModel, Column, JSON


   
# table  structure/ model
  
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


Worker.model_rebuild()  # agar aik table ki entry m kuch update karna ho yeh func khud relation waly table m bhi update kar daita h






class Service(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    service_name: str = Field(index=True, unique=True)
    is_active: bool = Field(default=True)
    workers: list["Worker"] = Relationship(back_populates="services", link_model=WorkerService)


Service.model_rebuild()  # agar aik table ki entry m kuch update karna ho yeh func khud relation waly table m bhi update kar daita h

