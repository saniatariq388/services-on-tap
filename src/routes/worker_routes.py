from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
import rich
from sqlmodel import Session, func, select
from src.db.engine import get_session
from src.models.model import Service, Worker, WorkerService
from src.utils.api_response import AllWorkersResponse, WorkerItem, WorkerResponse
from src.utils.exception import InvalidServiceError
from src.validators.worker_create_validation import WorkerCreate
from src.validators.worker_update_validation import WorkerUpdate



router = APIRouter(prefix="/workers", tags=["/workers"])

#------------------------------------------------------------
# Worker (table object) -> WorkerItem (response), services ke NAAM ke saath


def to_item(w: Worker) -> WorkerItem:
    return WorkerItem(
        id=w.id,
        worker_name=w.worker_name,
        phone=w.phone,
        area=w.area,
        skills=w.skills,
        experience=w.experience,
        bio=w.bio,
        is_available=w.is_available,
        services=[s.service_name for s in w.services],
    )

#--------------------------------------------------------------------------POST register  worker


# http://localhost:8000/services/workers

# POST localhost:8000/workers  -> worker register

# POST /workers  -> worker register
@router.post("/", response_model=WorkerResponse)
def create_worker(worker: WorkerCreate, session: Session = Depends(get_session)):

    # 1. phone pehle se registered to nahi
    exists = session.exec(select(Worker).where(Worker.phone == worker.phone)).first()
    if exists:
        raise InvalidServiceError(409, worker.services, f"Worker with phone {worker.phone} already exists")

    # 2. naam saaf karo: extra spaces hatao, "Plumber" format, duplicate ek ho jayein
    clean = {}
    for n in worker.services:
        name = " ".join(n.split()).title()
        if name:
            clean[name.lower()] = name              # {"plumber": "Plumber"}

    if not clean:
        raise InvalidServiceError(422, worker.services, "Must include one service")

    # 3. jo services DB mein pehle se hain
    services = list(session.exec(
        select(Service).where(func.lower(Service.service_name).in_(list(clean.keys())))
    ).all())
    existing = {s.service_name.lower() for s in services}

    # 4. jo nahi hain, nayi bana do (loop ke andar add + append)
    for key, name in clean.items():
        if key not in existing:
            new_service = Service(service_name=name)
            session.add(new_service)
            services.append(new_service)

    # 5. worker banao (services ke baghair), phir services jodo
    db_worker = Worker(**worker.model_dump(exclude={"services"}))
    db_worker.services = services                   # workerservice rows khud banengi

    session.add(db_worker)
    session.commit()                                # worker + nayi services + links ek saath
    session.refresh(db_worker)

    rich.print("Worker created:", db_worker)

    return WorkerResponse(
        status="success",
        message="Worker created successfully",
        worker=[to_item(db_worker)],                # object nahi, WorkerItem
    )

#----------------------------------------------------------------GET  all workers with optional filters (service, area)------------------------------------------------------------

#    http://localhost:8000/services/workers?service=Plumber&area=gulberg

# GET /workers?service=Plumber&area=gulberg  -> search (dono optional)

@router.get("/", response_model=AllWorkersResponse)
def search_service_based_workers(
    service: Optional[str] = None,
    area: Optional[str] = None,
    session: Session = Depends(get_session),
):
    query = select(Worker).where(Worker.is_available == True)

    if service:                                           # service di ho tabhi join + filter
        query = (
            query
            .join(WorkerService, WorkerService.worker_id == Worker.id)
            .join(Service, Service.id == WorkerService.service_id)
            .where(func.lower(Service.service_name) == service.strip().lower())
        )

    if area:
        query = query.where(func.lower(Worker.area) == area.strip().lower())



    workers = session.exec(query).all()
    
    
    if not workers:
        raise InvalidServiceError(404, [service], "Workers not found with this service")


    items = [to_item(w) for w in workers]                 # wahi helper jo POST mein hai

    rich.print("Search results:", items)

    return AllWorkersResponse(count=len(items), workers=items)
#---------------------------------------------------------------------

# GET http://localhost:8000/workers/1  

# GET single worker by id
@router.get("/{worker_id}", response_model=WorkerItem)
def get_worker(
    worker_id: int,
    session: Session = Depends(get_session)):

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

@router.patch("/{worker_id}", response_model=WorkerResponse)
def update_worker(
    worker_id: int,
    update: WorkerUpdate,
    session: Session = Depends(get_session),
):
    # 1. worker dhoondo
    worker = session.get(Worker, worker_id)
    if not worker:
        raise InvalidServiceError(404, [], f"Worker with id {worker_id} not found")

    # 2. sirf wohi fields jo body mein bheji gayi
    data = update.model_dump(exclude_unset=True, exclude_none=True)
    services = data.pop("services", None)           # services alag handle hongi

    # 3. phone badla ho to duplicate check
    new_phone = data.get("phone")
    if new_phone and new_phone != worker.phone:
        taken = session.exec(select(Worker).where(Worker.phone == new_phone)).first()
        if taken:
            raise InvalidServiceError(409, [], f"Worker with phone {new_phone} already exists")

    # 4. services bheji gayi hon to replace (nayi ho to bana do)
    if services is not None:
        if not services:
            raise InvalidServiceError(422, [], "Atleast one service")

        clean = {}
        for n in services:
            name = " ".join(n.split()).title()      # "  tile   work " -> "Tile Work"
            if name:
                clean[name.lower()] = name

        service_objs = list(session.exec(
            select(Service).where(func.lower(Service.service_name).in_(list(clean.keys())))
        ).all())
        existing = {s.service_name.lower() for s in service_objs}

        for key, name in clean.items():
            if key not in existing:                 # table mein nahi, nayi bana do
                new_service = Service(service_name=name)
                session.add(new_service)
                service_objs.append(new_service)

        worker.services = service_objs              # purani links hat, nayi ban jayengi

    # 5. baqi fields (name, area, bio, skills, experience, is_available, phone)
    for field, value in data.items():
        setattr(worker, field, value)

    worker.updated_at = datetime.now(timezone.utc)

    # 6. save
    session.add(worker)
    session.commit()
    session.refresh(worker)

    return WorkerResponse(
        status="success",
        message="Worker updated successfully",
        worker=[to_item(worker)],
    )


@router.delete("/{worker_id}" , response_model=WorkerResponse)
async def delete_worker(
       worker_id: int,
       session: Session = Depends(get_session),
    ):


    worker = session.get(Worker, worker_id)

    if not worker:
        raise InvalidServiceError(error_status_code=404, reason= "Worker not found")


    session.delete(worker)
    session.commit()
    
    return WorkerResponse(status= "success", message= " worker deleted", worker = [])