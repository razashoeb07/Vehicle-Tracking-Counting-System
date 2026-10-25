from .connection import engine, Base
from .models import Video, VehicleEvent, VehicleCount, ProcessingJob


Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")