from fastapi import FastAPI
from app.api import site_a, site_b, task_c, sample, health

app = FastAPI()

app.include_router(site_a.router, prefix="/site-a")
app.include_router(site_b.router, prefix="/site-b")
app.include_router(task_c.router, prefix="/task-c")
app.include_router(sample.router, prefix="/sample")
app.include_router(health.router)
