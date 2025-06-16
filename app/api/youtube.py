from fastapi import APIRouter, Query
from app.services.youtube_crawler import crawl_youtube_channel

router = APIRouter()

@router.get("/crawl")
def crawl(channel: str = Query(..., description="유튜브 채널명")):
    result = crawl_youtube_channel(channel)
    return result
