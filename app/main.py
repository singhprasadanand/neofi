from fastapi import FastAPI
from fastapi.security import HTTPBearer
from app.utils.db_utils.database import Base, engine
from app.api.auth import auth_router
from app.api.events import events_router
import uvicorn


# Create all DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth_router,prefix='/api/auth',tags=['Authentication'])
app.include_router(events_router,prefix="/api/events", tags=["Events"])

bearer_scheme = HTTPBearer()

if __name__ == '__main__':
    uvicorn.run('main:app',reload=True)

