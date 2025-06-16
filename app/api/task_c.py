from fastapi import APIRouter
from app.services.task_c import do_task_c

router = APIRouter()

@router.get("/")
def do_task():
    return do_task_c()
