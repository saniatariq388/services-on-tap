from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
import rich
from sqlmodel import Session, func, select

from src.db.engine import get_session
from src.models.model import Service, ServiceName, Worker, WorkerService
from src.utils.api_response import AllWorkersResponse, WorkerItem, WorkerResponse
from src.utils.exception import InvalidServiceError
from src.validators.worker_create_validation import WorkerCreate

router = APIRouter(prefix="/services", tags=["/services"])



#-----------------------------------------------------GET all services for dropdown-----------------------------------------------------------

#  http://localhost:8000/services

# GET /services  -> saari services (app ke dropdown ke liye)
@router.get("/", response_model=list[ServiceName])
def get_services(session: Session = Depends(get_session)):
     services = session.exec(select(Service)).all()

     
     all_services = [ServiceName(s.service_name) for s in services]

     rich.print("all_services:", all_services)

     return all_services






#--------------------------------------------------------------------------POST register  worker


# http://localhost:8000/services/workers

# POST /services/workers  -> worker register
@router.post("/workers", response_model=WorkerResponse)
def create_worker(worker: WorkerCreate, session: Session = Depends(get_session)):
    # 1. phone pehle se registered to nahi
    exists = session.exec(select(Worker).where(Worker.phone == worker.phone)).first()
    if exists:
        raise InvalidServiceError(409, worker.services, f"Worker with phone {worker.phone} already exists")

    # 2. dropdown ke naam -> Service objects
    names = {s.value for s in worker.services}
    services = session.exec(select(Service).where(Service.service_name.in_(names))).all()
    if len(services) != len(names):
        missing = names - {s.service_name for s in services}
        raise HTTPException(422, f"Service not found: {', '.join(sorted(missing))}")

    # 3. worker banao, services jodo (workerservice rows khud banengi)
    db_worker = Worker(**worker.model_dump(exclude={"services"}))
    db_worker.services = list(services)

    session.add(db_worker)
    session.commit()
    session.refresh(db_worker)

    rich.print("Worker created:", db_worker)

    return WorkerResponse(
        status="success",
        worker_name=db_worker.worker_name,
        phone=db_worker.phone,
        area=db_worker.area,
        services=[s.service_name for s in db_worker.services],
    )




#----------------------------------------------------------------GET  all workers with optional filters (service, area)------------------------------------------------------------

#    http://localhost:8000/services/workers?service=Plumber&area=gulberg

# GET /services/workers?service=Plumber&area=gulberg  -> search (dono optional)
@router.get("/workers", response_model=AllWorkersResponse)
def search_service_based_workers(
    service: Optional[ServiceName] = None,
    area: Optional[str] = None,
    session: Session = Depends(get_session),
 ):
    query = select(Worker).where(Worker.is_available == True)    # hamesha lagega

    if service:                                                   # service di ho tabhi join + filter
        query = (
            query
            .join(WorkerService, WorkerService.worker_id == Worker.id)
            .join(Service, Service.id == WorkerService.service_id)
            .where(Service.service_name == service.value)
        )

    if area:
        query = query.where(func.lower(Worker.area) == area.strip().lower())

    workers = session.exec(query).all()

    items = [
        {
            "id": w.id,
            "worker_name": w.worker_name,
            "phone": w.phone,
            "area": w.area,
            "skills": w.skills,
            "experience": w.experience,
            "bio": w.bio,
            "is_available": w.is_available,
            "services": [s.service_name for s in w.services],
        }
        for w in workers
    ]

    rich.print("Search results:", items)

    return AllWorkersResponse(count=len(workers), workers=items)

#---------------------------------------------------------------------

# GET http://localhost:8000/services/workers/1  

# GET single worker by id
@router.get("/workers/{worker_id}", response_model=WorkerItem)
def get_worker(worker_id: int, session: Session = Depends(get_session)):
    worker = session.get(Worker, worker_id)
    if not worker:
        raise InvalidServiceError(404, [], f"Worker with id {worker_id} not found")

    return WorkerItem(
        id=worker.id,
        worker_name=worker.worker_name,
        phone=worker.phone,
        area=worker.area,
        skills=worker.skills,
        experience=worker.experience,
        bio=worker.bio,
        is_available=worker.is_available,
        services=[s.service_name for s in worker.services],
    )




#---------------------------------------------------patch worker service

#   http://localhost:8000/services/workers/1/services

# PATCH /services/workers/1/services  -> update worker services


@router.patch("/workers/{worker_id}", response_model=WorkerResponse)
def update_worker(
    worker_id: int,
    update: WorkerUpdate,
    session: Session = Depends(get_session),
):
    worker = session.get(Worker, worker_id)
    if not worker:
        raise InvalidServiceError(404, [], f"Worker with id {worker_id} not found")

    # sirf wohi fields jo body mein bheji gayi
    data = update.model_dump(exclude_unset=True, exclude_none=True)
    services = data.pop("services", None)        # services alag handle hongi

    # phone badla ho to duplicate check
    new_phone = data.get("phone")
    if new_phone and new_phone != worker.phone:
        taken = session.exec(select(Worker).where(Worker.phone == new_phone)).first()
        if taken:
            raise InvalidServiceError(409, [], f"Worker with phone {new_phone} already exists")

    # services bheji gayi hon to replace
    if services is not None:
        if not services:
            raise InvalidServiceError(422, [], "Kam az kam ek service zaroori hai")
        names = {s.value for s in services}
        service_objs = session.exec(select(Service).where(Service.service_name.in_(names))).all()
        if len(service_objs) != len(names):
            missing = names - {s.service_name for s in service_objs}
            raise InvalidServiceError(422, [], f"Service not found: {', '.join(sorted(missing))}")
        worker.services = list(service_objs)

    # baqi fields
    for field, value in data.items():
        setattr(worker, field, value)

    worker.updated_at = datetime.now(timezone.utc)

    session.add(worker)
    session.commit()
    session.refresh(worker)

    return WorkerResponse(
        status="success",
        worker_name=worker.worker_name,
        phone=worker.phone,
        area=worker.area,
        services=[s.service_name for s in worker.services],
    )
