from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
import rich
from sqlmodel import Session, func, select
from src.routes.worker_routes import to_item
from src.db.engine import get_session
from src.models.model import Service
from src.utils.api_response import AllWorkersResponse, ServiceItem, ServicesResponse, WorkerItem, WorkerResponse
from src.utils.exception import InvalidServiceError
from src.validators.worker_create_validation import WorkerCreate
from src.validators.worker_update_validation import WorkerUpdate
from src.validators.service_create_validation import ServiceCreate






router = APIRouter(prefix="/services", tags=["/services"])


def to_service_item(s: Service) -> ServiceItem:
    return ServiceItem(
        id=s.id,
        service_name=s.service_name,
        is_active=s.is_active,
        total_workers=len(s.workers),
        workers=[w.worker_name for w in s.workers],
    )

#----------------------------------------------POST service



@router.post("/", response_model=ServicesResponse)
def create_service( service_data: ServiceCreate , session: Session =Depends(get_session)):
      name = " ".join(service_data.service_name.split()).title()

      # check if exist
      query = select(Service).where(func.lower(Service.service_name) == name.lower())

      exists = session.exec(query).first()
      if exists: 
            raise InvalidServiceError(error_status_code=409, service_name= name, reason= f'Service "{name}" is already exists')

      service = Service(service_name=name)
      session.add(service)
      session.commit()
      session.refresh(service)

      return ServicesResponse(
        status="success",
        message="Service Created Successfully",
        services=[to_service_item(service)],
    )



#-----------------------------------------------------GET all services for dropdown-----------------------------------------------------------

#  http://localhost:8000/services

# GET /services  -> saari services (app ke dropdown ke liye)
@router.get("/", response_model=ServicesResponse)
def get_all_services(session: Session = Depends(get_session)):

     
     services = session.exec(select(Service)).all()

     

     rich.print("all_services:", services)

     return ServicesResponse(status = "success", services = [to_service_item(s) for s in services])

#-----------------------------------------------------GET service by id-----------------------------------------------------------

#  http://localhost:8000/services/{id}

# GET /services/{id}  -> aik service (app ke dropdown ke liye)
@router.get("/{service_id}", response_model=ServicesResponse)
def get_service_by_id(service_id: int, session: Session = Depends(get_session)):

     service = session.get(Service, service_id)

     if not service:
          raise InvalidServiceError(error_status_code= 404, service_name= service, reason= f"Service {service} not found" )

     
     rich.print("all_services:", service)

     return ServicesResponse(status = "success", services = [to_service_item(service)])


#-----------------------------------------------------GET all worker of specific service-----------------------------------------------------------

#  http://localhost:8000/services/{id}/workers

# GET /services/{id}/workers  -> saray workers aik service ky (app ke dropdown ke liye)
# GET /services/{service_id}/workers -> aik service ke saray workers (poori detail)
@router.get("/{service_id}/workers", response_model=AllWorkersResponse)
def get_workers_of_service(service_id: int, session: Session = Depends(get_session)):

    service = session.get(Service, service_id)
    if not service:
        raise InvalidServiceError(404, str(service_id), f"Service {service_id} not found")

    # list comprehension
    # [ kya_banana  for  item  in  list ]
    #  to_item(w)      w         service.workers
    
    workers = [to_item(w) for w in service.workers]

    return AllWorkersResponse(
        status="success",
        message=f"Workers of {service.service_name} fetched successfully",
        count=len(workers),
        workers=workers,
    )



    #----------------------------------------------------------------

    # delete service by id

    # DELETE     http://localhost:8000/services/{id} 




#------------------------------------------------------------------- delete service 
@router.delete("/{service_id}", response_model=AllWorkersResponse)
def delete_service(service_id: int, session: Session = Depends(get_session)):


     # first check service exists

     service = session.get(Service, service_id)

     if not service:
          raise InvalidServiceError(error_status_code = 404, service_name = service, reason = "Invalid Service Name")

     # if service exists check any worker exists in this service
     if len(service.workers) > 0:
          raise InvalidServiceError(error_status_code = 409, service_name = service.service_name, reason = f"Service have {len(service.workers)} workers , so delete workers first.")

     # service worker ky table sy bhi count hosakhta h

#      count = session.exec(
#     select(func.count()).select_from(WorkerService).where(WorkerService.service_id == service_id)
# ).one()

# if count > 0:
#     raise InvalidServiceError(409, [], f"Service ke {count} workers hain, delete nahi ho sakti")

     session.delete(service)
     session.commit()

     return ServicesResponse(status = "success", services = service, message = "Service Deleted Successfully!")






