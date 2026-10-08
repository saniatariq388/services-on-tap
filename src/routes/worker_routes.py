from fastapi import APIRouter, Depends
import rich
from sqlmodel import Session, func, select
from src.models.model import Worker, Service, WorkerService
from src.db.engine import get_session
from src.validators.worker_create_validation import WorkerCreate
from src.utils.api_response import WorkerResponse
from utils.exception import InvalidServiceError



router = APIRouter(prefix="/services", tags=["/services"])
# tags is show on fastapi browser docs swagger optional h

#--------------------------------------

def get_service_ids(session: Session, names: list[str]) -> list[int]:
    ids = []
    for name in names:
        clean = " ".join(name.split()).title()      # "  tile   fitter " -> "Tile Fitter"

        service = session.exec(
            select(Service).where(func.lower(Service.service_name) == clean.lower())
        ).first()

        if not service:                              # nayi service, table mein add
            service = Service(service_name=clean)
            session.add(service)
            session.flush()                          # id mil jati hai

        if service.id not in ids:
            ids.append(service.id)
    return ids

#-------------------------------------------    
# GET /services  -> saari services
@router.get("/")
def get_services(session: Session = Depends(get_session)):
    return session.exec(select(Service)).all()

#----------------------------------------------

# POST("/workers") --> locathost:8000/services/workers
@router.post("/workers", response_model=WorkerResponse)
def create_worker(worker: WorkerCreate, session: Session = Depends(get_session)):
    # 1. phone pehle se registered to nahi
    exists = session.exec(select(Worker).where(Worker.phone == worker.phone)).first()
    if exists:
        raise InvalidServiceError(409, worker.services, "This Phone no is already registered", f"Worker with phone {worker.phone} already exists")

    # 2. WorkerCreate -> Worker table object (services Worker ka column nahi)
    db_worker = Worker(**worker.model_dump(exclude={"services"}))
    session.add(db_worker)
    session.flush()                                  # worker ki id mil gayi

    # 3. service names -> ids (nayi ho to table mein add)
    service_ids = get_service_ids(session, worker.services)

    # 4. link table mein rows
    for sid in service_ids:
        session.add(WorkerService(worker_id=db_worker.id, service_id=sid))

    session.commit()                                 # worker + services ek saath save
    session.refresh(db_worker)

    rich.print("Created Worker:", db_worker)
    return {"status": "success", "worker_name": db_worker.worker_name, "phone": db_worker.phone, "area": db_worker.area, "services": worker.services}



#-------------------------------------------    
# GET("/workers") --> locathost:8000/services/workers 
@router.get("/workers")
def get_all_workers(service_name: str | None = None, area: str | None = None, session: Session = Depends(get_session)):
     # Get all workers with optional filters for service_name and area

     query = select(Worker)
     all_workers = session.exec(query).all()
     rich.print("All Workers:", all_workers)
     # filter service 
     # service_obj = session.exec(
     #      select(Service).where(func.lower(Service.service_name) == service_name.lower())
     # ).first()
     # if not service_obj:
     #      raise InvalidServiceError(404, service_name,f"Service '{service_name}' not found")  
     return {"message": "Workers fetched successfully", "workers":all_workers }