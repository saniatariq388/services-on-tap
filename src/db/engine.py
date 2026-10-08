from sqlmodel import SQLModel, create_engine, Session
from src.models.model import Worker, Service, WorkerService


database_url = "sqlite:///database.db"
engine = create_engine(database_url, echo=True)  # create engine for ORM  echo terminal pr query show karta h


# create table
def create_tables():
     
     SQLModel.metadata.create_all(engine)  # create table if not created or if exist it didnot recreate it by the help of metadata method



#open /close connection
def get_session():
     with Session(engine) as session:  #with connection ko open or close khud karta h session  query ko chalanay m help karta
          yield session




          