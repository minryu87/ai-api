from fastapi import FastAPI
from app.api import site_a, site_b, task_c, sample, health, youtube_videos, youtube_comments, airtable, creator_advisor, naver_creator_advisor, postgres_thread_processor

app = FastAPI()

app.include_router(site_a.router, prefix="/site-a")
app.include_router(site_b.router, prefix="/site-b")
app.include_router(task_c.router, prefix="/task-c")
app.include_router(sample.router, prefix="/sample")
app.include_router(health.router)

app.include_router(youtube_videos.router, prefix="/youtube")
app.include_router(youtube_comments.router, prefix="/youtube")

app.include_router(airtable.router, prefix="/api/v1/airtable", tags=["Airtable"])
app.include_router(creator_advisor.router, prefix="/api/v1/creator-advisor", tags=["Creator Advisor"])
app.include_router(naver_creator_advisor.router, prefix="/api/v1/naver-creator-advisor", tags=["Naver Creator Advisor Crawler"])
app.include_router(postgres_thread_processor.router, prefix="/api/v1/postgres", tags=["Postgres Processor"])
