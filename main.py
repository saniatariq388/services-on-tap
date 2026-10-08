from fastapi import FastAPI 
from contextlib import asynccontextmanager
from src.db.seed import seed_services
from src.db.engine import create_tables
from src.routes.worker_routes import router as WorkerCreate
from fastapi.middleware.cors import CORSMiddleware
from src.utils.exception import Invalid_Service_Error_Handler, InvalidServiceError

# life span controller used as decorator, control your starting n ending controlller
@asynccontextmanager
async def lifespan(app: FastAPI):
     print("✅ server started")
     create_tables()
     seed_services()
     yield                          # yield server start ky bad print chaly ga n stop end sy pehly chaly ga
     print("❌ server stopped")



app = FastAPI(
    title= "Service On Click App Backend",
    description="This backend api of review for service on click app .",
    lifespan=lifespan
)

# cors allow
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # dev ke liye theek hai
    allow_methods=["*"],
    allow_headers=["*"],
)


# register error exception custom class
app.add_exception_handler(InvalidServiceError, Invalid_Service_Error_Handler)



# register route of ReviewCreate
app.include_router(WorkerCreate)

@app.get("/")
def hello():
    return {"message": " Hello, Welcome To Service On Click App!"}