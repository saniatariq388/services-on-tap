from typing import Optional

from sqlmodel import SQLModel


class WorkerItem(SQLModel):
    id: int
    worker_name: str
    phone: str
    area: str
    skills: Optional[list[str]] = None
    experience: Optional[int] = None
    bio: Optional[str] = None
    is_available: bool
    services: list[str]


class AllWorkersResponse(SQLModel):
    status: str = "success"
    status_code: int = 200
    message: str = "All workers fetched successfully"
    count: int = 0
    workers: list[WorkerItem] = []


class WorkerResponse(SQLModel):
    status: str = "success"
    worker_name: str
    phone: str
    area: str
    services: list[str]