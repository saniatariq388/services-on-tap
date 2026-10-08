from sqlmodel import Session, select
from src.db.engine import engine
from src.models.model import Service, ServiceName


def seed_services():
    with Session(engine) as session:
        existing = set(session.exec(select(Service.service_name)).all())
        for s in ServiceName:
            if s.value not in existing:
                session.add(Service(service_name=s.value))
        session.commit()




# existing = {Plumber, Electrician, Painter, Carpenter, AC Technician, Mason}

# Plumber      → pehle se hai, chhor do
# ...
# Tile Fitter  → table mein nahi, ADD

# enum m service add karty hi  server start pr update kr dy ga




