from typing import Optional

from sqlmodel import SQLModel




class WorkerUpdate(SQLModel):
    worker_name: Optional[str] = None
    phone: Optional[str] = None
    area: Optional[str] = None
    services: Optional[list[str]] = None     # dropdown, bheji to poori list replace hogi
    skills: Optional[list[str]] = None
    experience: Optional[int] = None
    bio: Optional[str] = None
    is_available: Optional[bool] = None