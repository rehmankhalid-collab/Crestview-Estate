from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.content import get_content
from app.database import Base, engine, get_db
from app.email_utils import send_lead_notification
from app.models import Lead
from app.schemas import LeadCreate


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Crestview Estates", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
templates.env.filters["usd"] = lambda value: f"${value:,.0f}"


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        request, "index.html", {"content": get_content()}
    )


@app.post("/api/leads")
async def create_lead(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    payload = await request.json()
    try:
        lead_in = LeadCreate.model_validate(payload)
    except ValidationError as exc:
        errors = {err["loc"][0]: err["msg"] for err in exc.errors()}
        return JSONResponse(status_code=422, content={"success": False, "errors": errors})

    lead = Lead(name=lead_in.name, phone=lead_in.phone)
    db.add(lead)
    db.commit()
    db.refresh(lead)

    background_tasks.add_task(send_lead_notification, lead, get_settings())

    return {"success": True, "message": "Thank you — we'll be in touch shortly."}
