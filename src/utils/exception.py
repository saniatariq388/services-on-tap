#pyton ki error class h exception


from fastapi import Request
from fastapi.responses import JSONResponse


class InvalidServiceError(Exception):

   def __init__(self, error_status_code: int, service_name: str, reason: str = "Invalid Service Name"):
        self.error_status_code = error_status_code
        self.service_name = service_name
        self.reason = reason  


async def Invalid_Service_Error_Handler(request : Request, exc: InvalidServiceError):
   return JSONResponse(
        status_code = exc.error_status_code,
        content = {
           "reason" : exc.reason, 
           "service_name": exc.service_name
        }
   )