from typing import List

from sqlmodel import SQLModel




class WorkerResponse(SQLModel):
    status: str = "success"
    worker_name: str
    phone: str
    area: str
    services: list[str]





#  worker_name: str
#     skills: Optional[str] 
#     phone: str 
#     experience: int
#     area: str
#     services: list[str] = Field(min_length=1)
#     bio: Optional[str] = None
#     is_available: bool = True
