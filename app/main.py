import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import BackgroundTasks, Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.content import get_content
from app.database import Base, engine, get_db
from app.email_utils import send_lead_notification
from app.models import Lead
from app.schemas import LeadCreate

# Absolute, not relative: a serverless host (e.g. Vercel) can run this
# with a working directory that isn't the project root, which would
# otherwise break StaticFiles/Jinja2Templates lookups.
BASE_DIR = Path(__file__).resolve().parent.parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError:
        # Read-only filesystem (e.g. DATABASE_URL still pointing at a
        # non-writable path in production) — log and keep serving pages;
        # /api/leads will surface the real error on the next write.
        logging.getLogger("crestview").exception(
            "Could not create database tables; check DATABASE_URL."
        )
    yield


app = FastAPI(title="Crestview Estates", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
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
